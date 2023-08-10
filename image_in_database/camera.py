import cv2 as cv

# Use the default camera (index 0) to create the video capture object
cap = cv.VideoCapture(0)

# Check if the video capture object is opened successfully
if not cap.isOpened():
    print("Error: No camera found or unable to access the camera.")
else:
    while True:
        success, img = cap.read()

        # Check if the frame was read successfully
        if not success:
            print("Error: Unable to read a frame.")
            break

        cv.imshow("Image", img)

        if cv.waitKey(1) & 0xFF == 27:  # Press the 'Esc' key to exit the loop (ASCII value of 'Esc' is 27)
            break

    cap.release()
    cv.destroyAllWindows()
