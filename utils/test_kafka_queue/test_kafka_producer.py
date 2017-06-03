from kafka import KafkaProducer
from kafka import SimpleProducer, KafkaClient

kafka = KafkaClient('52.90.213.141:9092')
producer = SimpleProducer(kafka)
topic = 'security_images'
producer.send_messages(topic, b"spam")