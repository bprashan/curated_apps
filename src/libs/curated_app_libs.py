import inspect
import subprocess
import sys
import yaml
import os
import shutil
from torchvision import models
import torch
import signal

CURATED_APPS_PATH = os.getenv('CURATED_APPS_PATH', "")
VERIFIER_SERVICE_PATH = CURATED_APPS_PATH + "/verifier_image"

def read_config_yaml(config_file_path, test_name):
    yaml_file = open(config_file_path, "r")
    parsed_yaml_file = yaml.safe_load(yaml_file)
    test_config = parsed_yaml_file["default_input_args"]

    if parsed_yaml_file.get(test_name):
        test_items = parsed_yaml_file[test_name]
        test_config.update(test_items)
    return test_config

def get_inputs_from_dict(test_config_dict):
    input_str = ''
    for key, value in test_config_dict.items():
        if value:
            input_str += str(value).strip() + "\n"
        else:
            input_str += "\n"
    return input_str

def create_input_file(path, input_str):
    with open(path + "/input.txt", mode="w") as f:
        f.write(input_str)
        f.close()

def generate_local_image(workload_image):
    if "redis" in workload_image:
        os.system("docker pull redis:latest")
    elif "pytorch" in workload_image:
        output_filename = CURATED_APPS_PATH + "/pytorch/pytorch_with_plain_text_files/plaintext/alexnet-pretrained.pt"
        alexnet = models.alexnet(pretrained=True)
        torch.save(alexnet, output_filename)
        print("Pre-trained model was saved in \"%s\"" % output_filename)
        os.chdir(CURATED_APPS_PATH + "/pytorch/pytorch_with_plain_text_files")
        os.system("docker build -t pytorch-plain .")

def pre_actions(test_config_dict):
    ordered_test_config = {}
    end_key = test_config_dict.get("end_test")
    if os.path.isdir(CURATED_APPS_PATH+"/test_config"):
        shutil.rmtree(CURATED_APPS_PATH+"/test_config")
    shutil.copytree("test_config", CURATED_APPS_PATH+"/test_config")

    pre_actions_for_verifier_image(test_config_dict, end_key)

    input_ord_list = ['signing_key_path', 'attestation', 'cert_file', 'ssl_path', 'ca_cert_file_path',
                      'runtime_variables', 'runtime_variable_list', 'encrypted_files', 'encrypted_files_path']
    invalid_keys = ["cert_file", "ssl_path"]
    # sort dictionary based on input order list
    
    for key in input_ord_list:
        if key in test_config_dict and key not in invalid_keys:
            ordered_test_config[key] = test_config_dict.get(key)
            if key == end_key:
                break
    return ordered_test_config

def generate_curated_image(test_config_dict, run_with_test_option):
    curation_output = ''
    workload_image = test_config_dict["docker_image"]

    if test_config_dict.get("create_local_image") == "y":
        generate_local_image(workload_image)
    
    os.chdir(CURATED_APPS_PATH)

    if run_with_test_option:
        curation_cmd = 'python3 curation_app.py ' + workload_image + ' test'
    else:
        curation_cmd = 'python3 curation_app.py ' + workload_image + ' < input.txt'
    print("Curation cmd ", curation_cmd)
    process = subprocess.Popen(curation_cmd, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    while True:
        output = process.stdout.readline()
        if process.poll() is not None and output == '':
            break
        if output:
            print(output.strip())
            curation_output += output
            if "docker run" in output:
                curation_output = output.strip()
    return curation_output

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def run_curated_image(gsc_docker_command):
    gsc_docker_command = gsc_docker_command.replace("-it", "-t")
    process = subprocess.Popen(gsc_docker_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, shell=True, encoding='ascii')
    while True:
        nextline = process.stdout.readline()
        print(nextline.strip())
        if nextline == '' and process.poll() is not None:
            break
        if "Ready to accept connections" in nextline:
            process.stdout.close()
            kill(process.pid)
            sys.stdout.flush()
            break

def update_verifier_service_call(filepath, old_args):
    with open(filepath, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in lines:
            if old_args in line:
                print('line found in the curation_app.py -> ' + line)
                line = line.rstrip().rstrip("'") + " < input.txt'\n"
                print('the above line shall be updated as -> ' + line)
            f.write(line)
        f.close()


def pre_actions_for_verifier_image(test_config_dict, end_test_key_str):
    if test_config_dict["attestation"] == "y" and end_test_key_str != "attestation":
        # set up the input arguments for verifier service and copy the ssl path if provided
        input_for_verifier_service = test_config_dict["cert_file"] + "\n"
        if test_config_dict["cert_file"] == "y" and end_test_key_str != "cert_file":
            input_for_verifier_service += "\n"
            # copy the verifier_image ssl folder
            if os.path.isdir(VERIFIER_SERVICE_PATH + "/ssl"):
                shutil.rmtree(VERIFIER_SERVICE_PATH + "/ssl")
            shutil.copytree(test_config_dict["ssl_path"], VERIFIER_SERVICE_PATH + "/ssl")
        # update curation_app.py to call verifier_helper_script.sh with user inputs
        old_verifier_args = "args_verifier ='./verifier_helper_script.sh'"
        update_verifier_service_call(CURATED_APPS_PATH + "/curation_app.py", old_verifier_args)
        create_input_file(VERIFIER_SERVICE_PATH, input_for_verifier_service)

def run_test(test_instance, test_yaml_file):
    run_with_test_option = False
    test_name = inspect.stack()[1].function
    print(f"\n********** Executing {test_name} **********\n")
    test_config_dict = read_config_yaml(test_yaml_file, test_name)
    if test_config_dict.get("test_option"):
        run_with_test_option = True
    else:
        sorted_dict = pre_actions(test_config_dict)
        input_str = get_inputs_from_dict(sorted_dict)
        create_input_file(CURATED_APPS_PATH, input_str)
    
    curation_output = generate_curated_image(test_config_dict, run_with_test_option)
    if test_config_dict.get("end_test") != "n":
        if test_config_dict.get("expected_output") in curation_output:
            return 1
        else:
            return 0

    workload_output = run_curated_image(curation_output)
    return 1
    
    

