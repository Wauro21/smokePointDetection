from tkinter import *
from tkinter import ttk
from processing_options import argsHandler
from processing import smokepoint
# Default values
CORE_THRESHOLD_PERCENT_TEXT = 75
CONTOUR_THRESHOLD_PERCENT_TEXT = 35
DEFAULT_VIDEO="test.avi"
def startProcessing(args, core, contour, display, bb):
    core_field = core.get()
    contouer_field = contour.get()
    args.TresholdCore = float(core_field)
    args.ThreshodContour = float(contouer_field)
    args.Display = display.get()
    args.Boxes = bb.get()
    # ONLY FOR DEMO
    args.Video = DEFAULT_VIDEO
    print(args)
    smokepoint(args)


def basicGUI():
    args = argsHandler()
    root = Tk()
    root.title("Smoke Point Detection")
    processing_params_frame = ttk.Frame(root, padding=10)
    processing_params_frame.grid()
    # Text for processing section
    ttk.Label(processing_params_frame, text="Parámetros de Procesamiento").grid(column=0, row=0)
    ttk.Label(processing_params_frame, text="Umbral Nucleo").grid(column=0,row=1)
    ttk.Label(processing_params_frame, text="Umbral Contorno").grid(column=0,row=2)
    ttk.Label(processing_params_frame, text="%").grid(column=3,row=1)
    ttk.Label(processing_params_frame, text="%").grid(column=3,row=2)
    # Fields
    core_threshold_field = ttk.Entry(processing_params_frame,width=5)
    core_threshold_field.grid(column=1,row=1)
    # Default core Threshold
    core_threshold_field.insert(0,CORE_THRESHOLD_PERCENT_TEXT)
    contour_threshold_field = ttk.Entry(processing_params_frame,width=5)
    contour_threshold_field.grid(column=1,row=2)
    # Default contouer threshold
    contour_threshold_field.insert(0,CONTOUR_THRESHOLD_PERCENT_TEXT)
    ttk.Button(processing_params_frame, text="Quit", command=root.destroy).grid(column=1, row=0)
    # Checkboxes
    # -> Vars
    display_var = BooleanVar()
    bb_var = BooleanVar()
    # -> Actual boxes
    bb_box = ttk.Checkbutton(processing_params_frame, text="BoundingBoxes", offvalue=False, onvalue=True, variable=bb_var)
    bb_box.grid(column=1, row=3)
    display_box = ttk.Checkbutton(processing_params_frame, text="Display", offvalue=False, onvalue=True, variable=display_var)
    display_box.grid(column=0,row=3)

    ttk.Button(processing_params_frame, text="Start", command=lambda: startProcessing(args,core_threshold_field, contour_threshold_field, display_var, bb_var)).grid(column=1,row=5)
    root.mainloop()

if __name__ == '__main__':
    basicGUI()
