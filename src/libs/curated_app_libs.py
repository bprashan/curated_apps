import inspect
import subprocess
import sys
import yaml
import os
import shutil

CURATED_APPS_PATH = os.getenv('CURATED_APPS_PATH', "")

def read_config_yaml(config_file_path, test_name):
    yaml_file = open(config_file_path, "r")
    parsed_yaml_file = yaml.safe_load(yaml_file)
    test_config = parsed_yaml_file["default_input_args"]

    if parsed_yaml_file.get(test_name):
        test_items = parsed_yaml_file[test_name]
        test_config.update(test_items)
    return test_config

def create_input_file(input_str):
    with open(CURATED_APPS_PATH + "/input.txt", mode="w") as f:
        f.write(input_str)
        f.close()


def run_curated_app(base_os, run_with_test_option):
    os.chdir(CURATED_APPS_PATH)
    if run_with_test_option:
        curation_cmd = 'python3 curation_app.py ' + base_os + ' test'
    else:
        curation_cmd = 'python3 curation_app.py ' + base_os + ' < input.txt'
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
    #print(test_config_dict)
    docker_base_os = test_config_dict["docker_image"]
    print(docker_base_os)
    if test_config_dict.get("test_option"):
        run_with_test_option = True
        return run_curated_app(docker_base_os, run_with_test_option)
    sorted_dict = pre_actions(test_config_dict)
    print(sorted_dict)
    input_str = get_inputs_from_dict(sorted_dict)
    #print(input_str)
    create_input_file(input_str)
    return run_curated_app(docker_base_os)
