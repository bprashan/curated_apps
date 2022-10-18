import yaml
import os
import shutil
from data.constants import *
from libs import utils

def read_config_yaml(config_file_path, test_name):
    yaml_file = open(config_file_path, "r")
    parsed_yaml_file = yaml.safe_load(yaml_file)
    test_config = parsed_yaml_file["default_input_args"]

    if parsed_yaml_file.get(test_name):
        test_config["test_name"] = test_name
        test_items = parsed_yaml_file[test_name]
        test_config.update(test_items)
        test_config["log_file"] = f"{LOGS}/{test_name}.log"
        base_image_name = test_config.get("docker_image").split(' ', maxsplit=1)[1]
        base_image_type = test_config.get("docker_image").split(' ', maxsplit=1)[0]
        # log_file_name, n = re.subn('[:/]', '_', base_image_name)
        log_file_name = base_image_name.replace(":", "_")
        log_file = f'{WORKLOADS_PATH}/{base_image_type}/{log_file_name}.log'
        test_config["curation_log"] = log_file
    return test_config

def convert_dict_to_str(sorted_dict):
    input_str = b''
    for key, value in sorted_dict.items():
        if value:
            input_str += str(value).strip().encode('utf-8') + b'\x07'
        else:
            input_str += b'\x07'
        if key == sorted_dict.get('end_test'):
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

    if os.environ["SETUP_MACHINE"] == "Azure Linux Agent":
        input_ord_list = AZURE_ORD_LIST
    else:
        input_ord_list = DCAP_ORD_LIST

    for key in input_ord_list:
        if key in test_config_dict.keys():
            ordered_test_config[key] = test_config_dict.get(key)
            if key == end_key:
                ordered_test_config['end_test'] = key
                break
    return ordered_test_config

def generate_ssl_certificate():
    utils.run_subprocess("rm -rf test_config/ssl/server.crt >/dev/null 2>&1")
    utils.run_subprocess("rm -rf test_config/ssl/ca.key >/dev/null 2>&1")
    utils.run_subprocess("rm -rf test_config/ssl/server.key >/dev/null 2>&1")

    utils.run_subprocess("openssl genrsa -out ssl/ca.key 2048", TEST_CONFIG_PATH)
    utils.run_subprocess("openssl req -x509 -new -nodes -key ssl/ca.key -sha256 -days 1024 \
        -out ssl/ca.crt -config ssl/ca_config.conf", TEST_CONFIG_PATH)
    utils.run_subprocess("openssl genrsa -out ssl/server.key 2048", TEST_CONFIG_PATH)
    utils.run_subprocess("openssl req -new -key ssl/server.key -out ssl/server.csr -config \
        ssl/ca_config.conf", TEST_CONFIG_PATH)
    utils.run_subprocess("openssl x509 -req -days 360 -in ssl/server.csr -CA ssl/ca.crt -CAkey \
        ssl/ca.key -CAcreateserial -out ssl/server.crt", TEST_CONFIG_PATH)

def data_pre_processing_for_verifier_image(test_config_dict, end_test_key_str):
    if test_config_dict["attestation"] == "done" and end_test_key_str != "attestation":
        generate_ssl_certificate()
        # copy the verifier ssl folder
        if os.path.isdir(VERIFIER_SERVICE_PATH + "/ssl"):
            shutil.rmtree(VERIFIER_SERVICE_PATH + "/ssl")
        if test_config_dict['ssl_path']:
            shutil.copytree(test_config_dict["ssl_path"], VERIFIER_SERVICE_PATH + "/ssl")
    if "bash" in test_config_dict['docker_image']:
        bash_setup(test_config_dict['docker_image'])

def bash_setup(docker_image):
    shutil.copytree("data/bash", BASH_PATH)
    if "ubuntu_20_04" in docker_image:
        utils.update_file_contents(UBUNTU_18_04, UBUNTU_20_04, BASH_DOCKERFILE)
    if os.environ["SETUP_MACHINE"] == "Azure Linux Agent":
        utils.update_file_contents(ENV_PROXY_STRING, '', BASH_DOCKERFILE)
        utils.update_file_contents(ENV_PROXY_STRING, '', BASH_GSC_DOCKERFILE)
   