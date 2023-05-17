import cv2
import numpy as np
import mediapipe as mp
import serial

# Initialize an array to store the coordinates of circles
circles = np.zeros((4, 2), np.int16)
counter = 0

# Create instances of mediapipe modules
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Callback function for mouse events


def mousePoints(event, x, y, flags, params):
    global counter
    if event == cv2.EVENT_LBUTTONDOWN:
        circles[counter] = x, y
        counter += 1
        print(circles)


# Open video capture from camera
cap = cv2.VideoCapture(0)
address = "http://192.168.50.166:8080/video"
cap.open(address)

# Initialize serial port (COM5) and baudrate (9600)
ser = None
try:
    ser = serial.Serial('COM5', 9600)
except serial.SerialException as e:
    print(f"Failed to open serial port: {e}")
    exit(1)

# Set height and width for display
height, width = 1080, 1920

# Predefined circles for the region of interest
circles = [[369, 192], [1518, 192], [1518, 968], [369, 968]]

while True:
    # Read a frame from the video
    success, frame = cap.read()

    # Fullscreen the window
    cv2.namedWindow('Webcam', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        'Webcam', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Convert frame color space from BGR to RGB
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the pose detection
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        # Draw landmarks on the frame
        mpDraw.draw_landmarks(
            frame, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

        # Check the position of landmarks and perform actions
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = frame.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 2, (255, 0, 0), cv2.FILLED)

            # Check if the person is outside the predefined region
            if (
                (circles[0][0] > cx)
                | (circles[1][0] < cx)
                | (circles[0][1] > cy)
                | (circles[2][1] < cy)
            ):
                # Display warning message and send 'T' to serial port
                cv2.rectangle(frame, (0, int(height)),
                              (360, int(height) - 50), (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    "Baby Going Out...!",
                    (25, int(height) - 15),
                    cv2.FONT_HERSHEY_COMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )
                try:
                    ser.write('T'.encode())

                except serial.SerialException as e:
                    print(f"Failed to write to serial port: {e}")

            else:
                # Send 'F' to serial port indicating the person is safe
                try:
                    ser.write('F'.encode())

                except serial.SerialException as e:
                    print(f"Failed to write to serial port: {e}")

        # Draw lines and circles on the frame
        if counter == 4:
            color = (0, 0, 255)
            thickness = 3

            for i in range(1, 4):
                # Draw lines between the circles
                img = cv2.line(
                    frame, circles[i - 1], circles[i], color, thickness)

                if i == 3:
                    # Draw a closing line to complete the shape
                    img = cv2.line(
                        frame, circles[0], circles[i], color, thickness)

        # Draw circles on the frame
        for x in range(0, 4):
            cv2.circle(frame, (circles[x][0], circles[x]
                       [1]), 6, (0, 200, 255), cv2.FILLED)

        # Set position for the title
        position = ((int)(width / 2 - 460 / 2), (int)(43))

        # Draw a rectangle for the title
        cv2.rectangle(frame, (0, 0), (int(width), 60), (255, 255, 255), -1)

        # Add the title text
        cv2.putText(
            frame,  # numpy array on which text is written
            "SMART BABY SHEET",  # text
            position,  # position at which writing has to start
            cv2.FONT_HERSHEY_COMPLEX_SMALL,  # font family
            2,  # font size
            (56, 37, 7),  # font color
            2,  # font stroke
        )

        # Show the frame
        cv2.imshow("Webcam", frame)

        # Set mouse callback for selecting circles
        cv2.setMouseCallback("Webcam", mousePoints)

        # Check for key press to exit the program
        key = cv2.waitKey(1)
        if key == ord("q"):  # Press 'q' to exit
            break

# Release the video capture and close the windows
cap.release()
cv2.destroyAllWindows()

# Close the serial port
if ser:
    ser.close()
