import cv2
import numpy as np
from progress.bar import Bar
import csv
import math
from processing_options import argsHandler
import os
from utils import verbosePrint, getConnectedComponents, heightBox, resultPlotting, dataLoader
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('tkAgg')
# Default Values
MAX_PIXEL_VALUE = 255
MAX_CENTROID_TOLERANCE = 10 #px, converted from the 1mm by authors
#DER_LOW_BOUND = 2e-5
SP_THRESHOLD = 1 #px, converted from the 0,1mm by authors

# Drawing values
CENTROID_RADIUS = 10

# Fig save padding
FIG_PADDING = 200 #px

TARGET_SP = 22.7
SP_TOL = 0.25
DELTA = 1


def px_2_mm(px_val):
	mm = (0.1038*px_val) + 3.55
	return mm


def smokepoint(args):
	# Check folder for output data
	out_path = args.runName
	if not(os.path.isdir(out_path)):
		os.mkdir(out_path)


	out_frame_folder = os.path.join(out_path,'frames')
	if not(os.path.isdir(out_frame_folder)):
		os.mkdir(out_frame_folder)

	# Load the data (video or folder)
	error = float('inf')
	core_por = 2.5
	contour_por = 1.5


	while(error > SP_TOL):
		parsed = dataLoader(args.Input)
		media = cv2.VideoCapture(parsed,0)
		n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
		width = int(media.get(cv2.CAP_PROP_FRAME_WIDTH))
		height = int(media.get(cv2.CAP_PROP_FRAME_HEIGHT))
		# Set threshold for core and countour
		core_threshold_value = round(MAX_PIXEL_VALUE*core_por/100)
		contour_threshold_value = round(MAX_PIXEL_VALUE*contour_por/100)

		save_cut = height//2 + 100

		h = []
		H = []
		first_frame_flag = True
		reference_centroid_x = -float('inf')
		reference_centroid_y = -float('inf')
		invalid_frame_counter = 0
		frame_counter = 0
		# Perform frame by frame processing
		while media.isOpened():
			ret, frame = media.read()
			if not ret:
				break
			frame_counter += 1

			# -> Check if cutting the frame is needed
			if(args.cut):
				cut = args.cut//2
				center_line = width//2
				frame = frame[:,center_line-cut:center_line+cut]

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

			if(first_frame_flag):
				reference_centroid_x = contour_components['cX']
				reference_centroid_y = contour_components['cY']
				first_frame_flag = False
				# Manually add the values of h and H, before continuing
				h.append(contour_height)
				H.append(tip_height)
				continue

			# Draw reference centroid and frame centroid [TO-DO:ARGUMENT?]

			centroid_diff = abs(contour_components['cX']-reference_centroid_x)

			# Check if frame is not valid
			if(centroid_diff > MAX_CENTROID_TOLERANCE):
				invalid_frame_counter +=1
				continue
			# If valid, get height data
			h.append(contour_height)
			H.append(tip_height)

		# End of media reading

		media.release()

		# -> Fit a 10th order poly
		tenth_poly = np.polyfit(h, H, 10)

		# -> Derivative of the 10th poly
		der_poly = np.polyder(tenth_poly,2)

		# -> Get linear region
		linear_interval_flag = True
		linear_region_start = -float('inf')
		linear_region_end = float('inf')
		linear_region_points = {}

		for flame_pos, flame_height in enumerate(h):
			eval = abs(np.polyval(der_poly, flame_height))
			if(eval <= args.DerivativeThreshold):
				linear_region_points[flame_height] = np.polyval(tenth_poly, flame_height)
				if linear_interval_flag:
					linear_region_start = flame_pos
					linear_interval_flag = False
				linear_region_end = flame_pos

		# Check if linear region does in fact was found
		if(len(linear_region_points) <= 2):
			print("No enough points ({}) were found to set the linear region with derivative threshold of {}".format(len(linear_region_points),args.DerivativeThreshold))
			linear_poly = None
			sp_height = None
			sp_Height = None
		else:
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
				if(distance > SP_THRESHOLD):
					sp_height = flame_height
					sp_Height = poly_H_val
					break

		if(sp_height):
			sp_mm = px_2_mm(sp_height)
			error = TARGET_SP - sp_mm
		
		print("Core % {} | SPH = {} mm | TARGET = {} | ERROR = {}".format(core_por, sp_mm, TARGET_SP, error))
		# Recalculate thresholds 
		core_por += DELTA*error







if __name__ == '__main__':
	args = argsHandler()
	smokepoint(args)
