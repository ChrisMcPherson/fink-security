from flask import Flask, Response
from kafka import KafkaConsumer
import avro.schema
import avro.io
import io

#connect to Kafka server and pass the topic we want to consume
consumer = KafkaConsumer('demo', group_id=None, bootstrap_servers=['52.90.213.141:9092']
                                    ,auto_offset_reset='earliest')

schema_path="../../edge_data_collection/image_motion_capture/image_schema.avsc"
schema = avro.schema.Parse(open(schema_path).read())

#Continuously listen to the connection and print messages as recieved
app = Flask(__name__)

@app.route('/')
def index():
    # return a multipart response
    return Response(kafkastream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
def kafkastream():
    for msg in consumer:
        bytes_reader = io.BytesIO(msg.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        image = reader.read(decoder)

        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + image['frame'] + b'\r\n\r\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)