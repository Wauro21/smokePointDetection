import cv2
import numpy as np
from progress.bar import Bar
import csv
import math
from processing_options import argsHandler
import os
from utils import verbosePrint, getConnectedComponents, heightBox
from matplotlib import pyplot as plt

# Default Values
MAX_PIXEL_VALUE = 255
MAX_CENTROID_TOLERANCE = 10 #px, converted from the 1mm by authors
DER_LOW_BOUND = 2e-5
SP_THRESHOLD = 1 #px, converted from the 0,1mm by authors

# Drawing values
CENTROID_RADIUS = 10


def smokepoint(args):
	# Load the data (video or folder)
	media = cv2.VideoCapture(args.Input)
	n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
	# Set threshold for core and countour
	core_threshold_value = round(MAX_PIXEL_VALUE*args.ThresholdCore/100)
	contour_threshold_value = round(MAX_PIXEL_VALUE*args.ThresholdContour/100)

	verbosePrint(args.Verbose,"[INFO] The threshold values are:\n\tCore: {}\n\tContour: {}".format(core_threshold_value,contour_threshold_value))

	if args.Verbose:
		bar = Bar('Processing', max=n_frames)
	else:
		bar = None

	if(args.Display):
		cv2.namedWindow("input", cv2.WINDOW_NORMAL)

	h = []
	H = []
	first_frame_flag = True
	reference_centroid_x = -float('inf')
	reference_centroid_y = -float('inf')
	invalid_frame_counter = 0
	# Perform frame by frame processing
	while media.isOpened():
		ret, frame = media.read()
		if not ret:
			verbosePrint(args.Verbose, "[INFO] End of stream, processing is done")
			break

		# -> Convert to grayscale
		gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# -> Apply core and contour umbrals
		ret, core_thresh = cv2.threshold(gray_frame, core_threshold_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)
		ret, contour_thresh = cv2.threshold(gray_frame, contour_threshold_value, MAX_PIXEL_VALUE, cv2.THRESH_BINARY)

		# -> From connected components, get stats
		core_components = getConnectedComponents(core_thresh,4)
		contour_components = getConnectedComponents(contour_thresh,4)

		# -> Get heights and centroid of the first frame
		contour_height = contour_components['h']
		# Consider that (0,0) is top left corner
		tip_height = core_components['y'] - contour_components['y']

		if(args.Boxes):
			heightBox(frame, core_components,'r')
			heightBox(frame, contour_components,'g')


		if(first_frame_flag):
			reference_centroid_x = contour_components['cX']
			reference_centroid_y = contour_components['cY']
			first_frame_flag = False
			continue

		# Draw reference centroid and frame centroid [TO-DO:ARGUMENT?]
		cv2.circle(frame, (int(reference_centroid_x), int(reference_centroid_y)), CENTROID_RADIUS, (255,0,255),-1)
		cv2.circle(frame, (int(contour_components['cX']),int(contour_components['cY'])), CENTROID_RADIUS, (255,0,0),-1)

		centroid_diff = abs(contour_components['cX']-reference_centroid_x)

		# Check if frame is not valid
		if(centroid_diff > MAX_CENTROID_TOLERANCE):
			invalid_frame_counter +=1
			verbosePrint(args.Verbose, "Invalid Frame {}".format(invalid_frame_counter))
			continue
		# If valid, get height data
		h.append(contour_height)
		H.append(tip_height)

		if(bar):
			bar.next()

		if(args.Display):
			cv2.imshow('input', frame)
			if cv2.waitKey(1) == ord('q'):
				break

	 # End of media reading

	if(bar):
		bar.finish()
	media.release()

	# -> Fit a 10th order poly
	tenth_poly = np.polyfit(h, H, 10)

	# -> Derivative of the 10th poly
	der_poly = np.polyder(tenth_poly,2)

	# -> Get linear region
	linear_interval_flag = True
	linear_region_start = -float('inf')
	linear_region_points = {}

	for flame_pos, flame_height in enumerate(h):
		eval = abs(np.polyval(der_poly, flame_height))
		if(eval <= DER_LOW_BOUND):
			linear_region_points[flame_height] = np.polyval(tenth_poly, flame_height)
			if linear_interval_flag:
				linear_region_start = flame_pos
				print('valor primer valor zona lineal {}'.format(h[linear_region_start]))
				linear_interval_flag = False
	print("inicio region lineal {}".format(linear_region_start))
	# Linear regresion for points of region
	linear_poly = np.polyfit(list(linear_region_points.keys()),list( linear_region_points.values()),1)


	# -> Get first value over the linear region
	# Save coordinates of the point
	sp_height = -float('inf')
	sp_Height = -float('inf')
	for flame_pos in range(linear_region_start, len(h)):
		flame_height = h[flame_pos]
		poly_H_val = np.polyval(tenth_poly, flame_height)
		poly_linear_val = np.polyval(linear_poly, flame_height)
		distance = poly_H_val - poly_linear_val
		print(distance)
		if(distance > SP_THRESHOLD):
			sp_height = flame_height
			sp_Height = poly_H_val
			break





	# Remove after debugging
	debug_plot = plt.figure()
	plt.subplot(2,1,1)
	# Plot raw data
	plt.scatter(h,H,color='b', label='Raw height data')
	# Plot poly
	low_bound = math.floor(min(h))
	upp_bound = math.ceil(max(h))
	samples = len(h)
	show_heights = np.linspace(low_bound, upp_bound, samples)
	show_poly_val = np.polyval(tenth_poly, show_heights)
	plt.plot(show_heights, show_poly_val,'r',label='Tenth order poly')
	# Plot raw linear data
	plt.scatter(list(linear_region_points.keys()), list(linear_region_points.values()),color='g',label='Raw linear points')
	# Plot linear poly
	linear_h = list(linear_region_points.keys())
	show_linear_poly = np.polyval(linear_poly, linear_h)
	plt.plot(linear_h, show_linear_poly, color='y', label='Linear Fit')
	# Plot SP
	plt.scatter(sp_height, sp_Height, s=50, color='m', label='Smoke Point')
	plt.xlabel('Flame height px')
	plt.ylabel('Flame Tip height px')
	plt.grid()
	plt.legend()
	plt.show()







if __name__ == '__main__':
	args = argsHandler()
	smokepoint(args)
