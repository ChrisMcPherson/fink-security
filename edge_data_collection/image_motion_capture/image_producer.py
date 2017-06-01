import time
import picamera
from kafka import SimpleProducer, KafkaClient
# connect to Kafka
kafka = KafkaClient('52.90.213.141:9092')
producer = SimpleProducer(kafka)
topic = 'security_images'

# initialize camera
camera = picamera.PiCamera()

def photo_emitter(image):
    print('Taking photo')
    image = take_photo()
    print(' emitting.....')

    # Convert the image to bytes and send to kafka
    producer.send_messages(topic, jpeg.tobytes())
    # To reduce CPU usage create sleep time of 0.2sec  
    time.sleep(0.2)
    print('done emitting')

def take_photo():
    camera.capture('image.jpg')

if __name__ == '__main__':
    photo_emitter()