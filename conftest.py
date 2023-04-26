import pytest
import os
from data.constants import *
from libs import utils

@pytest.fixture(scope="session", autouse=True)
def curated_setup():
    print_env_variables()
    utils.run_subprocess(f"rm -rf {LOGS}")
    os.mkdir(LOGS)
    utils.run_subprocess("docker system prune -f --all")
    utils.stop_docker_process("server_dcap")
    print("Cleaning old contrib repo")
    utils.run_subprocess("rm -rf {}".format(ORIG_CURATED_PATH))
    print("Cloning and checking out Contrib Git Repo")
    utils.run_subprocess(CONTRIB_GIT_CMD)
    utils.run_subprocess(GIT_CHECKOUT_CMD, ORIG_CURATED_PATH)
    if REBASE_CONTRIB_GIT_REPO:
        utils.run_subprocess(REBASE_GIT_REPO_CMD, ORIG_CURATED_PATH)
        utils.run_subprocess(FETCH_REBASE_REPO_CMD, ORIG_CURATED_PATH)
        utils.run_subprocess(REBASE_BRANCH_CMD, ORIG_CURATED_PATH)
    update_env_variables()

def update_env_variables():
    if os.environ["gramine_commit"]:
        update_gramine_branch(os.environ["gramine_commit"])
    if os.environ["gsc_repo"] or os.environ["gsc_commit"]:
        update_gsc(os.environ["gsc_commit"], os.environ["gsc_repo"])

def print_env_variables():
    os.environ["gramine_commit"] = os.environ.get("gramine_commit", "")
    os.environ["gsc_repo"]       = os.environ.get("gsc_repo", "")
    os.environ["gsc_commit"]     = os.environ.get("gsc_commit", "")
    os.environ["contrib_repo"]   = os.environ.get("contrib_repo", "")
    os.environ["contrib_branch"] = os.environ.get("contrib_branch", "")
    os.environ["rebase_contrib_repo"]   = os.environ.get("rebase_contrib_repo", "")
    os.environ["rebase_contrib_branch"] = os.environ.get("rebase_contrib_branch", "")
    print("\n\n############################################################################")
    print("Printing the environment variables")
    print("Gramine Commit: ", os.environ["gramine_commit"])
    print("GSC Repo:       ", os.environ["gsc_repo"])
    print("GSC Commit:     ", os.environ["gsc_commit"])
    print("Contrib Repo:   ", os.environ["contrib_repo"])
    print("Contrib Commit: ", os.environ["contrib_branch"])
    print("Rebase Contrib Repo:   ", os.environ["rebase_contrib_repo"])
    print("Rebase Contrib Commit: ", os.environ["rebase_contrib_branch"])
    print("############################################################################\n\n")

@pytest.fixture(scope="function", autouse=True)
def copy_repo():
    utils.run_subprocess("sudo rm -rf {}".format(REPO_PATH))
    utils.run_subprocess("cp -rf {} {}".format(ORIG_CURATED_PATH, REPO_PATH))

def update_gramine_branch(commit):
    commit_str = f" && cd gramine && git checkout {commit} && cd .."
    copy_cmd = "cp config.yaml.template config.yaml"
    if not "v1" in commit:
        utils.run_subprocess(f"cp -rf helper-files/{VERIFIER_TEMPLATE} {VERIFIER_DOCKERFILE}")
    utils.update_file_contents(copy_cmd, copy_cmd + "\nsed -i 's|Branch:.*master|Branch: \"{}|' config.yaml".format(commit), CURATION_SCRIPT)
    utils.update_file_contents(GRAMINE_CLONE, GRAMINE_CLONE.replace(GRAMINE_DEPTH_STR, "") + commit_str,
            VERIFIER_DOCKERFILE)
    utils.update_file_contents(GRAMINE_CLONE, GRAMINE_CLONE.replace(GRAMINE_DEPTH_STR, "") + commit_str,
        os.path.join(ORIG_BASE_PATH, "verifier", "helper.sh"))

def update_gsc(gsc_commit='', gsc_repo=''):
    if gsc_commit: checkout_str = f" && cd gsc && git checkout {gsc_commit} && cd .."
    if gsc_repo: repo_str = f"git clone {gsc_repo}"
    if gsc_repo and gsc_commit:
        utils.update_file_contents(GSC_CLONE, repo_str + checkout_str, CURATION_SCRIPT)
    elif gsc_repo and not gsc_commit:
        utils.update_file_contents(GSC_CLONE, repo_str, CURATION_SCRIPT)
    elif gsc_commit:
        utils.update_file_contents(GSC_CLONE, GSC_CLONE.replace(GSC_DEPTH_STR, "") + checkout_str, CURATION_SCRIPT)

@pytest.fixture(scope="class", autouse=True)
def teardown():
    yield
    utils.run_subprocess("docker system prune -f --all")

