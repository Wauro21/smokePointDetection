from CONSTANTS import CONTOUR_BOUNDING_BOX_COLOR, CORE_BOUNDING_BOX_COLOR, FRAME_CENTROID_COLOR, MAX_CENTROID_TOLERANCE, REFERENCE_CENTROID_COLOR
from GUI_CONSTANTS import FrameTypes
from utils import getThreshvalues, heightBox, plotCentroid
from processing import frameProcess
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
import numpy as np
import cv2

class VideoReader(QThread):

    update_frame_signal = pyqtSignal(np.ndarray)
    values_signal = pyqtSignal(list)
    centroid_signal = pyqtSignal(list)
    
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
        core_threshold_value = getThreshvalues(self.process_controls['core_%'])
        contour_threshold_value = getThreshvalues(self.process_controls['contour_%'])
        
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
            ret, frame = media.read()
            if(not ret):
                # End of media
                break
            
            cut_info = self.process_controls['cut']

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

                self.centroid_signal.emit([frame_counter, reference_centroid_x])

                continue

            # For the rest of the frames

            # -> Generate height boxes to display
            if(self.process_controls['bboxes']): 
                heightBox(frame_processed[FrameTypes.FRAME], frame_processed[FrameTypes.CORE_CC], CORE_BOUNDING_BOX_COLOR)
                heightBox(frame_processed[FrameTypes.FRAME], frame_processed[FrameTypes.CONTOUR_CC], CONTOUR_BOUNDING_BOX_COLOR)

            # -> Draw the reference centroids and the actual centroid
            if(self.process_controls['centroids']):
                plotCentroid(frame_processed[FrameTypes.FRAME], reference_centroid_x, reference_centroid_y, REFERENCE_CENTROID_COLOR)
                plotCentroid(frame_processed[FrameTypes.FRAME], frame_processed[FrameTypes.CONTOUR_CC]['cX'], frame_processed[FrameTypes.CONTOUR_CC]['cY'], FRAME_CENTROID_COLOR)
                
            
            # Calculate the centroid difference to check if is a valid frame
            invalid_frame_h = []
            invalid_frame_H = []
            frame_centroid = frame_processed[FrameTypes.CONTOUR_CC]['cX']
            centroid_diff = abs(frame_centroid - reference_centroid_x)
            if(centroid_diff > MAX_CENTROID_TOLERANCE):
                invalid_frame_counter += 1
                invalid_frame_h.append(contour_height)
                invalid_frame_H.append(tip_height)
                self.centroid_signal.emit([frame_counter, frame_centroid, False])
                continue
            
            # If the data is valid, append it
            h.append(contour_height)
            H.append(tip_height)
            self.centroid_signal.emit([frame_counter, frame_centroid, True])

            # End of media reading

            # -> Select displayed media
            requestedFrame = self.process_controls['display']
            to_display = self.toDisplay(requestedFrame, frame_processed)
            self.update_frame_signal.emit(to_display)


            self.values_signal.emit([frame_counter, contour_height, tip_height])

    def toDisplay(self, requestedFrame, frame_processed):
        
        if(requestedFrame is FrameTypes.CORE_CC or requestedFrame is FrameTypes.CONTOUR_CC):
            return frame_processed[requestedFrame]['cmask']

        return frame_processed[requestedFrame]