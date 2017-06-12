## Central Image Processing
With various edge nodes producing data and loading it to a Kafka queue, this acts as the consumer and heavy lifter for deeper processing of data off of the image Kafka topics. It will handle object detection (is there a body, face, or vehicle in the frame?) and recognition (do we recognize the face or vehicle?).

#### Instructions
1. Adjust the conf.json file for testing detection and recognition of specific photos or continuous consumption of images off of a specified Kafka image topic. 

2. Run script:

```sh
$ python object_detection.py --conf conf.json
```


