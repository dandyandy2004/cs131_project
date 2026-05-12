import jetson.utils
from detect import detect_objects
from send import send_data

CAMERA_POSITION = "FRONT"

camera = jetson.utils.videoSource("csi://0")
display = jetson.utils.videoOutput("display://0")

print(f"{CAMERA_POSITION} camera started")

while display.IsStreaming():

    img = camera.Capture()

    if img is None:
        continue

    objects = detect_objects(img)

    print(f"\n[{CAMERA_POSITION} CAMERA]")

    for obj in objects:

        name, confidence = obj

        print(f"{name}: {confidence:.1f}%")

        if name in ["person", "car", "truck", "bus", "bicycle"]:
            print("WARNING: obstacle detected")

    send_data(objects)

    display.Render(img)

    display.SetStatus(
        f"{CAMERA_POSITION} Camera | Objects: {len(objects)}"
    )