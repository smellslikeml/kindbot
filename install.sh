#!/bin/bash

echo 'Updating...'
sudo apt-get update -y
cd ~/
echo

echo 'Starting OpenCV installation...'
sudo apt-get install build-essential cmake pkg-config -y
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev -y
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt-get install libxvidcore-dev libx264-dev -y
sudo apt-get install libgtk2.0-dev -y
sudo apt-get install libatlas-base-dev gfortran -y
sudo apt-get install python2.7-dev python3-dev -y
cd ~/
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.0.0.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.0.0.zip
unzip opencv_contrib.zip
rm opencv.zip opencv_contrib.zip
echo 'Installing numpy dependency, this might take a while...'
sudo pip3 install numpy
echo 'Installing OpenCV now...'
cd ~/opencv-3.0.0/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.0.0/modules \
    -D BUILD_EXAMPLES=ON ..
echo 'Making OpenCV.. this will take approx. 9 hrs!'
make
sudo make install
sudo ldconfig
echo 'DONE installing OpenCV!'
echo


echo 'Starting TensorFlow installation...'
sudo apt-get install python3-pip python3-dev -y
sudo apt-get install libblas-dev liblapack-dev python-dev libatlas-base-dev gfortran python-setuptools -y
cd ~/
echo 'Installing TensorFlow now...'
wget http://ci.tensorflow.org/view/Nightly/job/nightly-pi-zero-python3/lastSuccessfulBuild/artifact/output-artifacts/tensorflow-1.6.0-cp34-none-any.whl
sudo pip3 install tensorflow-1.6.0-cp34-none-any.whl
echo 'DONE installing TensorFlow!'
echo

echo 'Installing darkflow'
sudo pip3 install Cython
git clone https://github.com/thtrieu/darkflow.git
cd darkflow
sed -i 's/self.offset = 16/self.offset = 20/g' /home/pi/darkflow/darkflow/utils/loader.py
python3 setup.py build_ext --inplace
sudo pip3 install .


echo 'DONE!'

