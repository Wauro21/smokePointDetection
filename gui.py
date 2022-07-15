import tkinter as tk
from tkinter import ttk
import ttkthemes
from tkinter.filedialog import askopenfilename
import os
import cv2
import imutils
from PIL import Image, ImageTk
import time
import threading

def readFrames(frameHolder):
    video = cv2.VideoCapture('test.mp4')
    while video.isOpened():
        ret, frame = video.read()
        if(ret):
            cv2img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2img)
            imgTk = ImageTk.PhotoImage(image=img)
            #frameHolder.imgtk = imgTk
            frameHolder.config(image=imgTk)
            time.sleep(1/25)
        else:
            break

class  MainWindow:
    #Constructor
    def __init__(self):
        self.root = tk.Tk()
        # Define UI style
        self.root.style = ttkthemes.ThemedStyle()
        self.root.style.theme_use('breeze')

        self.filePane = FileBox(self.root)
        self.videoPane = VideoWindow(self.root)

    def start(self):
        self.root.mainloop()

class FileBox(ttk.Frame):

    def __init__(self, root):
        super().__init__(root,width=500, height =200, relief=tk.GROOVE, borderwidth = 1)

        # Items for this pane
        #   -> Input selection: Show path and button
        #   -> Info about the input (In some part open the input)
        #   -> Type of input : Video or Frame Folder

        # [FIX] Change the geometry for more dynamic view

        self.fileName = tk.StringVar(self, 'EMPTY FILE')
        self.filePath = tk.StringVar(self, 'EMPTY PATH')
        self.infoText = tk.StringVar(self, '')

        input_sign = tk.Label(self, text='Input: ',font='Helvetica 10 bold')
        input_sign.grid(row = 0, column = 0)

        self.file_display = tk.Label(self, textvariable=self.fileName,width=30, justify='left',anchor='w',relief='sunken', bg='white')
        self.file_display.grid(row=0, column=1)

        self.info_title = tk.Label(self, text = 'Media Information:',font='Helvetica 10 bold')
        self.info_title.grid(row=1,column=0)
        self.info_display = tk.Label(self, textvariable=self.infoText, justify='left')
        self.info_display.grid(row=2, column=0)

        self.btn = tk.Button(self, text='Open', command = self.loadRoutine )
        self.btn.grid(row = 0, column = 2)
        self.pack_propagate(0)
        self.pack()


    def loadRoutine(self):
        #User loads file
        self.openFile()
        # Info its update
        self.getInfo()

    def openFile(self):
        file = askopenfilename(filetypes = [('Video Files', '*.avi')])

        self.filePath.set(file)
        self.fileName.set(os.path.basename(file))


    def getInfo(self):
        base_text = "- Dimentions: {} px x {} px \n- FPS: {} \n- Frames totales: {}"

        try:
            video = cv2.VideoCapture(self.filePath.get())
            width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = video.get(cv2.CAP_PROP_FPS)
            fc = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            video.release()
            self.infoText.set(base_text.format(width, height, fps, fc))
        except Exception as e:
            tk.messagebox.showerror('Media Error', e)

class VideoWindow(ttk.Frame):
    def __init__(self,root):
        super().__init__(root, relief=tk.GROOVE, borderwidth = 1)
        self.videoDisplay = tk.Label(self, width=500, height=500)
        self.videoDisplay.grid(row=0,column=0)
        #self.videoDisplay.imgtk = None
        self.pack()

def main():
    a = MainWindow()
    x = threading.Thread(target=readFrames, args=(a.videoPane.videoDisplay,), daemon=True)
    x.start()
    a.start()
if __name__ == '__main__':
    main()
