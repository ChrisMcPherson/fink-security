## Motion Detection Utility
This utility tests the basic motion detection functionality on a Raspberry Pi.

Install libraries with:
```sh
$ pip install kafka-python picamera imutils
```
The Raspberry pi should also be equipped with OpenCV. Follow this guide to get setup: 
http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/

### Instructions
1. SSH into your RaspberryPi through an interface that supports X11 (PUTTY on Windows has been tested to work with the X11 PUTTY functionality toggled on)

2. Modify the config file with preferences or run as is

3. Execute Python script:

```sh
$ python test_pi_surveillance.py --conf conf.json
```