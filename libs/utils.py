import subprocess
import os
import time
import psutil
import libs.config_parser as config_parser
from data.constants import *
import re

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
        run_subprocess("docker rmi gsc-{} -f".format(workload))
        run_subprocess("docker rmi gsc-{}-unsigned -f".format(workload))
        run_subprocess("docker rmi {} -f".format(workload.replace(":", "_x:")))
        run_subprocess("docker rmi verifier:latest -f")
        if run_subprocess("docker ps -a -q"):
            run_subprocess("docker rm -f $(docker ps -a -q)")
        if run_subprocess("docker volume ls -q"):
            run_subprocess("docker volume rm $(docker volume ls -q)")
        #run_subprocess("docker system prune -f")
        #run_subprocess("docker rmi pytorch-plain:latest")
        #run_subprocess("docker rmi pytorch-encryption:latest")
        #run_subprocess("docker rmi bash-test:latest -f")
    except Exception as e:
        print("Exception occured during cleanup ", e)

def get_workload_name(docker_image):
    try:
        return docker_image.split(" ")[1]
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

def create_docker_image(docker_path, docker_name):
    docker_build_cmd = "docker build -t %s ." % docker_name
    print("docker build cmd is ", docker_build_cmd)
    output = run_subprocess(docker_build_cmd, docker_path)
    print(output)

def generate_local_image(workload_image, encryption):
    if "pytorch" in workload_image:
        if encryption:
            output = run_subprocess(PYTORCH_HELPER_CMD + " encrypt", PYTORCH_HELPER_PATH)
        else:
            output = run_subprocess(PYTORCH_HELPER_CMD, PYTORCH_HELPER_PATH)
        print(output)
    elif "bash" in workload_image:
        image_name = workload_image.split(":")[0].split(" ")[1]
        create_docker_image(BASH_PATH, image_name)
    elif "redis" in workload_image:
        run_subprocess("docker pull redis:7.0.0")

def local_image_setup(test_config_dict):
    encryption = False
    if test_config_dict.get("create_local_image") == "y":
        if test_config_dict["docker_image"] == "pytorch pytorch-base-encrypt:latest":
            encryption = True
        generate_local_image(test_config_dict["docker_image"], encryption)
    return encryption

def test_setup(test_config_dict):
    if test_config_dict.get("test_option") == None:
        sorted_dict = config_parser.data_pre_processing(test_config_dict)
        input_str = config_parser.convert_dict_to_str(sorted_dict)
        config_parser.create_input_file(input_str)
    else:
        config_parser.create_input_file(b'\x07')
    encryption = local_image_setup(test_config_dict)
    return encryption

def update_file_contents(old_contents, new_contents, filename):
    fd = open(filename)
    fd_contents = fd.read()
    fd.close()
    new_data = re.sub(old_contents, new_contents, fd_contents)
    fd = open(filename, "w")
    fd.write(new_data)
    fd.close()