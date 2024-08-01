#!/bin/bash
set -x #echo on
set +e

python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r client_requirements.txt

mkdir -p results
export no_proxy=intel.com,.intel.com,localhost,127.0.0.1

python3 face_detection.py --batch_size 1 --width 600 --height 400 --input_images_dir images --output_dir results --grpc_port 9000

deactivate
