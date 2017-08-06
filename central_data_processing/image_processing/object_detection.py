from facial_recognition import FaceRecognition
import numpy as np
import cv2
from kafka import KafkaConsumer
import avro.schema
import avro.io
import io
import os
import argparse
import warnings
import json

def main():
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
    #Avro initialization 
    file_path = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.abspath(os.path.join(file_path,"..",".."
                ,"edge_data_collection"
                ,"image_motion_capture"
                ,"image_schema.avsc"))
    print(schema_path)
    with open(schema_path) as avro_schema_file:
        schema = avro.schema.Parse(avro_schema_file.read())

    if conf["test"]:
        img = cv2.imread(conf["test_image"])
        detect_bodies(body_cascade, img)
        detect_faces(face_cascade, img)
    else:
        # Connect to Kafka client and pass the topic we want to consume
        consumer = KafkaConsumer(conf['kafka_topic'], group_id=None, bootstrap_servers=[conf['kafka_client']]
                                        ,auto_offset_reset='earliest')
        for msg in consumer:
            bytes_reader = io.BytesIO(msg.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(schema)
            image = reader.read(decoder)
            img = cv2.imread(image['frame'])
            detect_bodies(body_cascade, img)
            detect_faces(face_cascade, img) # I had false here for some reason?

def detect_bodies(classifier, img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bodies = classifier.detectMultiScale(gray_img, 1.3, 5)
    if len(bodies) != 0:
        for (x,y,w,h) in bodies:
            body_crop = img[y:y+h, x:x+w]
            cv2.imshow('img', body_crop)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print('There were no bodies found')

def detect_faces(classifier, img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = classifier.detectMultiScale(gray_img, 1.3, 5)
    if len(faces) != 0:
        for (x,y,w,h) in faces:
            face_crop = img[y:y+h, x:x+w]
            cv2.imshow('img',face_crop)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # match face with known faces
            face_recognition = FaceRecognition()
            face_recognition.compare_face(face_crop)
    else:
        print('There were no faces found')

if __name__ == '__main__':
    main()





