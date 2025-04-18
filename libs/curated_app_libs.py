import inspect
import subprocess
import sys
import os
from data.constants import *
from libs import config_parser
from libs import utils
from libs import workload
import time
import re
from queue import Empty

def get_curation_cmd(test_config_dict):
    workload_image = test_config_dict["docker_image"]
    debug_mode = ''
    if test_config_dict.get("debug_mode") == 'y':
        debug_mode = " -b debug "
    elif test_config_dict.get("debugoptimized_mode") == 'y':
        debug_mode = " -b debugoptimized "
    if test_config_dict.get("test_option"):
        curation_cmd = 'python3 curate.py ' + workload_image + debug_mode + ' -t'
    else:
        curation_cmd = 'python3 curate.py ' + workload_image + debug_mode + ' < input.txt'
    return curation_cmd

def write_to_log_file(tc_dict, output):
    fd = open(os.path.join(FRAMEWORK_PATH, tc_dict['log_file']), "w")
    fd.write(output)
    fd.close()

def screen_verification(output):
    if "This application will provide step-by-step guidance" in output:
        return "home_page"
    elif "Please provide path to your enclave signing key" in output:
        return "signing_page"
    elif "Please enter the passphrase for the signing key" in output:
        return "signing_key_password"
    elif "To enable remote attestation using Azure DCAP client" in output:
        return "attestation_page"
    elif "Building the RA-TLS Verifier image" in output:
        return "verifier_page"
    elif "Specify docker command-line arguments here in a single" in output:
        return "runtime_page"
    elif "Specify docker run flags here in a single string" in output:
        return "flags_page"
    elif "Please specify a list of env variables" in output:
        return "environment_page"
    elif "Encrypted files in the base image used by the" in output:
        return "encrypted_page"
    elif "Please provide the path to the key used for" in output:
        return "encryption_key_page"
    elif re.search("The curated GSC image gsc-(.*) is ready", output):
        return "final_page"

def test_should_break(screen_name, expected_screen):
    pos = SCREEN_LIST.index(screen_name)
    if expected_screen not in SCREEN_LIST[pos:]:
        return True

def generate_curated_image(test_config_dict):
    curation_output = ''

    curation_cmd = get_curation_cmd(test_config_dict)
    end_test = test_config_dict.get('expected_output_console')
    os.chdir(CURATED_APPS_PATH)
    timeout = time.time() + 1800
    try:
        process = subprocess.Popen(curation_cmd, shell=True, stdout=subprocess.PIPE, encoding="utf-8")
        print(f"Process started : {curation_cmd}, process.pid {process.pid}")
        os.chdir(FRAMEWORK_PATH)
        screen_name = "home_page"

        queue, thread = utils.monitor_thread(process.stdout)
        while True:
            try:
                output = queue.get_nowait()
            except Empty:
                output = ""

            if process.poll() is not None and output == '':
                break

            if output:
                curation_output += output
                value = screen_verification(output)
                if value: screen_name = value
                if 'expected_output_console' in test_config_dict.keys():
                    should_break = test_should_break(screen_name, test_config_dict.get('expected_screen'))
                    if end_test in output or should_break:
                        break
            if time.time() > timeout:
                print("Timeout exceeded for workload")
                break
    except Exception as e:
        pass
    finally:
        queue.task_done()
        thread.join(5)
        utils.terminate_process(process)
    write_to_log_file(test_config_dict, curation_output)
    return curation_output

def get_docker_run_command(test_config_dict, curation_output):
    output = []
    if test_config_dict.get('test_option') is None:
        log_contents = utils.read_file(COMMANDS_TXT_PATH)
    else:
        log_contents = curation_output
    log_contents = log_contents.split("\n")
    for line in log_contents:
        if "docker run" in line:
            if "--net=host" not in line:
                line = line.replace("docker run", "docker run --net=host")
            if "--device=/dev/sgx/enclave" in line:
                line = line.replace("--device=/dev/sgx/enclave","--device=/dev/sgx_enclave")
            if "RA_TLS_MRENCLAVE" in line and "RA_TLS_ALLOW_OUTDATED_TCB_INSECURE" not in line:
                line = line.replace("-e RA_TLS_MRENCLAVE",
                        "-e RA_TLS_ALLOW_OUTDATED_TCB_INSECURE=1 -e RA_TLS_MRENCLAVE")
            if "<verifier-dns-name:port>" in line:
                line = line.replace("<verifier-dns-name:port>", "localhost:4433")
            if "-it" in line:
                line = line.replace("-it", "-t")
            if "$ docker run" in line:
                line = line.replace("$ docker run", "docker run")
            output.append(line)
    return output

def get_workload_result(test_config_dict):
    d_image = test_config_dict["docker_image"]
    if "workload_result" in test_config_dict.keys():
        workload_result = [test_config_dict["workload_result"]]
    elif "bash" in d_image:
        workload_result = ["total        used        free      shared  buff/cache   available"]
    elif "redis" in d_image:
        workload_result = ["Ready to accept connections"]
    elif "pytorch" in d_image:
        workload_result = ["Done. The result was written to `result.txt`."]
    elif "sklearn" in d_image:
        workload_result = ["Kmeans perf evaluation finished"]
    elif "tensorflow-serving" in d_image:
        workload_result = ["Running gRPC ModelServer at 0.0.0.0:8500"]
    elif "mysql" in d_image:
        workload_result = ["/usr/sbin/mysqld: ready for connections"]
    elif "mariadb" in d_image:
        workload_result = ["mariadbd: ready for connections"]
    elif "memcached" in d_image:
        if test_config_dict.get("debug_mode") == "y":
            time.sleep(180)
        else:
            time.sleep(30)
        out = utils.run_subprocess("sudo lsof -i:11211 | grep LISTEN")
        if out:
            workload_result = ""
    elif "openvino-model-server" in d_image:
        workload_result = ["ServableManagerModule started"]
    return workload_result

def expected_msg_verification(test_config_dict, curation_output):
    result = False
    if "expected_output_infile" in test_config_dict.keys():
        log_file = test_config_dict["curation_log"]
        with open(os.path.join(CURATED_APPS_PATH, log_file), "r") as log_file_pointer:
            for line in log_file_pointer.readlines():
                print(line)
                if test_config_dict.get("expected_output_infile") in line:
                    result = True
            return result

    if "expected_output_console" in test_config_dict.keys():
        if re.search(test_config_dict["expected_output_console"], curation_output):
            result = True
        return result

    if "flag_validation" in test_config_dict.keys():
        docker_commands = get_docker_run_command(test_config_dict, curation_output)
        for cmd in docker_commands:
            if test_config_dict["flag_validation"] in cmd:
                print(cmd)
                result = True
        return result
    return None

def verify_process(test_config_dict, process=None, verifier_process=None):
    result = False
    debug_log = None
    if verifier_process and test_config_dict.get("verifier_error"):
        workload_result = test_config_dict.get("verifier_error")
        process = verifier_process
        verifier_process = None
    else:
        workload_result = get_workload_result(test_config_dict)

    # Redirecting the debug mode logs to file instead of console because
    # it consumes whole lot of console and makes difficult to debug
    if test_config_dict.get("debug_mode") == "y":
        debug_log_file = test_config_dict["log_file"].replace(".log", "_console.log")
        debug_log = open(debug_log_file, "w+")

    queue, thread = utils.monitor_thread(process.stdout)
    timeout = time.time() + 1800
    try:
        while True:
            try:
                nextline = queue.get_nowait()
            except Empty:
                nextline = ""

            if process.poll() is not None and nextline == "":
                break

            if nextline:
                if debug_log:
                    debug_log.write(nextline)
                else:
                    print(nextline.strip())

                if all(x in nextline for x in workload_result):
                    if verifier_process:
                        utils.terminate_process(verifier_process)
                    sys.stdout.flush()
                    result = True
                    break

            if time.time() > timeout:
                print("Timeout exceeded for workload")
                break
    except Exception as e:
        pass
    finally:
        queue.task_done()
        thread.join(5)
        utils.terminate_process(process)

    if debug_log: debug_log.close()
    if verifier_process:
        try:
            container_name = utils.run_subprocess("docker ps -a | grep verifier:latest | awk '{print $NF}'")
            container_output = utils.run_subprocess(f"docker logs {container_name}")
            with open(test_config_dict["log_file"].replace(".log", "_verifier_console.log"), "w+") as file:
                file.write(f"Docker Verifier logs\n: {container_output}\n")
        except Exception as e:
            print("Failed to write verifier console log")
    return result

def run_verifier_process(test_config_dict, verifier_cmd):
    error_msg = test_config_dict.get("verifier_error")
    if error_msg:
        verifier_cmd = verifier_cmd.replace("pytorch/base_image_helper", "test_config")

    verifier_process = utils.popen_subprocess(verifier_cmd)
    time.sleep(20)
    if error_msg:
        return verify_process(test_config_dict, verifier_process=verifier_process)
    return verifier_process

def run_curated_image(test_config_dict, curation_output):
    verifier_process = None
    unsigned_image = False
    attestation = True if test_config_dict["attestation"] in ["test", "done"] else False

    docker_command = get_docker_run_command(test_config_dict, curation_output)
    gsc_docker_command = docker_command[-1]
    if attestation and (test_config_dict.get("verifier_run") == None):
        if test_config_dict.get('test_option') != 'y':
            verifier_process = run_verifier_process(test_config_dict, docker_command[0])
            if type(verifier_process) == bool:
                return verifier_process
    process = utils.popen_subprocess(gsc_docker_command)
    return verify_process(test_config_dict, process, verifier_process)

def verify_run(curation_output):
    if re.search("The curated GSC image gsc-(.*)ready", curation_output, re.DOTALL) or \
        "docker run --net=host" in curation_output:
        return True
    return False

def run_workload_client(test_config_dict):
    out = True
    d_image = test_config_dict["docker_image"]
    if "redis" in d_image or "memcached" in d_image:
        wk_name = utils.get_workload_name(d_image)
        out = workload.run_memtier_benchmark(wk_name)
    elif "tensorflow-serving" in d_image:
        out = workload.run_tensorflow_serving_client(test_config_dict)
    elif "mysql" in d_image or "mariadb" in d_image:
        out = workload.run_mysql_client(d_image)
    elif "openvino-model-server" in d_image:
        out = workload.run_ovms_client()
    return out

def run_test(test_instance, test_yaml_file):
    result = False
    test_name = inspect.stack()[1].function
    print(f"\n********** Executing {test_name} **********\n")
    test_config_dict = config_parser.read_config_yaml(test_yaml_file, test_name)
    utils.test_setup(test_config_dict)
    try:
        curation_output = generate_curated_image(test_config_dict)
        result = expected_msg_verification(test_config_dict, curation_output)
        if result == None and verify_run(curation_output):
            result = run_curated_image(test_config_dict, curation_output)
            time.sleep(3)
            if result:
                result = run_workload_client(test_config_dict)
    finally:
        if "_latest_" in test_name:
            version_update = utils.check_app_version(test_config_dict)
            if result == None: result = False
            result = result & version_update
        print("Docker images cleanup")
        utils.cleanup_after_test(test_config_dict)
    return result

