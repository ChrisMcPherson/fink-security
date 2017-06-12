## Edge Motion Detection
Capture frames on an edge data collector (tested on a Raspberry Pi) and, where motion was detected, upload them to a Kafka queue for further processing.

Install libraries with:
```sh
$ pip install kafka-python picamera imutils
```
The Raspberry pi should also be equipped with OpenCV. Follow this guide to get setup: 
http://www.pyimagesearch.com/2016/04/18/install-guide-raspberry-pi-3-raspbian-jessie-opencv-3/

### Instructions
1. Load python script to each edge node that will be collecting image data

2. Modify the config file with preferences (kafka endpoint, frame rate, etc) or run as is

3. Execute Python script:

```sh
$ python pi_surveillance.py --conf conf.json
```