import os
from libs import utils
from data.constants import *

def run_redis_client():
    result = False
    redis_output = utils.run_subprocess("docker run -it --net=host --rm redis redis-cli ping")
    print(redis_output)
    if "PONG" in redis_output:
        result = True

    return result
