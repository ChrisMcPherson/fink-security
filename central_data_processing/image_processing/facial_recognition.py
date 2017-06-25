import face_recognition
import cv2

class FaceRecognition:

    def compare_face(self, unknown_face):
        new_face_encoding = face_recognition.face_encodings(unknown_face)[0]
        my_image = face_recognition.load_image_file("./test_images/face_training.jpg")
        my_face_encoding = face_recognition.face_encodings(my_image)[0]

        results = face_recognition.compare_faces([my_face_encoding], new_face_encoding)

        if results[0]:
            name = "Chris"

        # Draw a label with a name below the face
        #cv2.rectangle(unknown_face, (left, top), (right, bottom), (0, 0, 255), 2)
        #cv2.rectangle(unknown_face, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        #font = cv2.FONT_HERSHEY_DUPLEX
        #cv2.putText(unknown_face, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        cv2.putText(unknown_face, "Person: {}".format(name), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #cv2.putText(unknown_face, (10, unknown_face.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # Display the resulting image
        cv2.imshow('img', unknown_face)

        # Hit 'q' on the keyboard to quit!
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def add_known_face(self, face):
        pass

def main():
    recognized_faces = FaceRecognition()
    # load known faces for specific household
    # known faces will grow overtime, however, an initial training is still required
    known_people = []

    test_image = face_recognition.load_image_file("./test_images/face.jpg")
    recognized_faces.compare_face(test_image)

if __name__ == '__main__':
    main()