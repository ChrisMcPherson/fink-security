import face_recognition
import cv2
import datetime
import os
from twilio.rest import Client
import cloudinary
import cloudinary.uploader
import cloudinary.api

class FaceRecognition:

    def compare_face(self, unknown_face, test):

        # Initialize Twilio and Cloudinary
        account_sid = os.environ['TWILIO_SID']
        auth_token = os.environ['TWILIO_TOKEN']
        twilio_client = Client(account_sid, auth_token)

        cloudinary.config( 
            cloud_name = 'dvrauboyr', 
            api_key = os.environ['CLOUDINARY_KEY'], 
            api_secret = os.environ['CLOUDINARY_SECRET'])

        # Face encoding
        new_face_encoding = face_recognition.face_encodings(unknown_face)[0]
        my_image = face_recognition.load_image_file("./test_images/face_training.jpg")
        my_face_encoding = face_recognition.face_encodings(my_image)[0]

        results = face_recognition.compare_faces([my_face_encoding], new_face_encoding)

        if results[0]:
            name = "Chris"

            cv2.putText(unknown_face, "Person: {}".format(name), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            if test:
                # Display the resulting image
                cv2.imshow('img', unknown_face)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                # Load image
                timestamp = datetime.datetime.now()
                image_file = "test_image_{}.jpg".format(timestamp)
                cv2.imwrite(image_file, unknown_face, [cv2.IMWRITE_JPEG_QUALITY, 50])
                response = cloudinary.uploader.upload(image_file)
                image_url = response.get("url")
                os.remove(image_file)
                # Send message
                twilio_client.messages.create(
                    to="+13307803553",
                    from_="+12164782236",
                    body="{} just entered your home".format(name),
                    media_url=image_url)


    def add_known_face(self, face):
        pass

def main():
    recognized_faces = FaceRecognition()
    # load known faces for specific household
    # known faces will grow overtime, however, an initial training is still required
    known_people = []

    test_image = face_recognition.load_image_file("./test_images/face.jpg")
    recognized_faces.compare_face(test_image, False)

if __name__ == '__main__':
    main()