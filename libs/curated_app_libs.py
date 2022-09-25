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


def get_curation_cmd(test_config_dict):
    workload_image = test_config_dict["docker_image"]
    debug_mode = " debug " if test_config_dict.get("debug_mode") == 'y' else ''
    if test_config_dict.get("test_option"):
        curation_cmd = 'python3 curate.py ' + workload_image + debug_mode + ' test' + ' < input.txt'
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
    elif "Provide the Distro of your base image" in output:
        return "distro_page"
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
    try:
        process = subprocess.Popen(curation_cmd, shell=True, stdout=subprocess.PIPE, encoding="utf-8")
        print("Process started ", curation_cmd)
        os.chdir(FRAMEWORK_PATH)
        screen_name = "home_page"
        while True:
            output = process.stdout.readline()
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
    finally:
        process.stdout.close()
        utils.kill(process.pid)
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
            if "<verifier-dns-name:port>" in line:
                line = line.replace("<verifier-dns-name:port>", "localhost:4433")
            if "-it" in line:
                line = line.replace("-it", "-t")
            if "$ docker run" in line:
                line = line.replace("$ docker run", "docker run")
            output.append(line)
    print("Get Docker Run Command is ", output)
    return output

def get_workload_result(test_config_dict):
    if "workload_result" in test_config_dict.keys():
        workload_result = [test_config_dict["workload_result"]]
    elif "bash" in test_config_dict["docker_image"]:
        workload_result = ["total        used        free      shared  buff/cache   available"]
    elif "redis" in test_config_dict["docker_image"]:
        workload_result = ["Ready to accept connections"]
    elif "pytorch" in test_config_dict["docker_image"]:
        workload_result = ["Done. The result was written to `result.txt`."]
    return workload_result

def expected_msg_verification(test_config_dict, curation_output):
    result = False
    if "expected_output_infile" in test_config_dict.keys():
        base_image_name = test_config_dict.get("docker_image").split(' ', maxsplit=1)[1]
        base_image_type = test_config_dict.get("docker_image").split(' ', maxsplit=1)[0]
        log_file_name, n = re.subn('[:/]', '_', base_image_name)
        log_file = f'{base_image_type}/{log_file_name}.log'
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
    return None

def verify_process(process, workload_result, verifier_process=None):
    result = False
    while True:
        nextline = process.stdout.readline()
        print(nextline.strip())
        if nextline == '' and process.poll() is not None:
            break
        if all(x in nextline for x in workload_result):
            process.stdout.close()
            if verifier_process:
                utils.kill(verifier_process.pid)
            utils.kill(process.pid)
            sys.stdout.flush()
            result = True
            break
    return result

def run_verifier_process(test_config_dict, verifier_cmd):
    error_msg = test_config_dict.get("verifier_error")
    if error_msg:
        verifier_cmd = verifier_cmd.replace("pytorch/base_image_helper", "test_config")

    verifier_process = utils.popen_subprocess(verifier_cmd)
    time.sleep(20)
    if error_msg:
        return verify_process(verifier_process, [error_msg])
    return verifier_process

def run_curated_image(test_config_dict, curation_output):
    verifier_process = None
    unsigned_image = False
    attestation = True if test_config_dict["attestation"] in ["test", "done"] else False
    workload_result = get_workload_result(test_config_dict)

    docker_command = get_docker_run_command(test_config_dict, curation_output)
    gsc_docker_command = docker_command[-1]
    if attestation and (test_config_dict.get("verifier_run") == None):
        if test_config_dict.get('test_option') != None:
            verifier_process = run_verifier_process(test_config_dict, docker_command[0])
            if type(verifier_process) == bool:
                return verifier_process

    process = utils.popen_subprocess(gsc_docker_command)
    return verify_process(process, workload_result, verifier_process)

def verify_run(curation_output):
    if re.search("The curated GSC image gsc-(.*) is ready", curation_output) or \
            re.search("docker run", curation_output):
        return True
    return False

def run_test(test_instance, test_yaml_file):
    result = False
    test_name = inspect.stack()[1].function
    print(f"\n********** Executing {test_name} **********\n")
    test_config_dict = config_parser.read_config_yaml(test_yaml_file, test_name)
    utils.test_setup(test_config_dict)
    try:
        workload_name = utils.get_workload_name(test_config_dict['docker_image'])
        curation_output = generate_curated_image(test_config_dict)
        result = expected_msg_verification(test_config_dict, curation_output)
        if result == None:
            if verify_run(curation_output):
                result = run_curated_image(test_config_dict, curation_output)
                if "redis" in test_name:
                    result = workload.run_redis_client()
    finally:
        print("Docker images cleanup")
        utils.cleanup_after_test(workload_name, test_name)
    return result

