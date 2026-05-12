import jetson.utils

# camera input
camera = jetson.utils.videoSource("csi://0")

# display output
display = jetson.utils.videoOutput("display://0")

print("Camera started")

while display.IsStreaming():

    img = camera.Capture()

    if img is None:
        continue

    display.Render(img)

    display.SetStatus("Live Camera Feed")