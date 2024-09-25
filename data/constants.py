import os

FRAMEWORK_PATH              = os.getcwd()
REPO_PATH                   = os.path.join(FRAMEWORK_PATH, "contrib_repo")
ORIG_CURATED_PATH           = os.path.join(FRAMEWORK_PATH, "orig_contrib_repo")
CONTRIB_GIT_REPO            = os.environ.get("contrib_repo")
if not CONTRIB_GIT_REPO:
    CONTRIB_GIT_REPO        = "https://github.com/gramineproject/contrib.git"
CONTRIB_GIT_CMD             = f"git clone {CONTRIB_GIT_REPO} orig_contrib_repo"
CONTRIB_BRANCH              = os.environ.get("contrib_branch")
if not CONTRIB_BRANCH:
    CONTRIB_BRANCH          = "master"
GIT_CHECKOUT_CMD            = f"git checkout {CONTRIB_BRANCH}"
REBASE_CONTRIB_GIT_REPO     = os.environ.get("rebase_contrib_repo")
REBASE_CONTRIB_BRANCH       = os.environ.get("rebase_contrib_branch")
REBASE_GIT_REPO_CMD         = f"git remote add repo_rebase {REBASE_CONTRIB_GIT_REPO}"
FETCH_REBASE_REPO_CMD       = f"git fetch repo_rebase"
REBASE_BRANCH_CMD           = f"git rebase repo_rebase/{REBASE_CONTRIB_BRANCH}"
CURATED_PATH                = "Intel-Confidential-Compute-for-X"
CURATED_APPS_PATH           = os.path.join(REPO_PATH, CURATED_PATH)
WORKLOADS_PATH              = os.path.join(CURATED_APPS_PATH, "workloads")
COMMANDS_TXT_PATH           = os.path.join(CURATED_APPS_PATH, "commands.txt")
VERIFIER_SERVICE_PATH       = os.path.join(CURATED_APPS_PATH, "verifier")
VERIFIER_TEMPLATE           = "verifier.dockerfile.template"
ORIG_BASE_PATH              = os.path.join(ORIG_CURATED_PATH, CURATED_PATH)
VERIFIER_DOCKERFILE         = os.path.join(ORIG_BASE_PATH, "verifier", VERIFIER_TEMPLATE)
PYTORCH_HELPER_PATH         = os.path.join(WORKLOADS_PATH, "pytorch", "base_image_helper")
PYTORCH_HELPER_CMD          = f"bash {PYTORCH_HELPER_PATH}/helper.sh"
SKLEARN_HELPER_PATH         = os.path.join(WORKLOADS_PATH, "sklearn", "base_image_helper")
SKLEARN_HELPER_CMD          = f"bash {SKLEARN_HELPER_PATH}/helper.sh"
TFSERVING_HELPER_PATH       = os.path.join(WORKLOADS_PATH, "tensorflow-serving", "base_image_helper")
TFSERVING_HELPER_CMD        = f"bash {TFSERVING_HELPER_PATH}/helper.sh"
BASH_PATH                   = os.path.join(WORKLOADS_PATH, "bash")
SCREEN_LIST                 = ["home_page", "runtime_page", "environment_page", "flags_page", "encrypted_page", "encryption_key_page",
                            "attestation_page", "signing_page", "signing_key_password", "verifier_page", "final_page"]
BASH_DOCKERFILE             = os.path.join(WORKLOADS_PATH, "bash", "Dockerfile")
BASH_GSC_DOCKERFILE         = os.path.join(WORKLOADS_PATH, "bash", "bash-gsc.dockerfile.template")
ENV_PROXY_STRING            = 'ENV http_proxy "http://proxy-dmz.intel.com:911"\nENV https_proxy "http://proxy-dmz.intel.com:912"\n'
INPUT_ORD_LIST              = ['start', 'runtime_args_text', 'runtime_variable_list', 'docker_flags', 'encrypted_files_path', 'encryption_key', 
                            'attestation', 'signing_key_path', 'signing_key_password', 'end']
UBUNTU_18_04                = "From ubuntu:18.04"
UBUNTU_20_04                = "From ubuntu:20.04"
LOGS                        = os.path.join(FRAMEWORK_PATH, "logs")
TEST_CONFIG_PATH            = os.path.join(FRAMEWORK_PATH, "test_config")
CONFIG_YAML                 = "config.yaml.template"
GIT_CLONE                   = "git clone"
GRAMINE_MAIN_REPO           = "https://github.com/gramineproject/gramine.git"
GSC_MAIN_REPO               = "https://github.com/gramineproject/gsc.git"
TF_EXAMPLE_PATH             = os.path.join(TFSERVING_HELPER_PATH, "serving/tensorflow_serving/example")
TF_IMAGE                    = "gramine.azurecr.io:443/base_images/intel-optimized-tensorflow-serving-avx512-ubuntu18.04"
CURATION_SCRIPT             = os.path.join(ORIG_BASE_PATH, "util", "curation_script.sh")
DB_MOUNT                    = "sudo mkdir -p /mnt/tmpfs && sudo mount -t tmpfs tmpfs /mnt/tmpfs && mkdir -p "
MYSQL_TESTDB_PATH           = "workloads/mysql/test_db"
MYSQL_ENC_PATH              = "/var/run/test_db_encrypted"
MYSQL_INIT_DB_CMD           = f"docker run --rm --net=host --name init_test_db --user $(id -u):$(id -g) \
                            -v $PWD/workloads/mysql/test_db:/test_db \
                            -e MYSQL_ALLOW_EMPTY_PASSWORD=true -e MYSQL_DATABASE=test_db mysql:8.0.35-debian \
                            --datadir /test_db"
STOP_TEST_DB_CMD            = "docker stop init_test_db"
VENV_PACKAGE                = "python3.8-venv"
MYSQL_CLIENT                = "mysql-client"
APT_INSTALL                 = "sudo apt-get install -y "
GRAMINE                     = "gramine"
MYSQL_INPUT_FILE            = "input.txt"
MYSQL_INPUT_TXT             = f"echo \"SELECT User FROM mysql.user;\\nexit\" >> {MYSQL_INPUT_FILE}"
MYSQL_CURR_VERSION          = "mysql:8.0.35-debian"
MARIADB_CURR_VERSION        = "mariadb:11.0.3-jammy"
MYSQL_CLIENT_CMD            = "mysql -h 127.0.0.1 -uroot "
MARIADB_TESTDB_PATH         = "workloads/mariadb/test_db"
MARIADB_ENC_PATH            = "/mnt/tmpfs/test_db_encrypted"
MARIADB_LOGS                = "mariadb.log"
MARIADB_INIT_DB_CMD         = f"docker run --rm --net=host --name init_test_db \
                            -v $PWD/workloads/mariadb/test_db:/test_db \
                            -e MARIADB_RANDOM_ROOT_PASSWORD=yes -e MARIADB_DATABASE=test_db mariadb:11.0.3-jammy \
                            --datadir /test_db | tee {MARIADB_LOGS}"
MARIADB_CHMOD               = f"sudo chown -R $USER:$USER $PWD/workloads/mariadb/test_db"
MYSQL_TESTDB_VERIFY         = "/usr/sbin/mysqld: ready for connections"
MARIADB_TESTDB_VERIFY       = "mariadbd: ready for connections"
OVMS_INIT_PATH              = os.path.join(CURATED_APPS_PATH, "workloads/openvino-model-server")
OVMS_TESTDB_PATH            = "workloads/openvino-model-server/models"
OVMS_ENC_PATH               = "/mnt/tmpfs/model_encrypted"
OVMS_INIT_DB_CMD            = f"curl --create-dirs https://storage.openvinotoolkit.org/repositories/open_model_zoo/2023.0/models_bin/1/face-detection-retail-0004/FP32/face-detection-retail-0004.xml https://storage.openvinotoolkit.org/repositories/open_model_zoo/2023.0/models_bin/1/face-detection-retail-0004/FP32/face-detection-retail-0004.bin \
                         -o {OVMS_TESTDB_PATH}/1/face-detection-retail-0004.xml -o {OVMS_TESTDB_PATH}/1/face-detection-retail-0004.bin"
OVMS                        = "openvino-model-server"
BASELINE_APP_VERSION        = {"redis": "7.0.11", "mysql": "8.0.36-1debian11", "mariadb": "11.3.2", "openvino-model-server": "2024.3.0e33a366b", \
                               "pytorch": "2.2.1", "sklearn": "c0647ca260ebca3acf34b944ce1ea944522382901d1a8a0841af4799366bb326",
                               "memcached": "1.6.14"}
PYTORCH_UPDATE_APP_VERSION  = f"sed -i 's\\2.0.1-cuda11.7-cudnn8-runtime\\latest\\g' Dockerfile"
SKLEARN_UPDATE_APP_VERSION  = f"sed -i 's\\scikit-learn-2023.1.1-xgboost-1.7.5-pip-base\\latest\\g' Dockerfile"
MYSQL_PORT                  = 3306
MARIADB_PORT                = 3306
OVMS_PORT                   = 9000
TFSERVING_PORT              = 8500
