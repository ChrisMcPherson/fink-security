from kafka import KafkaConsumer
consumer = KafkaConsumer('security_images', group_id='view', bootstrap_servers=['52.90.213.141:9092'])
for msg in consumer:
    print(msg)