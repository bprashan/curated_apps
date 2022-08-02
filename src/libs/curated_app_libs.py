import inspect
import subprocess
import sys
import yaml
import os
import shutil
from torchvision import models
import torch

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


def run_curated_app(test_config_dict, run_with_test_option, end_test_key_exists):
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
    if end_test_key_exists:
        process.terminate()
    print(str(process.returncode))
    return process.returncode


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


def pre_actions(test_config_dict):
    if os.path.isdir(CURATED_APPS_PATH + "/test_config"):
        shutil.rmtree(CURATED_APPS_PATH + "/test_config")
    shutil.copytree("test_config", CURATED_APPS_PATH + "/test_config")

    end_test_key_str = ""
    end_test_key_exists = False
    if 'end_test' in test_config_dict.keys():
        end_test_key_exists = True
        end_test_key_str = test_config_dict["end_test"]

    pre_actions_for_verifier_image(test_config_dict, end_test_key_str)

    input_ord_list = ['signing_key_path', 'attestation', 'cert_file', 'ssl_path', 'ca_cert_file_path',
                      'runtime_variables', 'runtime_variable_list', 'encrypted_files', 'encrypted_files_path']
    # sort dictionary based on input order list
    if end_test_key_str:
        print('inside end_test_key_str ' + end_test_key_str)
        sorted_dict = {}
        for key in input_ord_list:
            if key in test_config_dict.keys():
                sorted_dict[key] = test_config_dict[key]
            if key == test_config_dict["end_test"]:
                break
    else:
        sorted_dict = {key: test_config_dict[key] for key in input_ord_list if key in test_config_dict.keys()}

    # remove verifier image input keys
    invalid_keys = ["cert_file", "ssl_path"]
    return {key: sorted_dict[key] for key in sorted_dict if key not in invalid_keys}, end_test_key_exists


def run_test(test_instance, test_yaml_file):
    run_with_test_option = False
    test_name = inspect.stack()[1].function
    print(f"\n********** Executing {test_name} **********\n")
    test_config_dict = read_config_yaml(test_yaml_file, test_name)
    if test_config_dict.get("test_option"):
        run_with_test_option = True
        return run_curated_app(test_config_dict, run_with_test_option)
    sorted_dict, end_test_key_exists = pre_actions(test_config_dict)
    input_str = get_inputs_from_dict(sorted_dict)
    print(input_str)
    create_input_file(CURATED_APPS_PATH, input_str)
    return run_curated_app(test_config_dict, run_with_test_option, end_test_key_exists)
    # return 0
