import pytest
import os
from data.constants import *
from libs import utils

@pytest.fixture(scope="session")
def curated_setup():
    utils.run_subprocess(f"rm -rf {LOGS}")
    os.mkdir(LOGS)
    print("Cleaning old contrib repo")
    utils.run_subprocess("rm -rf {}".format(REPO_PATH))
    utils.run_subprocess("rm -rf {}".format(ORIG_CURATED_PATH))
    print("Cloning and checking out Contrib Git Repo")
    utils.run_subprocess(CONTRIB_GIT_CMD)
    utils.run_subprocess(GIT_CHECKOUT_CMD, ORIG_CURATED_PATH)
    if utils.check_machine() == "DCAP client":
        print("Configuring the contrib repo to setup DCAP client")
        dcap_setup()

@pytest.fixture()
def copy_repo():
    utils.run_subprocess("rm -rf {}".format(REPO_PATH))
    utils.run_subprocess("cp -rf {} {}".format(ORIG_CURATED_PATH, REPO_PATH))

def dcap_setup():
    copy_cmd = "cp /etc/sgx_default_qcnl.conf {}/verifier/".format(os.path.join(ORIG_CURATED_PATH, CURATED_PATH))
    utils.run_subprocess(copy_cmd)
    utils.update_file_contents(AZURE_DCAP, "", VERIFIER_DOCKERFILE)
    utils.update_file_contents(GRAMINE_INSTALL, GRAMINE_INSTALL+DCAP_LIBRARY, VERIFIER_DOCKERFILE)
    utils.update_file_contents('sgx.enclave_size = "8G"', 'sgx.enclave_size = "4G"', 
                os.path.join(ORIG_CURATED_PATH, CURATED_PATH, "pytorch", "pytorch.manifest.template"))

@pytest.fixture(scope="function")
def clone_gsc_repo():
    print("Cleaning old gsc repo")
    utils.run_subprocess("rm -rf {}".format(GSC_REPO_PATH))
    print("Cloning and checking out GSC Git Repo")
    utils.run_subprocess(GSC_CHECKOUT_CMD, FRAMEWORK_PATH)
    utils.run_subprocess(CONFIG_YAML_CMD, GSC_REPO_PATH)

