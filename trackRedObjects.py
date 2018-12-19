# import the necessary packages
import numpy as np
import cv2


redLowerLower = (0, 100, 140)
redLowerUpper = (10, 255, 255)
redUpperLower = (170, 100, 140)
redUpperUpper = (179, 255, 255)
cap = cv2.VideoCapture(0)

while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	mask = cv2.inRange(hsv, redLowerLower, redLowerUpper) + cv2.inRange(hsv, redUpperLower, redUpperUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# Display the resulting frame
	cv2.imshow('frame', frame)
	cv2.imshow('mask', mask)

	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()