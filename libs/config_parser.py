import sys
import yaml
import os
import shutil
from data.constants import *
from libs import utils
import re

def read_config_yaml(config_file_path, test_name):
    yaml_file = open(config_file_path, "r")
    parsed_yaml_file = yaml.safe_load(yaml_file)
    test_config = parsed_yaml_file["default_input_args"]

    if parsed_yaml_file.get(test_name):
        test_items = parsed_yaml_file[test_name]
        test_config.update(test_items)
        test_config["log_file"] = f"logs/{test_name}.log"
    return test_config

def convert_dict_to_str(test_config_dict):
    input_str = b''
    for key, value in test_config_dict.items():
        if value:
            input_str += str(value).strip().encode('utf-8') + b'\x07'
        else:
            input_str += b'\x07'
        if key == test_config_dict.get('end_test'):
            input_str += b'\x1a'
            break
    # Curator app expects ANY key press as the last input, after copying ssl certificates.
    return input_str

def create_input_file(input_str):
    path = CURATED_APPS_PATH + "/input.txt"
    with open(path, mode="wb") as f:
        f.write(input_str)
        f.close()

def data_pre_processing(test_config_dict):
    ordered_test_config = {}
    end_key = test_config_dict.get("end_test")
    if os.path.isdir(CURATED_APPS_PATH + "/test_config"):
        shutil.rmtree(CURATED_APPS_PATH + "/test_config")
    shutil.copytree("test_config", CURATED_APPS_PATH + "/test_config")

    data_pre_processing_for_verifier_image(test_config_dict, end_key)

    if utils.check_machine() == "DCAP client":
        input_ord_list = DCAP_ORD_LIST
    else:
        input_ord_list = AZURE_ORD_LIST

    for key in input_ord_list:
        if key in test_config_dict.keys():
            ordered_test_config[key] = test_config_dict.get(key)
            if key == end_key:
                ordered_test_config['end_test'] = key
                break
    return ordered_test_config

def data_pre_processing_for_verifier_image(test_config_dict, end_test_key_str):
    if test_config_dict["attestation"] == "done" and end_test_key_str != "attestation":
            # copy the verifier ssl folder
        if os.path.isdir(VERIFIER_SERVICE_PATH + "/ssl"):
            shutil.rmtree(VERIFIER_SERVICE_PATH + "/ssl")
        if test_config_dict['ssl_path']:
            shutil.copytree(test_config_dict["ssl_path"], VERIFIER_SERVICE_PATH + "/ssl")
    if "bash" in test_config_dict['docker_image']:
        bash_setup(test_config_dict['docker_image'])

def bash_setup(docker_image):
    shutil.copytree("data/bash", CURATED_APPS_PATH + "/bash")
    if "ubuntu_20_04" in docker_image:
        utils.update_file_contents(UBUNTU_18_04, UBUNTU_20_04, BASH_DOCKERFILE)
    if utils.check_machine() == "Azure Linux Agent":
        utils.update_file_contents(ENV_PROXY_STRING, '', BASH_DOCKERFILE)
        utils.update_file_contents(ENV_PROXY_STRING, '', BASH_GSC_DOCKERFILE)
   