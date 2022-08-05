import os

REPO_PATH             = os.path.join(os.getcwd(), "contrib_repo")
ORIG_CURATED_PATH     = os.path.join(os.getcwd(), "orig_contrib_repo")
CONTRIB_GIT_CMD       = "git clone https://github.com/veenasai2/contrib.git orig_contrib_repo"
GIT_CHECKOUT_CMD      = "git checkout gsc_image_curation"
CURATED_PATH          = "Examples/gsc_image_curation"
CURATED_APPS_PATH     = os.path.join(REPO_PATH, CURATED_PATH)
VERIFIER_SERVICE_PATH = os.path.join(CURATED_APPS_PATH, "verifier_image")
VERIFIER_DOCKERFILE   = os.path.join(ORIG_CURATED_PATH, CURATED_PATH, "verifier_image/verifier.dockerfile")