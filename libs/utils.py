import subprocess
import os
import time
import psutil
import libs.config_parser as config_parser
from torchvision import models
import torch
from data.constants import *

def run_subprocess(command, dest_dir=None):
    if dest_dir:
        os.chdir(dest_dir)

    print("Starting Process %s from %s" %(command, os.getcwd()))
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True, shell=True)
    if process.returncode != 0:
        print(process.stderr.strip())
        raise Exception("Failed to run command {}".format(command))
    
    if dest_dir: os.chdir(FRAMEWORK_PATH)
    return process.stdout.strip()

def popen_subprocess(command, dest_dir=None):
    if dest_dir:
        os.chdir(dest_dir)

    print("Starting Process ", command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    time.sleep(1)
   
    if dest_dir: os.chdir(FRAMEWORK_PATH)
    return process

def kill(proc_pid):
    try:
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.terminate()
        process.terminate()
    except:
        pass

def kill_process_by_name(processName):
    procs = [p for p in psutil.process_iter() for c in p.cmdline() if processName in c]
    for process in procs:
        try:
            run_subprocess("sudo kill -9 {}".format(process.pid))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def cleanup_after_test(workload):
    try:
        kill_process_by_name("secret_prov_server_dcap")
        kill_process_by_name("/gramine/app_files/apploader.sh")
        kill_process_by_name("/gramine/app_files/entrypoint")
        kill_process_by_name("/gramine/meson_build_output/lib/x86_64-linux-gnu/gramine/sgx/loader")
        run_subprocess('sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"')
        run_subprocess("docker rmi gsc-{}x -f".format(workload))
        run_subprocess("docker rmi gsc-{}x-unsigned -f".format(workload))
        run_subprocess("docker rmi {}x -f".format(workload))
        run_subprocess("docker rmi verifier_image:latest -f")
        run_subprocess("docker system prune -f")
        run_subprocess("docker rmi pytorch-plain:latest")
        run_subprocess("docker rmi pytorch-encryption:latest")
        run_subprocess("docker rmi bash-test:latest")
    except Exception as e:
        print("Exception occured during cleanup ", e)

def get_workload_name(docker_image):
    try:
        return docker_image.split("/")[1]
    except Exception as e:
        return ''

def check_machine():
    service_cmd = "sudo systemctl --type=service --state=running"
    service_output = run_subprocess(service_cmd)
    if "walinuxagent.service" in service_output:
        print("Running on Azure Linux Agent")
        return "Azure Linux Agent"
    elif "pccs.service" in service_output:
        print("Running on DCAP client")
        return "DCAP client"
    else:
        print("No Provisioning service found, cannot run tests with attestation.")
        return "No Provisioning enabled"

def generate_encrypted_files(path, filename):
    output_path = os.path.join(path, "encrypted", "alexnet-pretrained.pt")
    encrypt_cmd = "gramine-sgx-pf-crypt encrypt -w wrap-key -i {} -o {}".format(filename, output_path)
    run_subprocess(encrypt_cmd, path)

def create_docker_image(docker_path, docker_name):
    docker_build_cmd = "docker build -t %s ." % docker_name
    print("docker build cmd is ", docker_build_cmd)
    output = run_subprocess(docker_build_cmd, docker_path)
    print(output)

def generate_local_image(workload_image, encryption=None):
    if "pytorch" in workload_image:
        output_filename = PYTORCH_PLAIN_PATH + "/plaintext/alexnet-pretrained.pt"
        alexnet = models.alexnet(pretrained=True)
        torch.save(alexnet, output_filename)
        print("Pre-trained model is saved in \"%s\"" % output_filename)

        if encryption == "y":
            generate_encrypted_files(PYTORCH_ENCRYPTED_PATH, output_filename)
            create_docker_image(PYTORCH_ENCRYPTED_PATH, PYTORCH_ENCRYPTION)
        else:
            create_docker_image(PYTORCH_PLAIN_PATH, PYTORCH_PLAIN)
    elif "bash" in workload_image:
        create_docker_image(BASH_PATH, BASH_TEST)

def test_setup(test_config_dict):
    if test_config_dict.get("test_option") == None:
        workload_image = test_config_dict["docker_image"]
        sorted_dict = config_parser.data_pre_processing(test_config_dict)
        input_str = config_parser.convert_dict_to_str(sorted_dict)
        config_parser.create_input_file(input_str)

        if test_config_dict.get("create_local_image") == "y":
            generate_local_image(workload_image, test_config_dict.get("encrypted_files"))
    else:
        config_parser.create_input_file(b'\x07')