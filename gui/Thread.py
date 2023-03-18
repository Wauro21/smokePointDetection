from CONSTANTS import CONTOUR_BOUNDING_BOX_COLOR, CORE_BOUNDING_BOX_COLOR, DERIVATIVE_LOW_BOUND, DERIVATIVE_ORDER, FRAME_CENTROID_COLOR, LINEAR_POLY_ORDER, MAX_CENTROID_TOLERANCE, POLYNOMIAL_ORDER, REFERENCE_CENTROID_COLOR, SP_THRESHOLD
from GUI_CONSTANTS import CentroidTypes, FrameTypes
from utils import findLinearRegion, getThreshvalues, heightBox, plotCentroid
from processing import frameProcess, processHeights
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
import numpy as np
import cv2


class PolyAnalizer(QThread):
    heights_plot = pyqtSignal()
    linear_plot = pyqtSignal()
    linear_error = pyqtSignal()
    sp_plot = pyqtSignal()
    sp_error = pyqtSignal()

    def __init__(self, process_controls):
        
        super().__init__()

        self.process_controls = process_controls


    def run(self):
        
        der_threshold = self.process_controls['controls']['der_threshold']
        h = self.process_controls['results']['h']
        H = self.process_controls['results']['H']

        # -> Fit 10th order poly
        tenth_poly = np.polyfit(h,H, POLYNOMIAL_ORDER)
        self.process_controls['results']['10th_poly'] = tenth_poly

        # -> Derivative of the 10th order poly
        der_poly = np.polyder(tenth_poly, DERIVATIVE_ORDER)
        self.process_controls['results']['10th_der'] = der_poly
        
        # -> Emit h v/s H plot
        self.heights_plot.emit()

        # Find linear region
        linear_region = findLinearRegion(h, tenth_poly, der_poly, der_threshold)
        if(linear_region is None or len(linear_region) <= 2):
            # Not enough points to process
            self.linear_error.emit()
            return None
        
        # Save the linear region info
        self.process_controls['results']['linear_region'] = linear_region
        self.linear_plot.emit()

        # -> Apply linear fit to the region
        h_linear = list(linear_region.keys())
        H_linear = list(linear_region.values())
        linear_poly = np.polyfit(h_linear, H_linear, LINEAR_POLY_ORDER)
        self.process_controls['results']['linear_poly'] = linear_poly

        # Find the SP value
        sp_h = None
        sp_H = None
        h_points = np.linspace(min(h), max(h), len(h))
        h_linear_start = h_linear[0]
        for h_val in h_points:
            # Only search starting from linear region
            if(h_val >= h_linear_start):
                H_val = np.polyval(tenth_poly, h_val)
                H_poly = np.polyval(linear_poly, h_val)
                distance = H_val - H_poly
                if(distance > SP_THRESHOLD):
                    sp_h = h_val
                    sp_H = H_val
                    break
        if not(sp_H):
            self.sp_error.emit()
            return False
    
        # Save value and emit signal
        self.process_controls['results']['sp'] = [sp_h, sp_H]
        self.sp_plot.emit()

        

class VideoReader(QThread):

    update_frame_signal = pyqtSignal(np.ndarray)
    values_signal = pyqtSignal(list)
    centroid_signal = pyqtSignal(dict)
    
    def __init__(self, video_path, process_controls):
        super().__init__()
        self.video_path = video_path
        self.process_controls = process_controls


    def run(self):

        # Unpack media and info
        media = cv2.VideoCapture(self.video_path, 0)
        n_frames = int(media.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(media.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(media.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Get threshold values 
        core_threshold_value = getThreshvalues(self.process_controls['controls']['core_%'])
        contour_threshold_value = getThreshvalues(self.process_controls['controls']['contour_%'])
        
        # Temp storage for heights
        h = []
        H = []

        # For first frame, get reference centroids
        
        first_frame_flag = True
        # -> The values are set to something impossible
        reference_centroid_x = -float('inf')
        reference_centroid_y = -float('inf')

        # Frame statistics 
        frame_counter = 0
        invalid_frame_counter = 0        

        # Frame per frame processing
        while media.isOpened():

            # Check if stop is requested
            if(self.process_controls['signals']['stop']):
                return None

            ret, frame = media.read()
            if(not ret):
                # End of media
                break
            
            cut_info = self.process_controls['controls']['cut']

            frame_counter += 1
            frame_processed = frameProcess(frame, cut_info, core_threshold_value, contour_threshold_value)

            # Get contour and tip height
            contour_height = frame_processed[FrameTypes.CONTOUR_CC]['h']
            # -> Consider that (0,0) is top left corner
            tip_height = frame_processed[FrameTypes.CORE_CC]['y'] - frame_processed[FrameTypes.CONTOUR_CC]['y']

            if(first_frame_flag):
                reference_centroid_x = frame_processed[FrameTypes.CONTOUR_CC]['cX']
                reference_centroid_y = frame_processed[FrameTypes.CONTOUR_CC]['cY']
                first_frame_flag = False

                # First frame heights are considerated valid
                h.append(contour_height)
                H.append(tip_height)

                # Centroid reference emit

                centroid_message = {
                    CentroidTypes.REFERENCE: reference_centroid_x
                    }

                self.centroid_signal.emit(centroid_message)

                continue

            # For the rest of the frames

            # -> Generate height boxes to display
            if(self.process_controls['frames_info']['bboxes']): 
                heightBox(frame_processed[FrameTypes.FRAME], frame_processed[FrameTypes.CORE_CC], CORE_BOUNDING_BOX_COLOR)
                heightBox(frame_processed[FrameTypes.FRAME], frame_processed[FrameTypes.CONTOUR_CC], CONTOUR_BOUNDING_BOX_COLOR)

            # -> Draw the reference centroids and the actual centroid
            if(self.process_controls['frames_info']['centroids']):
                cv2.line(frame_processed[FrameTypes.FRAME], (round(reference_centroid_x), 0), (round(reference_centroid_x), height), REFERENCE_CENTROID_COLOR, thickness=2)
                plotCentroid(frame_processed[FrameTypes.FRAME], frame_processed[FrameTypes.CONTOUR_CC]['cX'], frame_processed[FrameTypes.CONTOUR_CC]['cY'], FRAME_CENTROID_COLOR)
                
            
            # Calculate the centroid difference to check if is a valid frame
            invalid_frame_h = []
            invalid_frame_H = []
            frame_centroid = frame_processed[FrameTypes.CONTOUR_CC]['cX']
            centroid_diff = abs(frame_centroid - reference_centroid_x)
            if(centroid_diff > self.process_controls['controls']['centroid_tol']):
                invalid_frame_counter += 1
                invalid_frame_h.append(contour_height)
                invalid_frame_H.append(tip_height)
                # Set the message 
                centroid_message = {
                    CentroidTypes.INVALID: [frame_counter, frame_centroid]
                }
                self.centroid_signal.emit(centroid_message)
                continue
            
            # If the data is valid, append it
            h.append(contour_height)
            H.append(tip_height)

            # Set the message
            centroid_message = {
                CentroidTypes.VALID: [frame_counter, frame_centroid]
            }
            self.centroid_signal.emit(centroid_message)

            # End of media reading

            # -> Select displayed media
            requestedFrame = self.process_controls['frames_info']['display']
            to_display = self.toDisplay(requestedFrame, frame_processed)
            self.update_frame_signal.emit(to_display)


            self.values_signal.emit([frame_counter, contour_height, tip_height])

        # When processing is done 
        self.process_controls['results']['h'] = h
        self.process_controls['results']['H'] = H
        

    def toDisplay(self, requestedFrame, frame_processed):
        
        if(requestedFrame is FrameTypes.CORE_CC or requestedFrame is FrameTypes.CONTOUR_CC):
            return frame_processed[requestedFrame]['cmask']

        return frame_processed[requestedFrame]