#!/bin/bash

echo "🔧 Fixing Python 3.12 venv setup on remote server..."

# Commands to run on the remote server to fix venv issues

cat << 'EOF'
# Run these commands on your remote server (yp-us-lg1):

# 1. Install python3.12-venv package
sudo apt update
sudo apt install python3.12-venv python3.12-dev python3.12-distutils

# 2. Alternative: Use virtualenv instead
pip3.12 install virtualenv
virtualenv -p python3.12 venv

# 3. Or create venv without pip initially, then install pip manually
python3.12 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python

# 4. If all else fails, use conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda create -n dr-web python=3.12
conda activate dr-web

# Once venv is working, install requirements:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers peft bitsandbytes accelerate datasets trl

EOF

echo "✅ Created fix_venv_setup.sh with commands to run on remote server"