## Kafka Utilities
This set of utilities test the basic functionality of the Kafka Queue.

Install libraries with:
```sh
$ pip install kafka-python flask
```

## kafka-image-web-service
This utility tests the consumption of images (in byte format) from a Kafka queue by starting a simple webserver to display the images as they are uploaded to the queue.

#### Instructions
1. The "test_images" Kafka queue already contains some test images. However, this utility was intended to be used to verify that current images of detected motion are uploaded correctly to the Kafka Queue. Configure and run the "edge_data_collection/image_motion_capture/pi_surveillance.py" python script on the RaspberryPi to begin sending images to the Kafka Queue (check that the Kafka topic is configured to be the same)

2. Run webserver:

```sh
$ python kafka_image_web_service.py
```

3. Navigate to *localhost:5000* to view the ~~real-time~~ stream of images that were captured when motion was detected.

