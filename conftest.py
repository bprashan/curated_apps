import pytest
import os
from data.constants import *
from libs import utils
import re


@pytest.fixture(scope="session")
def curated_setup():
    utils.run_subprocess("rm -rf logs")
    os.mkdir("logs")
    print("Cleaning old contrib repo")
    rm_cmd = "rm -rf {}".format(ORIG_CURATED_PATH)
    utils.run_subprocess(rm_cmd)
    print("Cloning and checking out Contrib Git Repo")
    utils.run_subprocess(CONTRIB_GIT_CMD)
    utils.run_subprocess(GIT_CHECKOUT_CMD, ORIG_CURATED_PATH)
    if utils.check_machine() == "DCAP client":
        print("Configuring the contrib repo to setup DCAP client")
        dcap_setup()

@pytest.fixture()
def copy_repo():
    copy_cmd = "cp -rf {} {}".format(ORIG_CURATED_PATH, REPO_PATH)
    utils.run_subprocess("rm -rf contrib_repo")
    utils.run_subprocess(copy_cmd)

def dcap_setup():
    copy_cmd = "cp /etc/sgx_default_qcnl.conf {}/verifier_image/".format(os.path.join(ORIG_CURATED_PATH, CURATED_PATH))
    utils.run_subprocess(copy_cmd)
    fd = open(VERIFIER_DOCKERFILE)
    fd_contents = fd.read()
    azure_dcap = "(.*)RUN wget https:\/\/packages.microsoft(.*)\n(.*)amd64.deb"
    updated_content = re.sub(azure_dcap, "", fd_contents)
    dcap_library = "RUN apt-get install -y gramine-dcap\nRUN apt install -y libsgx-dcap-default-qpl libsgx-dcap-default-qpl-dev\nCOPY sgx_default_qcnl.conf  /etc/sgx_default_qcnl.conf"
    new_data = re.sub("RUN apt-get install -y gramine-dcap", dcap_library, updated_content)
    fd.close()

    fd = open(VERIFIER_DOCKERFILE, "w+")
    fd.write(new_data)
    fd.close()

    

