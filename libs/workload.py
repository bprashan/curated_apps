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

def run_mysql_client():
    result = False
    install_my_sql_client = utils.run_subprocess(MYSQL_CLIENT_INSTALL_CMD)
    mysql_output = utils.run_subprocess(MYSQL_CLIENT_CMD)
    print(mysql_output)
    if re.findall(r"^User(?s:.*?)^root*", mysql_output, re.M):
        result = True
    return result
