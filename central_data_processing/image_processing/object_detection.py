import numpy as np
import cv2
from kafka import KafkaConsumer
import argparse
import warnings
import json

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to configuration file")
args = vars(ap.parse_args())

# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

# Load models
face_cascade = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier('./models/haarcascade_fullbody.xml')


def main():
    # kafka initialization
    if conf["test"]:
        img = cv2.imread(conf["test_image"])
        detect_bodies(img)
        detect_faces(img)
    else:
        # Connect to Kafka client and pass the topic we want to consume
        consumer = KafkaConsumer(conf['kafka_topic'], group_id=None, bootstrap_servers=[conf['kafka_client']]
                                        ,auto_offset_reset='earliest')
        for msg in consumer:
            img = cv2.imread(msg.value)
            detect_bodies(img)
            detect_faces(img)

def detect_bodies(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bodies = body_cascade.detectMultiScale(gray_img, 1.3, 5)
    if len(bodies) != 0:
        for (x,y,w,h) in bodies:
            body_crop = img[y:y+h, x:x+w]
            cv2.imshow('img', body_crop)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print('There were no bodies found')

def detect_faces(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)
    if len(faces) != 0:
        for (x,y,w,h) in faces:
            face_crop = img[y:y+h, x:x+w]
            cv2.imshow('img',face_crop)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print('There were no faces found')

if __name__ == '__main__':
    main()