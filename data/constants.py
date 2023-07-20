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
REBASE_CONTRIB_GIT_REPO = os.environ.get("rebase_contrib_repo")
REBASE_CONTRIB_BRANCH  = os.environ.get("rebase_contrib_branch")
REBASE_GIT_REPO_CMD    = f"git remote add repo_rebase {REBASE_CONTRIB_GIT_REPO}"
FETCH_REBASE_REPO_CMD  = f"git fetch repo_rebase"
REBASE_BRANCH_CMD      = f"git rebase repo_rebase/{REBASE_CONTRIB_BRANCH}"
CURATED_PATH           = "Intel-Confidential-Compute-for-X"
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
SCREEN_LIST            = ["home_page", "runtime_page", "environment_page", "flags_page", "encrypted_page", "encryption_key_page",
                            "attestation_page", "signing_page", "signing_key_password", "verifier_page", "final_page"]
BASH_DOCKERFILE        = os.path.join(WORKLOADS_PATH, "bash", "Dockerfile")
BASH_GSC_DOCKERFILE    = os.path.join(WORKLOADS_PATH, "bash", "bash-gsc.dockerfile.template")
ENV_PROXY_STRING       = 'ENV http_proxy "http://proxy-dmz.intel.com:911"\nENV https_proxy "http://proxy-dmz.intel.com:912"\n'
AZURE_DCAP             = "RUN env DEBIAN_FRONTEND=noninteractive apt-get install -y az-dcap-client\n"
DCAP_LIBRARY           = "\nRUN apt install -y libsgx-dcap-default-qpl libsgx-dcap-default-qpl-dev\nCOPY verifier/sgx_default_qcnl.conf  /etc/sgx_default_qcnl.conf\n"
DCAP_ORD_LIST          = ['start', 'azure_warning', 'runtime_args_text', 'runtime_variable_list', 'docker_flags', 'encrypted_files_path', 'encryption_key',
                            'attestation', 'signing_key_path', 'signing_key_password', 'end']
AZURE_ORD_LIST         = ['start', 'runtime_args_text', 'runtime_variable_list', 'docker_flags', 'encrypted_files_path', 'encryption_key',
                            'attestation', 'signing_key_path', 'signing_key_password', 'end']
UBUNTU_18_04           = "From ubuntu:18.04"
UBUNTU_20_04           = "From ubuntu:20.04"
LOGS                   = os.path.join(FRAMEWORK_PATH, "logs")
TEST_CONFIG_PATH       = os.path.join(FRAMEWORK_PATH, "test_config")
CONFIG_YAML            = "config.yaml.template"
GRAMINE_CLONE          = "RUN git clone --depth 1 --branch v1.4 https://github.com/gramineproject/gramine.git"
GSC_CLONE              = "git clone --depth 1 --branch v1.4-for-curated-apps https://github.com/gramineproject/gsc.git"
GRAMINE_DEPTH_STR      = "--depth 1 --branch v1.4 "
GSC_DEPTH_STR          = "--depth 1 --branch v1.4-for-curated-apps "
TF_EXAMPLE_PATH        = os.path.join(TFSERVING_HELPER_PATH, "serving/tensorflow_serving/example")
TF_IMAGE               = "gramine.azurecr.io:443/base_images/intel-optimized-tensorflow-serving-avx512-ubuntu18.04"
CURATION_SCRIPT        = os.path.join(ORIG_BASE_PATH, "util", "curation_script.sh")
MYSQL_TESTDB_PATH      = os.path.join(CURATED_APPS_PATH, "workloads/mysql/test_db")
MYSQL_INIT_FOLDER_PATH = os.path.join(MYSQL_TESTDB_PATH, "mysql")
MYSQL_CREATE_TESTDB_CMD = f"mkdir -p {MYSQL_TESTDB_PATH}"
MYSQL_INIT_DB_CMD      = f"docker run --rm --net=host --name init_test_db --user $(id -u):$(id -g) \
                            -v $PWD/workloads/mysql/test_db:/test_db \
                            -e MYSQL_ALLOW_EMPTY_PASSWORD=true -e MYSQL_DATABASE=test_db mysql:8.0.32-debian \
                            --datadir /test_db"
STOP_TEST_DB_CMD      = f"docker stop init_test_db"
MYSQL_TEST_ENCRYPTION_KEY    = f"dd if=/dev/urandom bs=16 count=1 > workloads/mysql/base_image_helper/encryption_key"

CLEANUP_ENCRYPTED_DB   = f"sudo rm -rf /var/run/test_db_encrypted && sudo rm -rf /var/run/model_encrypted"
MYSQL_ENCRYPT_DB_CMD         = f"sudo gramine-sgx-pf-crypt encrypt -w workloads/mysql/base_image_helper/encryption_key \
                            -i workloads/mysql/test_db -o /var/run/test_db_encrypted"
MYSQL_CLIENT_INSTALL_CMD = f"sudo apt-get -y install mysql-client"
MYSQL_INPUT_FILE       = "input.txt"
MYSQL_INPUT_TXT        = f"echo \"SELECT User FROM mysql.user;\\nexit\" >> {MYSQL_INPUT_FILE}"
MYSQL_CLIENT_CMD       = f"mysql -h 127.0.0.1 -uroot < {MYSQL_INPUT_FILE}"

MARIADB_TESTDB_PATH      = os.path.join(CURATED_APPS_PATH, "workloads/mariadb/test_db")
MARIADB_INIT_FOLDER_PATH = os.path.join(MARIADB_TESTDB_PATH, "mariadb")
MARIADB_CREATE_TESTDB_CMD = f"mkdir -p {MARIADB_TESTDB_PATH}"
MARIADB_INIT_DB_CMD      = f"docker run --rm --net=host --name init_test_db \
                            -v $PWD/workloads/mariadb/test_db:/test_db \
                            -e MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=true -e MARIADB_DATABASE=test_db mariadb:10.7 \
                            --datadir /test_db "
MARIADB_TEST_ENCRYPTION_KEY    = f"dd if=/dev/urandom bs=16 count=1 > workloads/mariadb/base_image_helper/encryption_key"
MARIADB_ENCRYPT_DB_CMD   = f"sudo gramine-sgx-pf-crypt encrypt -w workloads/mariadb/base_image_helper/encryption_key \
                            -i workloads/mariadb/test_db -o /var/run/test_db_encrypted"
MARIADB_CHMOD         = f"sudo chown -R $USER:$USER $PWD/workloads/mariadb/test_db"
MYSQL_TESTDB_VERIFY   = f"/usr/sbin/mysqld: ready for connections"
MARIADB_TESTDB_VERIFY = f"mariadbd: ready for connections"
OVMS_INIT_PATH        = os.path.join(CURATED_APPS_PATH, "workloads/openvino-model-server")
OVMS_TESTDB_PATH      = os.path.join(CURATED_APPS_PATH, "workloads/openvino-model-server/test_model")
OVMS_CREATE_TESTDB_CMD = f"mkdir -p {OVMS_TESTDB_PATH}"
OVMS_INIT_DB_CMD      = f"curl --create-dirs https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/face-detection-retail-0004/FP32/face-detection-retail-0004.xml https://storage.openvinotoolkit.org/repositories/open_model_zoo/2022.1/models_bin/2/face-detection-retail-0004/FP32/face-detection-retail-0004.bin \
                         -o workloads/openvino-model-server/test_model/1/face-detection-retail-0004.xml -o workloads/openvino-model-server/test_model/1/face-detection-retail-0004.bin"
OVMS_TEST_ENCRYPTION_KEY = f"dd if=/dev/urandom bs=16 count=1 > workloads/openvino-model-server/base_image_helper/encryption_key"
OVMS_ENCRYPT_DB_CMD   = f"sudo gramine-sgx-pf-crypt encrypt -w workloads/openvino-model-server/base_image_helper/encryption_key \
                        -i workloads/openvino-model-server/test_model -o /var/run/model_encrypted"
