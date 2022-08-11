import subprocess
import os
import time
import psutil

def run_subprocess(command, dest_dir=None):
    cwd = os.getcwd()
    if dest_dir:
        os.chdir(dest_dir)

    print("Starting Process %s from %s" %(command, os.getcwd()))
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True, shell=True)
    if process.returncode != 0:
        raise Exception("Failed to run command {}".format(command))
    
    if dest_dir: os.chdir(cwd)
    return process.stdout.strip()

def popen_subprocess(command, dest_dir=None):
    if dest_dir:
        cwd = os.getcwd()
        os.chdir(dest_dir)

    print("Starting Process ", command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    time.sleep(1)
   
    if dest_dir: os.chdir(cwd)
    return process

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()

def kill_process_by_name(processName):
    procs = [p.pid for p in psutil.process_iter() for c in p.cmdline() if "/gramine/app_files/apploader.sh" in c]
    for process in procs:
        try:
            utils.run_subprocess("sudo kill -9 {}".format(process))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def cleanup_after_test(workload):
    try:
        utils.run_subprocess("docker rmi verifier_image:latest -f")
        utils.run_subprocess('sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"')
        utils.run_subprocess("docker rmi gsc-{}-wrapper -f".format(workload))
        utils.run_subprocess("docker rmi gsc-{}-wrapper-unsigned -f".format(workload))
        utils.run_subprocess("docker rmi {}-wrapper -f".format(workload))
        kill_process_by_name("/gramine/app_files/apploader.sh")
        kill_process_by_name("/gramine/app_files/entrypoint")
    except Exception as e:
        pass

def get_workload_name(docker_image):
    return docker_image.split("/")[1]
