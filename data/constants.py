import os

FRAMEWORK_PATH         = os.getcwd()
REPO_PATH              = os.path.join(FRAMEWORK_PATH, "contrib_repo")
ORIG_CURATED_PATH      = os.path.join(FRAMEWORK_PATH, "orig_contrib_repo")
CONTRIB_GIT_CMD        = "git clone https://github.com/aneessahib/contrib.git orig_contrib_repo"
GIT_CHECKOUT_CMD       = "git checkout aneessahib/gsc_curation"
CURATED_PATH           = "GSC-Image-Curation"
CURATED_APPS_PATH      = os.path.join(REPO_PATH, CURATED_PATH)
VERIFIER_SERVICE_PATH  = os.path.join(CURATED_APPS_PATH, "verifier_image")
VERIFIER_DOCKERFILE    = os.path.join(ORIG_CURATED_PATH, CURATED_PATH, "verifier_image/verifier.dockerfile")
PYTORCH_PLAIN_PATH     = os.path.join(CURATED_APPS_PATH, "pytorch", "pytorch_with_plain_text_files")
PYTORCH_ENCRYPTED_PATH = os.path.join(CURATED_APPS_PATH, "pytorch", "pytorch_with_encrypted_files")
BASH_PATH              = os.path.join(CURATED_APPS_PATH, "bash")
PYTORCH_ENCRYPTION     = "pytorch-encryption"
PYTORCH_PLAIN          = "pytorch-plain"
BASH_TEST              = "bash-test"
SCREEN_LIST            = ["home_page", "signing_page", "attestation_page", "verifier_page", "runtime_page", "environment_page",
                          "encrypted_page", "final_page"]