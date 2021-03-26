# Import the necessary packages
import numpy as np
import cv2

# Define the color limits
redLowerLower = (0, 100, 140)
redLowerUpper = (10, 255, 255)
redUpperLower = (170, 100, 140)
redUpperUpper = (179, 255, 255)

cap = cv2.VideoCapture(0)


while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	# A gaussian filter is applied 
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)

	# Convert image from BGR to HSV
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# Create the mask
	mask = cv2.inRange(hsv, redLowerLower, redLowerUpper) + cv2.inRange(hsv, redUpperLower, redUpperUpper)
	# Opening
	mask = cv2.erode(mask, None, iterations=1)
	mask = cv2.dilate(mask, None, iterations=1)
	# Closing
	mask = cv2.dilate(mask, None, iterations=1)
	mask = cv2.erode(mask, None, iterations=1)

	# Find the mask contorus 
	im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# Delete the small contours
	contours = list(filter(lambda cnt: cv2.contourArea(cnt) > 1000, contours)) 

	# Calculate the position and the minimum enclosing circle
	approx, center, radius = [], [], []
	for cnt in contours:
		per = 0.01 * cv2.arcLength(cnt, True)
		approx.append(cv2.approxPolyDP(cnt, per, True))
		((x, y), rad) = cv2.minEnclosingCircle(cnt)
		center.append((int(x), int(y)))
		radius.append(int(rad))

	# Draw all info on the frame
	cv2.drawContours(frame, approx, -1, (255,0,0), 1)
	for (c, r) in zip(list(center), list(radius)):
		# Draw the minimun enclosing circle
		cv2.circle(frame, c, r, (0,255,0), 3)
		# Draw the center of the contour
		cv2.circle(frame, c, 3, (0,255,0), -1)
		# Draw the coordenates of the center
		cv2.putText(frame, ('X: ' + str(c[0])), ((c[0] - 35), (c[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
		cv2.putText(frame, ('Y: ' + str(c[1])), ((c[0] - 35), (c[1] + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)

	# Display the resulting frame
	cv2.imshow('frame', frame)
	cv2.imshow('mask', mask)

	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()