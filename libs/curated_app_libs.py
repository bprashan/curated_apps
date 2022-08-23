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
    if test_config_dict.get("test_option"):
        curation_cmd = 'sudo python3 curate.py ' + workload_image + ' test < input.txt'
    else:
        curation_cmd = 'sudo python3 curate.py ' + workload_image + ' < input.txt'
    return curation_cmd

def write_to_log_file(tc_dict, output):
    fd = open(os.path.join(FRAMEWORK_PATH, tc_dict['log_file']), "w")
    fd.write(output)
    fd.close()

def screen_verification(output):
    if "This application will provide step-by-step guidance" in output:
        return "home_page"
    elif "Please provide path to your signing key in the blue box" in output:
        return "signing_page"
    elif "To enable remote attestation using Azure DCAP client" in output:
        return "attestation_page"
    elif "Building the RA-TLS Verifier image" in output:
        return "verifier_page"
    elif "Specify docker run-time arguments here" in output:
        return "runtime_page"
    elif "Please specify a list of env variables" in output:
        return "environment_page"
    elif "If the base image contain encrypted data, please provide" in output:
        return "encrypted_page"
    elif "Image Creation:" in output:
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
                    should_break = test_should_break(screen_name, test_config_dict['expected_screen'])
                    if end_test in output or should_break:
                        break
    finally:
        process.stdout.close()
        utils.kill(process.pid)
    write_to_log_file(test_config_dict, curation_output)
    return curation_output

def get_docker_run_command(attestation, workload_name):
    output = []
    wrapper_image = "gsc-{}".format(workload_name)
    if attestation == 'y':
        verifier_cmd  = "docker run --rm --net=host -e RA_TLS_ALLOW_DEBUG_ENCLAVE_INSECURE=1 -e RA_TLS_ALLOW_OUTDATED_TCB_INSECURE=1 --device=/dev/sgx/enclave  -t verifier_image:latest"
        gsc_workload = "docker run --rm --net=host --device=/dev/sgx/enclave -e SECRET_PROVISION_SERVERS=\"localhost:4433\" \
            -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -t {}".format(wrapper_image)
        output.append(verifier_cmd)
    else:
        gsc_workload = "docker run --rm --net=host --device=/dev/sgx/enclave -t {}".format(wrapper_image)
    output.append(gsc_workload)
    return output

def get_workload_result(workload_name):
    pytorch_result = ["Result", "Labrador retriever", "golden retriever", "Saluki, gazelle hound", "whippet", "Ibizan hound, Ibizan Podenco"]
    bash_result = ["total        used        free      shared  buff/cache   available"]
    redis_result = ["Ready to accept connections"]
    if "bash" in workload_name:
        workload_result = bash_result
    elif "redis" in workload_name:
        workload_result = redis_result
    elif "pytorch" in workload_name:
        workload_result = pytorch_result
    return workload_result

def expected_msg_verification(test_config_dict, curation_output):
    result = False
    if "expected_output_infile" in test_config_dict.keys():
        with open(os.path.join(CURATED_APPS_PATH, test_config_dict.get("docker_image")+".log"), "r") as logfile:
            for line in logfile.readlines():
                print(line)
                if test_config_dict.get("expected_output_infile") in line:
                    result = True
            return result

    if "expected_output_console" in test_config_dict.keys():
        if test_config_dict.get("expected_output_console") in curation_output:
            result = True
        return result
    return None

def run_curated_image(docker_command, workload_name, attestation=None):
    result = False
    workload_result = get_workload_result(workload_name)
    gsc_docker_command = docker_command[-1]
    if attestation == 'y':
        verifier_process = utils.popen_subprocess(docker_command[0])
        time.sleep(5)

    process = utils.popen_subprocess(gsc_docker_command)
    while True:
        nextline = process.stdout.readline()
        print(nextline.strip())
        if nextline == '' and process.poll() is not None:
            break
        if  all(x in nextline for x in workload_result):
            process.stdout.close()
            if attestation == 'y': utils.kill(verifier_process.pid)
            utils.kill(process.pid)
            sys.stdout.flush()
            result = True
            break
    return result

def verify_run(curation_output):
    if re.search("docker run(.*)--device=/dev/sgx(.)enclave", curation_output):
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
                docker_run = get_docker_run_command(test_config_dict['attestation'], workload_name)
                result = run_curated_image(docker_run, workload_name, test_config_dict['attestation'])
                if "redis" in test_name:
                    result = workload.run_redis_client()
    finally:
        print("Docker images cleanup")
        utils.cleanup_after_test(workload_name)
    return result

