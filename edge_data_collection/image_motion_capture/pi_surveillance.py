# USAGE
# python pi_surveillance.py --conf conf.json

# packages
import avro.schema
import avro.io
from kafka import SimpleProducer, KafkaClient
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import io
import warnings
import datetime
import imutils
import json
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to configuration file")
args = vars(ap.parse_args())

# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

# kafka initialization
kafka = KafkaClient(conf["kafka_client"])
producer = SimpleProducer(kafka)

# Avro initialization
avro_schema = avro.schema.Parse(open("image_schema.avsc").read())
house_id = 1
unit_id = 1

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
raw_capture = PiRGBArray(camera, size=tuple(conf["resolution"]))

# allow the camera to warmup and initialize
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
last_updated = datetime.datetime.now()
motion_counter = 0

# capture frames from the camera
for f in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	frame = f.array
	timestamp = datetime.datetime.now()
	status = "Unoccupied"

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the average frame is None, initialize it
	if avg is None:
		print("[INFO] starting background model...")
		avg = gray.copy().astype("float")
		raw_capture.truncate(0)
		continue

	# accumulate the weighted average between the frames then compute the difference between the current
	cv2.accumulateWeighted(gray, avg, 0.5)
	frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate to fill in holes, then find contours
	thresh = cv2.threshold(frame_delta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = contours[0] if imutils.is_cv2() else contours[1]

	# loop over the contours
	for c in contours:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < conf["min_area"]:
			continue

		status = "Occupied"

	# check to see if the room is occupied
	if status == "Occupied":
		# check to see if enough time has passed between uploads
		if (timestamp - last_updated).seconds >= conf["min_upload_seconds"]:
			# increment the motion counter
			motion_counter += 1
			# check to see if the number of frames with consistent motion is high enough
			if motion_counter >= conf["min_motion_frames"]:
				if conf["use_kafka"]:
					# upload unaltered frame
					ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
					print("[UPLOAD] {}".format(ts))
					ret, png = img_str = cv2.imencode('.png', f.array)
					# write out to Avro in byte format
					writer = avro.io.DatumWriter(avro_schema)
					bytes_writer = io.BytesIO()
					encoder = avro.io.BinaryEncoder(bytes_writer)
					writer.write({"frame": png.tobytes(), "timestamp": ts, "house": house_id, "unit": unit_id}, encoder)
					raw_bytes = bytes_writer.getvalue()
					#producer.send_messages(conf["kafka_topic"], png.tobytes())
					producer.send_messages(conf["kafka_topic"], raw_bytes)
				
				# update the last uploaded timestamp and reset the motion counter
				last_uploaded = timestamp
				motion_counter = 0

	# otherwise, the room is not occupied
	else:
		motion_counter = 0

	# clear the stream in preparation for the next frame
	raw_capture.truncate(0)