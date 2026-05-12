import jetson.inference
import jetson.utils

# load object detection model
net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

def detect_objects(img):

    detections = net.Detect(img)

    detected = []

    for detection in detections:

        class_name = net.GetClassDesc(detection.ClassID)
        confidence = detection.Confidence * 100

        detected.append((class_name, confidence))

    return detected