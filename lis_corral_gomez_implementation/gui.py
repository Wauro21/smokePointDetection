import tkinter as tk
from tkinter import ttk
import ttkthemes
from tkinter.filedialog import askopenfilename


class  MainWindow:


    #Constructor
    def __init__(self):
        self.root = tk.Tk()
        # Define UI style
        self.root.style = ttkthemes.ThemedStyle()
        self.root.style.theme_use('breeze')

        self.filePane = FileBox(self.root)

    def start(self):
        self.root.mainloop()

class FileBox:

    def __init__(self, root):
        self.btn = tk.Button(root, text='Open', command = lambda:self.openFile())
        self.btn.pack(side=tk.TOP)


    def openFile(self):
        # This method for when processing A video
        file = askopenfilename(filetypes = [('Video Files', '*.avi')])
        return file


def main():
    print("Hello World!")
    a = MainWindow()
    a.start()
if __name__ == '__main__':
    main()
