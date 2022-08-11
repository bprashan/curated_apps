import os
from libs import utils
from data.constants import *

def run_redis_client():
    result = False
    redis_download_cmd = "wget https://download.redis.io/redis-stable.tar.gz"
    utils.run_subprocess(redis_download_cmd, CURATED_APPS_PATH)

    untar_cmd = "tar -zxvf redis-stable.tar.gz"
    utils.run_subprocess(untar_cmd, CURATED_APPS_PATH)

    utils.run_subprocess("make -j8", CURATED_APPS_PATH+"/redis-stable")

    if os.path.exists(os.path.join(CURATED_APPS_PATH,"redis-stable","src","redis-cli")):
        redis_cli_run_cmd = "./src/redis-cli ping"
        redis_output = utils.run_subprocess(redis_cli_run_cmd, CURATED_APPS_PATH+"/redis-stable")
        print(redis_output)
        if "PONG" in redis_output:
            result = True

    return result
