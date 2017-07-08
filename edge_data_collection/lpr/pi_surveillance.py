# Andrew Burrage - Fink Security
# Motion Detection for License Plate Recognition
# Code based off example at http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
import avro.schema
import avro.io
from kafka import SimpleProducer, KafkaClient
from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")
args = vars(ap.parse_args())

warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None

# kafka initialization
kafka = KafkaClient(conf["kafka_client"])
producer = SimpleProducer(kafka)

# Avro initialization
avro_schema = avro.schema.Parse(open("lpr_schema.avsc").read())
house_id = 2
unit_id = 2

camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

print ("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
motionCounter = 0


for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array
    timestamp = datetime.datetime.now()
    text = "Unoccupied"

    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if avg is None:
        print ("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue

    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    for c in cnts:
        if cv2.contourArea(c) < conf["min_area"]:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        #cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    #cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    #cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    if text == "Occupied":
       motionCounter += 1

       if motionCounter >= conf["min_motion_frames"]:
           t = TempImage()
           cv2.imwrite(t.path, frame)
           motionCounter = 0
       ########## THIS IS WHERE I WILL EITHER SEND IMAGE TO CLOUD FOR LPR OR CALL ANOTHER SCRIPT TO RUN OPENALPR
           subprocess.call("./lpr.sh", shell=True)
           if conf["use_kafka"]:
               ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
               print("[UPLOAD] {}".format(ts))
               ret, png = img_str = cv2.imencode('.png',f.array)
               # write to Avro in byte format
               writer = avro.io.DatumWriter(avro_schema)
               bytes_writer = io.BytesIO()
               encoder = avro.io.BinaryEncoder(bytes_writer)
               ##### I need to convert the json file to bytes and put in function call below...
               writer.write({"frame": t.tobytes(), "timestamp": ts, "house": house_id, "unit": unit_id}, encoder)
         #t.cleanup()

    else:
        motionCounter = 0

    if conf["show_video"]:
       cv2.imshow("Security Feed", frame)
       key = cv2.waitKey(1) & 0xFF

       if key == ord("q"):
           break

    rawCapture.truncate(0)