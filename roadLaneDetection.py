# Import the necessary packages
import numpy as np
import cv2


cap = cv2.VideoCapture(0)

# Crop the region of interest of the image
def crop_roi(img):
	# Define a blank matrix that matches the image height/width.
	mask = np.zeros_like(img)
	# Get the image size
	height = np.size(img, 0)
	width = np.size(img, 1)
	# Define the polygon of the region of interest
	vertices = [ (0, height), (width / 2, height / 2), (width, height) ]
	# Fill inside the polygon
	cv2.fillPoly(mask, np.array([vertices], np.int32), 255)
	# Returning the image only where mask pixels match
	masked_image = cv2.bitwise_and(img, mask)
	return masked_image


while(True):
	# Capture frame-by-frame
	ret, frame = cap.read()

	# Convert image from BGR to HSV
	gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# Crop the region of interest
	cropped_image = crop_roi(gray_img)

	# Create the mask to leave the white lines of the road
	mask = cv2.inRange(cropped_image, 200, 255)

	# Opening
	mask = cv2.erode(mask, None, iterations=1)
	mask = cv2.dilate(mask, None, iterations=1)
	# Closing
	mask = cv2.dilate(mask, None, iterations=1)
	mask = cv2.erode(mask, None, iterations=1)

	# A gaussian filter is applied 
	blurred = cv2.GaussianBlur(mask, (5, 5), 0)

	# Apply a canny edge detection
	canny_edges = cv2.Canny(blurred, 50, 150)

	# Use the Hough transform to find the road lines
	minLineLength = 100
	maxLineGap = 10
	lines = cv2.HoughLinesP(canny_edges, 1, np.pi/180, 100, minLineLength, maxLineGap)

	# Draw the lines into the image
	if lines is not None:
		for line in lines:
			for x1,y1,x2,y2 in line:
				cv2.line(frame, (x1, y1), (x2, y2), (0,255,0), 2)
	
	# Display the resulting frame
	cv2.imshow('frame', frame)
	cv2.imshow('mask', canny_edges)

	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()