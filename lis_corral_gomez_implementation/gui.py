import tkinter as tk
from tkinter import ttk
import ttkthemes
from tkinter.filedialog import askopenfilename
import os
import cv2

class  MainWindow:


    #Constructor
    def __init__(self):
        self.root = tk.Tk()
        # Define UI style
        self.root.style = ttkthemes.ThemedStyle()
        self.root.style.theme_use('breeze')

        self.filePane = FileBox(self.root)
        print(vars(self.filePane))

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

        input_sign = tk.Label(self, text='Input: ',font='Helvetica 10 bold')
        input_sign.grid(row = 0, column = 0)

        self.file_display = tk.Label(self, textvariable=self.fileName,width=30, justify='left',anchor='w',relief='sunken')
        self.file_display.grid(row=0, column=1)
        #self.

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

        try:
            print(self.filePath.get())
            video = cv2.VideoCapture(self.filePath.get())
            width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = video.get(cv2.CAP_PROP_FPS)
            fc = video.get(cv2.CAP_PROP_FRAME_COUNT)
            video.release()
            print('DIM {}x{}, fps {}, fc {}'.format(width,height, fps, fc))
        except Exception as e:
            print("AN ERROR NOT IMPLEMENTED YET ...")
            print(e)

def main():
    print("Hello World!")
    a = MainWindow()
    a.start()
if __name__ == '__main__':
    main()
