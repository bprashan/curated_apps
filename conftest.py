import pytest
import os
from data.constants import *
from libs import utils

@pytest.fixture(scope="session")
def curated_setup():
    print_env_variables()
    utils.run_subprocess(f"rm -rf {LOGS}")
    os.mkdir(LOGS)
    print("Cleaning old contrib repo")
    utils.run_subprocess("rm -rf {}".format(REPO_PATH))
    utils.run_subprocess("rm -rf {}".format(ORIG_CURATED_PATH))
    print("Cloning and checking out Contrib Git Repo")
    utils.run_subprocess(CONTRIB_GIT_CMD)
    utils.run_subprocess(GIT_CHECKOUT_CMD, ORIG_CURATED_PATH)
    os.environ["SETUP_MACHINE"] = utils.check_machine()
    if os.environ["SETUP_MACHINE"] == "DCAP client":
        print("Configuring the contrib repo to setup DCAP client")
        dcap_setup()
    elif os.environ["SETUP_MACHINE"] == "Azure Linux Agent":
        azure_setup()
    update_env_variables()

def update_env_variables():
    gramine_commit = os.environ.get('gramine_commit', '')
    if gramine_commit:
        update_gramine_branch(gramine_commit)
    gsc_repo = os.environ.get('gsc_repo', '')
    gsc_commit = os.environ.get('gsc_commit', '')
    if gsc_commit or gsc_repo:
        update_gsc(gsc_commit, gsc_repo)

def print_env_variables():
    print("\n\n############################################################################")
    print("Printing the environment variables")
    print("Gramine Commit: ", os.environ.get("gramine_commit", ""))
    print("GSC Repo: ", os.environ.get("gsc_repo", ""))
    print("GSC Commit: ", os.environ.get("gsc_commit", ""))
    print("Contrib Repo: ", os.environ.get("contrib_repo", ""))
    print("Contrib Commit: ", os.environ.get("contrib_branch", ""))
    print("############################################################################\n\n")

@pytest.fixture()
def copy_repo():
    utils.run_subprocess("rm -rf {}".format(REPO_PATH))
    utils.run_subprocess("cp -rf {} {}".format(ORIG_CURATED_PATH, REPO_PATH))

def dcap_setup():
    copy_cmd = "cp /etc/sgx_default_qcnl.conf {}/verifier/".format(os.path.join(ORIG_CURATED_PATH, CURATED_PATH))
    utils.run_subprocess(copy_cmd)
    utils.update_file_contents(AZURE_DCAP, "", VERIFIER_DOCKERFILE)
    utils.update_file_contents(GRAMINE_INSTALL, GRAMINE_INSTALL+DCAP_LIBRARY, VERIFIER_DOCKERFILE)
    # utils.update_file_contents('sgx.enclave_size = "8G"', 'sgx.enclave_size = "4G"', 
    #             os.path.join(ORIG_CURATED_PATH, CURATED_PATH, "workloads/pytorch", "pytorch.manifest.template"))

def azure_setup():
    utils.update_file_contents('sgx.enclave_size = "64G"', 'sgx.enclave_size = "16G"',
        os.path.join(ORIG_BASE_PATH, "workloads/tensorflow-serving",
        "tensorflow-serving.manifest.template"))

def update_gramine_branch(commit):
    commit_str = f" && cd gramine && git checkout {commit} && cd .."
    if commit != "master":
        utils.update_file_contents(GRAMINE_VERSION, commit, os.path.join(ORIG_BASE_PATH, "util", CONFIG_YAML))
        utils.update_file_contents(GRAMINE_CLONE, GRAMINE_CLONE.replace(DEPTH_STR, "") + commit_str,
            VERIFIER_DOCKERFILE)
    else:
        utils.run_subprocess(f"cp -rf helper-files/{VERIFIER_TEMPLATE} {VERIFIER_DOCKERFILE}")
        utils.run_subprocess(f"cp -rf helper-files/{CONFIG_YAML} {ORIG_BASE_PATH}/util/{CONFIG_YAML}")
    utils.update_file_contents(GRAMINE_CLONE, GRAMINE_CLONE.replace(DEPTH_STR, "") + commit_str,
        os.path.join(ORIG_BASE_PATH, "verifier", "helper.sh"))

def update_gsc(gsc_commit='', gsc_repo=''):
    curation_script = os.path.join(ORIG_BASE_PATH, "util", "curation_script.sh")
    if gsc_commit: checkout_str = f" && cd gsc && git checkout {gsc_commit} && cd .."
    if gsc_repo: repo_str = f"git clone {gsc_repo}"
    if gsc_repo and gsc_commit:
        utils.update_file_contents(GSC_CLONE, repo_str + checkout_str, curation_script)
    elif gsc_repo and not gsc_commit:
        utils.update_file_contents(GSC_CLONE, repo_str, curation_script)
    elif gsc_commit:
        utils.update_file_contents(GSC_CLONE, GSC_CLONE.replace(DEPTH_STR, "") + checkout_str, curation_script)
