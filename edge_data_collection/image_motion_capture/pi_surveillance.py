# USAGE
# python pi_surveillance.py --conf conf.json

# pacakages
from pyimagesearch.tempimage import TempImage
from kafka import SimpleProducer, KafkaClient
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
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
#client = None

# kafka initialization
kafka = KafkaClient(conf["kafka_client"])
producer = SimpleProducer(kafka)

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
	text = "Unoccupied"

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

		# compute the bounding box for the contour, draw it on the frame, and update the text
		#(x, y, w, h) = cv2.boundingRect(c)
		#cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"

	# draw the text and timestamp on the frame
	#ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	#cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		#cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	#cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		#0.35, (0, 0, 255), 1)

	# check to see if the room is occupied
	if text == "Occupied":
		# check to see if enough time has passed between uploads
		if (timestamp - last_updated).seconds >= conf["min_upload_seconds"]:
			# increment the motion counter
			motion_counter += 1

			# check to see if the number of frames with consistent motion is high enough
			if motion_counter >= conf["min_motion_frames"]:
				if conf["use_kafka"]:
					# write the image to temporary file
					#t = TempImage()
					#cv2.imwrite(t.path, frame)

					# upload the image to Dropbox and cleanup the tempory image
					#path = "{base_path}/{timestamp}.jpg".format(
						#base_path=conf["dropbox_base_path"], timestamp=ts)
					#client.put_file(path, open(t.path, "rb"))
					#t.cleanup()
					
					# upload unaltered frame
					print("[UPLOAD] {}".format(ts))
					png = img_str = cv2.imencode('.png', f)
					producer.send_messages(conf["kafka_topic"], png.tobytes())
				
				# update the last uploaded timestamp and reset the motion counter
				last_uploaded = timestamp
				motion_counter = 0

	# otherwise, the room is not occupied
	else:
		motion_counter = 0

	# check to see if the frames should be displayed to screen
	if conf["show_video"]:
		# display the security feed
		cv2.imshow("Security Feed", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key is pressed, break from the lop
		if key == ord("q"):
			break

	# clear the stream in preparation for the next frame
	raw_capture.truncate(0)