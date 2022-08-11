import inspect
import subprocess
import sys
import os
from torchvision import models
import torch
from data.constants import *
from libs import config_parser
from libs import utils
import time

def generate_encrypted_files(path, filename):
    output_path = os.path.join(path, "encrypted", "alexnet-pretrained.pt")
    encrypt_cmd = "gramine-sgx-pf-crypt encrypt -w wrap-key -i {} -o {}".format(filename, output_path)
    utils.run_subprocess(encrypt_cmd, path)

def generate_local_image(workload_image, encryption=None):
    if "redis" in workload_image:
        os.system("docker pull redis:latest")
    elif "pytorch" in workload_image:
        output_filename = CURATED_APPS_PATH + "/pytorch/pytorch_with_plain_text_files/plaintext/alexnet-pretrained.pt"
        alexnet = models.alexnet(pretrained=True)
        torch.save(alexnet, output_filename)
        print("Pre-trained model was saved in \"%s\"" % output_filename)

        if encryption == "y":
            docker_path = CURATED_APPS_PATH + "/pytorch/pytorch_with_encrypted_files"
            docker_build_cmd = "docker build -t pytorch_encrypted ."
            generate_encrypted_files(docker_path, output_filename)
        else:
            docker_path = CURATED_APPS_PATH + "/pytorch/pytorch_with_plain_text_files"
            docker_build_cmd = "docker build -t pytorch_plain ."

        output = utils.run_subprocess(docker_build_cmd, docker_path)
        print(output)

def generate_curated_image(test_config_dict, run_with_test_option):
    curation_output = ''
    workload_image = test_config_dict["docker_image"]

    if test_config_dict.get("create_local_image") == "y":
        generate_local_image(workload_image, test_config_dict.get("encrypted_files"))

    if run_with_test_option:
        curation_cmd = 'python3 curation_app.py ' + workload_image + ' test'
    else:
        curation_cmd = 'python3 curation_app.py ' + workload_image + ' < input.txt'
    print("Curation cmd ", curation_cmd)
    process = utils.popen_subprocess(curation_cmd, CURATED_APPS_PATH)

    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == '':
            break
        if output:
            print(output.strip())
            curation_output += output
            # if "docker run" in output:
            #     curation_output = True
            #     break
    return curation_output

def get_docker_run_command(attestation, workload_name):
    output = []
    wrapper_image = "gsc-{}x".format(workload_name)
    if attestation == 'y':
        verifier_cmd  = "docker run  --net=host  --device=/dev/sgx/enclave  -t verifier_image:latest"
        gsc_workload = "docker run --net=host --device=/dev/sgx/enclave -e SECRET_PROVISION_SERVERS=\"localhost:4433\" \
            -v /var/run/aesmd/aesm.socket:/var/run/aesmd/aesm.socket -t {}".format(wrapper_image)
        output.append(verifier_cmd)
    else:
        gsc_workload = "docker run  --device=/dev/sgx/enclave -t {}".format(wrapper_image)
    output.append(gsc_workload)
    return output

def run_curated_image(docker_command, attestation=None):
    result = False
    pytorch_result = ["Result", "Labrador retriever", "golden retriever", "Saluki, gazelle hound", "whippet", "Ibizan hound, Ibizan Podenco"]
    gsc_docker_command = docker_command[-1]
    if attestation == 'y':
        verifier_process = utils.popen_subprocess(docker_command[0])
        time.sleep(10)

    process = utils.popen_subprocess(gsc_docker_command)
    while True:
        nextline = process.stdout.readline()
        print(nextline.strip())
        if nextline == '' and process.poll() is not None:
            break
        if "Ready to accept connections" in nextline or all(x in nextline for x in pytorch_result):
            process.stdout.close()
            if attestation == 'y': utils.kill(verifier_process.pid)
            utils.kill(process.pid)
            sys.stdout.flush()
            result = True
            break
    return result

def run_test(test_instance, test_yaml_file):
    run_with_test_option = False
    result = False
    test_name = inspect.stack()[1].function
    print(f"\n********** Executing {test_name} **********\n")
    test_config_dict = config_parser.read_config_yaml(test_yaml_file, test_name)
    if test_config_dict.get("test_option"):
        run_with_test_option = True
    else:
        sorted_dict = config_parser.data_pre_processing(test_config_dict)
        input_str = config_parser.convert_dict_to_str(sorted_dict)
        config_parser.create_input_file(CURATED_APPS_PATH, input_str)
    try:
        workload_name = utils.get_workload_name(test_config_dict['docker_image'])
        curation_output = generate_curated_image(test_config_dict, run_with_test_option)
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
            else:
                result = False
            return result

        if curation_output:
            docker_run = get_docker_run_command(test_config_dict['attestation'], workload_name)
            result = run_curated_image(docker_run, test_config_dict['attestation'])
    finally:
        print("Docker images cleanup")
        utils.cleanup_after_test(workload_name)
    return result
    
    

