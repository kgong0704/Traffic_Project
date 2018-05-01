# import the necessary packages
import argparse
import cv2
from tkinter import Tk, filedialog
import numpy as np
import base64
import os
# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
count = 0
refPt = []
 # true if mouse is pressed

def region_select(ip):

	def click_pick_region(event, x, y, flags, param):
		# grab references to the global variables
		global refPt, count
		drawing = False
		ix,iy = -1,-1
		if event == cv2.EVENT_LBUTTONDOWN:
			drawing = True
			ix,iy = x,y

		# check to see if the left mouse button was released

		elif event == cv2.EVENT_LBUTTONUP:
			drawing = False
			cv2.circle(image,(x,y),5,(0,0,255),-1)
			cv2.imshow("click to pick RoI", image)
			# record the ending (x, y) coordinates and indicate that
			# the cropping operation is finished
			if count == 0:
				refPt = [(x, y)]
				count+=1
			elif count < 4:
				refPt.append((x, y))
				count+=1


	def sort_points():
		global refPt
		sorted_refPt = [];sorted_refPt_right = []
		refPt = sorted(refPt)
		sorted_refPt.append(refPt[0]); sorted_refPt.append(refPt[1])
		sorted_refPt = sorted(sorted_refPt, key=lambda x: x[1])


		sorted_refPt_right.append(refPt[2]); sorted_refPt_right.append(refPt[3])
		sorted_refPt_right = sorted(sorted_refPt_right, key=lambda x: x[1], reverse=True)

		sorted_refPt.append(sorted_refPt_right[0]); sorted_refPt.append(sorted_refPt_right[1])

		return sorted_refPt


	def mask_image(file_path):
		image = cv2.imread(file_path, -1)
		mask = np.zeros(image.shape, dtype=np.uint8)
		sorted_refPt = sort_points()
		roi_corners = np.array([sorted_refPt], dtype=np.int32)
		channel_count = image.shape[2]  # i.e. 3 or 4 depending on your image
		ignore_mask_color = (255,)*channel_count
		cv2.fillPoly(mask, roi_corners, ignore_mask_color)
		masked_image = cv2.bitwise_and(image, mask)

		return masked_image

	def roi_image_filename(ip):
		Camera_path = os.getcwd() + '/Cameras/' + ip
		for File in os.listdir(Camera_path):
			# print(File)
		    if File.endswith('.jpg'):
			    return Camera_path + '/' + File

	filename = roi_image_filename(ip)
	# load the image, clone it, and setup the mouse callback function
	image = cv2.imread(filename)
	clone = image.copy()
	cv2.namedWindow("click to pick RoI")
	cv2.setMouseCallback("click to pick RoI", click_pick_region)
	# keep looping until the 'q' key is pressed
	while True:
		# display the image and wait for a keypress
		cv2.imshow("click to pick RoI", image)
		key = cv2.waitKey(1) & 0xFF

		# if the 'c' key is pressed, break from the loop
		if count == 4:
			cv2.destroyAllWindows()
			break
	encoded = mask_image(filename)
	return refPt, encoded