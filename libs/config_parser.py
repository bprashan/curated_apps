import sys
import yaml
import os
import shutil
from data.constants import *

def read_config_yaml(config_file_path, test_name):
    yaml_file = open(config_file_path, "r")
    parsed_yaml_file = yaml.safe_load(yaml_file)
    test_config = parsed_yaml_file["default_input_args"]

    if parsed_yaml_file.get(test_name):
        test_items = parsed_yaml_file[test_name]
        test_config.update(test_items)
    return test_config

def convert_dict_to_str(test_config_dict):
    input_str = ''
    for key, value in test_config_dict.items():
        if value:
            input_str += str(value).strip() + "\n"
        else:
            input_str += "\n"
    # Curator app expects ANY key press as the last input, after copying ssl certificates.
    input_str += "\n"
    return input_str

def create_input_file(path, input_str):
    with open(path + "/input.txt", mode="w") as f:
        f.write(input_str)
        f.close()

def data_pre_processing(test_config_dict):
    ordered_test_config = {}
    end_key = test_config_dict.get("end_test")
    if os.path.isdir(CURATED_APPS_PATH + "/test_config"):
        shutil.rmtree(CURATED_APPS_PATH + "/test_config")
    shutil.copytree("test_config", CURATED_APPS_PATH + "/test_config")

    data_pre_processing_for_verifier_image(test_config_dict, end_key)

    input_ord_list = ['signing_key_path', 'runtime_args', 'runtime_variables', 'runtime_variable_list',
                      'attestation', 'encrypted_files', 'encrypted_files_path', 'encryption_key', 'cert_file']

    for key in input_ord_list:
        if key in test_config_dict:
            ordered_test_config[key] = test_config_dict.get(key)
            if key == end_key:
                break
    return ordered_test_config

def data_pre_processing_for_verifier_image(test_config_dict, end_test_key_str):
    if test_config_dict["attestation"] == "y" and end_test_key_str != "attestation":
        if test_config_dict["cert_file"] == "y" and end_test_key_str != "cert_file":
            # copy the verifier_image ssl folder
            if os.path.isdir(VERIFIER_SERVICE_PATH + "/ssl"):
                shutil.rmtree(VERIFIER_SERVICE_PATH + "/ssl")
            if test_config_dict['ssl_path']:
                shutil.copytree(test_config_dict["ssl_path"], VERIFIER_SERVICE_PATH + "/ssl")
