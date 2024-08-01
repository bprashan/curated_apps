import os
import re
from libs import utils
from data.constants import *

def run_memtier_benchmark(workload):
    result = False
    memtier_cmd = "docker run --net=host --rm redislabs/memtier_benchmark:latest --test-time=10"
    if workload == "redis":
        memtier_cmd += " -p 6379"
    elif workload == "memcached":
        memtier_cmd += " -p 11211 --protocol=memcache_binary"
    memtier_output = utils.run_subprocess(memtier_cmd)
    out = re.findall("ALL STATS.*Totals\s+(\d+.\d+)\s+(\d+.\d+)\s+(\d+.\d+)\s+(\d+.\d+)",
                     memtier_output, re.DOTALL)
    if out:
        print(out)
        result=True
    return result

def run_tensorflow_serving_client(test_config_dict):
    result = False
    response = ''
    if "mnist" in test_config_dict["runtime_args_text"] :
        client_file = "mnist_client.py"
        main_cmd = "if __name__ == '__main__':"
        proxy_cmd = "\n  import os\n  del os.environ['http_proxy']\n  del os.environ['https_proxy']"
        utils.update_file_contents(main_cmd, main_cmd + proxy_cmd, os.path.join(TF_EXAMPLE_PATH, client_file))
        response = utils.run_subprocess(f"python3 {client_file} --num_tests=1000 --server=127.0.0.1:8500",
            TF_EXAMPLE_PATH)
        if "Inference error rate: " in response: result = True
    elif "resnet" in test_config_dict["runtime_args_text"] :
        client_file = "resnet_client.py"
        utils.update_file_contents("MODEL_ACCEPT_JPG = False", "MODEL_ACCEPT_JPG = True",
            os.path.join(TF_EXAMPLE_PATH, client_file))
        response = utils.run_subprocess(f"python3 {client_file}", TF_EXAMPLE_PATH)
        if "Prediction class: " in response: result = True
    elif "half_plus_two" in test_config_dict["runtime_args_text"] :
        request = "curl -d '{\"instances\": [3.0]}' -X POST http://localhost:8501/v1/models/half_plus_two:predict"
        response = utils.run_subprocess(request)
        if '"predictions": [3.5' in response: result = True
    print(response)
    return result

def run_mysql_client(workload):
    result = False

    if not utils.is_package_installed(MYSQL_CLIENT):
        utils.run_subprocess(f"{APT_INSTALL} {MYSQL_CLIENT}", timeout=120)

    if os.path.isfile(MYSQL_INPUT_FILE):
        utils.run_subprocess(f"rm -rf {MYSQL_INPUT_FILE}")
    utils.run_subprocess(MYSQL_INPUT_TXT)
    client_cmd = MYSQL_CLIENT_CMD
    if "mariadb" in workload:
        with open(os.path.join(CURATED_APPS_PATH, MARIADB_LOGS)) as fd:
            gen_pwd = re.search("GENERATED ROOT PASSWORD(.*)", fd.read()).group().split(": ")[1]
            client_cmd += f"-p'{gen_pwd.strip()}'"
    client_cmd += f" < {MYSQL_INPUT_FILE}"
    mysql_output = utils.run_subprocess(client_cmd)
    print(mysql_output)
    if re.findall(r"^User(?s:.*?)^root*", mysql_output, re.M):
        result = True
    return result

def run_ovms_client():
    result = False
    inference_script_path = os.path.join(FRAMEWORK_PATH, "libs", "run_ovms_inference.sh")
    client_utils_path = os.path.join(FRAMEWORK_PATH, "workload_files", "client_utils.py")
    image_path = os.path.join(FRAMEWORK_PATH, "workload_files", "images")
    face_detection_file_path = os.path.join(FRAMEWORK_PATH, "workload_files", "face_detection.py")

    if not utils.is_package_installed(VENV_PACKAGE):
        utils.run_subprocess(f"{APT_INSTALL} {VENV_PACKAGE}", timeout=120)

    utils.run_subprocess(f"cp -f {client_utils_path} .", OVMS_INIT_PATH)
    utils.run_subprocess(f"cp -f {face_detection_file_path} .", OVMS_INIT_PATH)
    utils.run_subprocess(f"cp -f {inference_script_path} .", OVMS_INIT_PATH)
    utils.run_subprocess(f"chmod +x face_detection.py run_ovms_inference.sh", OVMS_INIT_PATH)
    utils.run_subprocess(f"cp -rf {image_path} .", OVMS_INIT_PATH)
    inference_output = utils.run_subprocess(f"/bin/bash run_ovms_inference.sh", OVMS_INIT_PATH)
    print(inference_output)
    inference_result = re.findall(r'Iteration 1; Processing time: \d+.\d+ ms; speed \d+.\d+ fps', inference_output)
    print(inference_result)
    if inference_result:
        result = True
    return result


