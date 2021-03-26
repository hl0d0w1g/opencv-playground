import cv2
import numpy as np
import time
import datetime

ALARM_TIMEOUT_MIN = 10  # Minutes
VIDEO_LENGHT = 50 # N frames

alarm_activated = True
last_alarm_time = None
motion = False
video_recording = False
frames_in_video = 0

cap = cv2.VideoCapture(0)

FRAME_WIDTH = int( cap.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int( cap.get( cv2.CAP_PROP_FRAME_HEIGHT))

while (cap.isOpened()):
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = [contour for contour in contours if cv2.contourArea(contour) > 900]
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)

        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if alarm_activated:
            
            alarm_time = time.time()
            if last_alarm_time is None:
                motion = True
                last_alarm_time = alarm_time
            elif ((alarm_time - last_alarm_time) / 60) > ALARM_TIMEOUT_MIN:
                motion = True
                last_alarm_time = alarm_time




    image = frame1.copy()
    cv2.imshow("feed", image)

    if motion:
        if not video_recording:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
            out = cv2.VideoWriter('recording ' + st + '.avi', fourcc, 10.0, (FRAME_WIDTH, FRAME_HEIGHT))
            video_recording = True

            out.write(image)
            frames_in_video += 1

            print('Video init')
        elif (frames_in_video > VIDEO_LENGHT):
            out.release() 
            print('Video saved')
            frames_in_video = 0
            motion = False
            video_recording = False

        else:
            out.write(image)
            frames_in_video += 1
            print('video', frames_in_video)

    frame1 = frame2
    ret, frame2 = cap.read()

    if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

cv2.destroyAllWindows()
cap.release()