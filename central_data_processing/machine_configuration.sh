#!/bin/bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libgtk-3-dev
sudo apt-get install libboost-all-dev
pip3 install scikit-image --user
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:george-edison55/cmake-3.x
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-dev
sudo apt-get purge cmake
sudo apt-get install cmake
git clone https://github.com/davisking/dlib.git
cd dlib
mkdir build; cd build; cmake .. -DDLIB_USE_CUDA=0 -DUSE_AVX_INSTRUCTIONS=1; cmake --build .
cd ..
sudo python3 setup.py install --yes USE_AVX_INSTRUCTIONS --no DLIB_USE_CUDA
pip3 install face_recognition --user
pip3 install kafka-python --user
pip3 install flask --user

