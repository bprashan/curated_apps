import os

FRAMEWORK_PATH         = os.getcwd()
REPO_PATH              = os.path.join(FRAMEWORK_PATH, "contrib_repo")
ORIG_CURATED_PATH      = os.path.join(FRAMEWORK_PATH, "orig_contrib_repo")
CONTRIB_GIT_REPO       = os.environ.get("contrib_repo")
if not CONTRIB_GIT_REPO:
    CONTRIB_GIT_REPO = "https://github.com/gramineproject/contrib.git"
CONTRIB_GIT_CMD        = f"git clone {CONTRIB_GIT_REPO} orig_contrib_repo"
CONTRIB_BRANCH         = os.environ.get("contrib_branch")
if not CONTRIB_BRANCH:
    CONTRIB_BRANCH = "master"
GIT_CHECKOUT_CMD       = f"git checkout {CONTRIB_BRANCH}"
CURATED_PATH           = "Curated-Apps"
CURATED_APPS_PATH      = os.path.join(REPO_PATH, CURATED_PATH)
WORKLOADS_PATH         = os.path.join(CURATED_APPS_PATH, "workloads")
COMMANDS_TXT_PATH      = os.path.join(CURATED_APPS_PATH, "commands.txt")
VERIFIER_SERVICE_PATH  = os.path.join(CURATED_APPS_PATH, "verifier")
VERIFIER_TEMPLATE      = "verifier.dockerfile.template"
ORIG_BASE_PATH         = os.path.join(ORIG_CURATED_PATH, CURATED_PATH)
VERIFIER_DOCKERFILE    = os.path.join(ORIG_BASE_PATH, "verifier", VERIFIER_TEMPLATE)
PYTORCH_HELPER_PATH    = os.path.join(WORKLOADS_PATH, "pytorch", "base_image_helper")
PYTORCH_HELPER_CMD     = f"bash {PYTORCH_HELPER_PATH}/helper.sh"
SKLEARN_HELPER_PATH    = os.path.join(WORKLOADS_PATH, "sklearn", "base_image_helper")
SKLEARN_HELPER_CMD     = f"bash {SKLEARN_HELPER_PATH}/helper.sh"
TFSERVING_HELPER_PATH    = os.path.join(WORKLOADS_PATH, "tensorflow-serving", "base_image_helper")
TFSERVING_HELPER_CMD     = f"bash {TFSERVING_HELPER_PATH}/helper.sh"
BASH_PATH              = os.path.join(WORKLOADS_PATH, "bash")
SCREEN_LIST            = ["home_page", "distro_page", "runtime_page", "environment_page", "flags_page", "encrypted_page", "encryption_key_page",
                            "attestation_page", "signing_page", "signing_key_password", "verifier_page", "final_page"]
BASH_DOCKERFILE        = os.path.join(WORKLOADS_PATH, "bash", "Dockerfile")
BASH_GSC_DOCKERFILE    = os.path.join(WORKLOADS_PATH, "bash", "bash-gsc.dockerfile.template")
ENV_PROXY_STRING       = 'ENV http_proxy "http://proxy-dmz.intel.com:911"\nENV https_proxy "http://proxy-dmz.intel.com:912"\n'
AZURE_DCAP             = "(.*)RUN wget https:\/\/packages.microsoft(.*)\n(.*)amd64.deb"
GRAMINE_INSTALL        = "RUN apt-get install -y gramine-dcap"
DCAP_LIBRARY           = "\nRUN apt install -y libsgx-dcap-default-qpl libsgx-dcap-default-qpl-dev\nCOPY sgx_default_qcnl.conf  /etc/sgx_default_qcnl.conf\n"
DCAP_ORD_LIST          = ['start', 'azure_warning', 'distro', 'runtime_args_text', 'runtime_variable_list', 'docker_flags', 'encrypted_files_path', 'encryption_key', 
                            'attestation', 'signing_key_path', 'signing_key_password', 'end']
AZURE_ORD_LIST         = ['start', 'distro', 'runtime_args_text', 'runtime_variable_list', 'docker_flags', 'encrypted_files_path', 'encryption_key', 
                            'attestation', 'signing_key_path', 'signing_key_password', 'end']
UBUNTU_18_04           = "From ubuntu:18.04"
UBUNTU_20_04           = "From ubuntu:20.04"
LOGS                   = os.path.join(FRAMEWORK_PATH, "logs")
GRAMINE_VERSION        = "v1.3.1"
TEST_CONFIG_PATH       = os.path.join(FRAMEWORK_PATH, "test_config")
CONFIG_YAML            = "config.yaml.template"
GRAMINE_CLONE          = "git clone --depth 1 --branch v1.3.1 https://github.com/gramineproject/gramine.git"
GSC_CLONE              = "git clone --depth 1 --branch v1.3.1 https://github.com/gramineproject/gsc.git"
DEPTH_STR              = "--depth 1 --branch v1.3.1 "
TF_EXAMPLE_PATH        = os.path.join(TFSERVING_HELPER_PATH, "serving/tensorflow_serving/example")
TF_IMAGE               = "gramine.azurecr.io:443/base_images/intel-optimized-tensorflow-serving-avx512-ubuntu18.04"