# Import Modules
import tkinter as tk
import os
# from ctypes import windll

# Custom Title bar Handler, because Tk sux
# I copied the code LMAO

# Tk Configurations
mainWindow = tk.Tk()
mainWindow.update_idletasks()
mainWindow.overrideredirect(True)
mainWindow.rowconfigure(0, minsize=800, weight=1)
mainWindow.columnconfigure(1, minsize=800, weight=1)
mainWindow.title("Calculator")
mainWindow.eval('tk::PlaceWindow . center')

mainCanvas = tk.Canvas(mainWindow,height=500,width=500)
mainCanvas.pack()

# External files
invisibleImage = tk.PhotoImage(file="Invisible.png")
minimizeImage = tk.PhotoImage(file="Minimize.png")
fullscreenImage = tk.PhotoImage(file="Fullscreen.png")
normalImage = tk.PhotoImage(file="Normal.png")
closeImage = tk.PhotoImage(file="Close.png")


# Window Menu / Title bar
def minimizeHandler():
    global hasopen, hasstyle
    if hasstyle:
        mainWindow.update_idletasks()
        mainWindow.withdraw()
        mainWindow.overrideredirect(False)
        mainWindow.state("iconic")
        hasopen = False
        hasstyle = False

def showHandler(_):
    global hasopen
    if not hasopen:
        mainWindow.withdraw()
        mainWindow.overrideredirect(True)
        mainWindow.update_idletasks()
        hasopen = True


titleCanvas = tk.Canvas(mainCanvas,relief=tk.RAISED, bd=0)
minimizeProgram = tk.Button(titleCanvas,image=minimizeImage,bd=0,command=minimizeHandler)
minimizeProgram.grid(row=0, column=2, sticky="e", padx=5, pady=5)
screenProgram = tk.Button(titleCanvas,image=fullscreenImage,bd=0,command=lambda : os.kill(os.getpid(),0))
screenProgram.grid(row=0, column=3, sticky="e", padx=5, pady=5)
closeProgram = tk.Button(titleCanvas,image=closeImage,bd=0,command=lambda : os.kill(os.getpid(),0))
closeProgram.grid(row=0, column=4, sticky="e", padx=5, pady=5)
titleCanvas.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
titleCanvas.bind("<Map>",showHandler)

# Normal Calculator
inputString = tk.StringVar()
inputString.trace_add("write",callback=lambda x,y,z :print(inputString.get()))
inputField = tk.Entry(mainCanvas,textvariable=inputString)
inputField.grid(row=1, column=0, sticky="ew", padx=5, pady=5)


# Start
hasstyle = False
hasopen = False
mainWindow.update_idletasks()
mainWindow.withdraw()
mainWindow.mainloop(0)