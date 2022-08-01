import inspect
import subprocess
import sys
import yaml
import os
import shutil
from torchvision import models
import torch

CURATED_APPS_PATH = os.getenv('CURATED_APPS_PATH', "")

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

def create_input_file(input_str):
    with open(CURATED_APPS_PATH + "/input.txt", mode="w") as f:
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

def run_curated_app(test_config_dict, run_with_test_option):
    workload_image = test_config_dict["docker_image"]

    if test_config_dict.get("create_local_image") == "y":
        generate_local_image(workload_image)
    
    os.chdir(CURATED_APPS_PATH)

    if run_with_test_option:
        curation_cmd = 'python3 curation_app.py ' + workload_image + ' test'
    else:
        curation_cmd = 'python3 curation_app.py ' + workload_image + ' < input.txt'
    print("Curation cmd ", curation_cmd)
    process = subprocess.Popen(curation_cmd, stdout=sys.stdout,
                        stderr=sys.stderr, shell=True)
    process.communicate()
    return process.returncode

def pre_actions(test_config_dict):
    if os.path.isdir(CURATED_APPS_PATH+"/test_config"):
        shutil.rmtree(CURATED_APPS_PATH+"/test_config")
    shutil.copytree("test_config", CURATED_APPS_PATH+"/test_config")

    input_ord_list = ['signing_key_path', 'attestation', 'ca_cert_path', 'runtime_variables',
                      'runtime_variable_list', 'encrypted_files', 'encrypted_files_path']
    # sort dictionary based on input order list
    return {key: test_config_dict[key] for key in input_ord_list if key in test_config_dict.keys()}

def run_test(test_instance, test_yaml_file):
    run_with_test_option = False
    test_name = inspect.stack()[1].function
    print(f"\n********** Executing {test_name} **********\n")
    test_config_dict = read_config_yaml(test_yaml_file, test_name)
    if test_config_dict.get("test_option"):
        run_with_test_option = True
        return run_curated_app(test_config_dict, run_with_test_option)
    sorted_dict = pre_actions(test_config_dict)
    input_str = get_inputs_from_dict(sorted_dict)
    create_input_file(input_str)
    return run_curated_app(test_config_dict, run_with_test_option)
