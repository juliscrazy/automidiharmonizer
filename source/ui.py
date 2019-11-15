import tkinter as tk
from source.porthandler import openports
from source.maps import *
import threading
import sys

def apply(inport, outport, newscale, newkey, inports, outports):
    global midiin, midiout, scale, key
    scale = newscale
    key = newkey
    midiin, midiout = openports(inports.index(bytes(inport[2:-1], "utf-8")), outports.index(bytes(outport[2:-1], "utf-8")))

def harmonize(pitch, scale, key):
    note = pitch % 12
    octave = pitch // 12
    if scale == "minor":
        note = minormap[note]
    if scale == "major":
        pass
    note = note + keymap[key]
    newpitch = note + 12 * octave
    return newpitch

def run():
    global midiin, midiout, key, scale, running
    running = True
    while running:
        try:
            midiag = midiin.get_message()
            if midiag != (None, None):
                print(midiag)
                status, pitch, velocity = midiag[0]
                newpitch = harmonize(pitch, scale, key)
                midiout.send_message([status, newpitch, velocity])
        except NameError:
            #no midi devices selected
            pass 

def on_closing():
    global midiout, midiin, midithread, root, running
    del midiout, midiin
    running = False
    root.destroy()
    sys.exit()

def backgroundthread():
    global midithread
    midithread = threading.Thread(target=run)
    midithread.start()

def _uisetup(inports: list, outports: list):
    global root

    root = tk.Tk()
    root.title("AMH")
    root.configure(padx=10, pady=10)
    root.resizable(False, False)
    # input
    inportvar = tk.StringVar(root)
    inportvar.set(inports[0])
    setinports = set(inports) 
    inportlabel = tk.Label(root, text="IN:")
    inportlabel.grid(row=0, column=0)
    inportmenu = tk.OptionMenu(root, inportvar, *setinports)
    inportmenu.grid(row=0, column=1, sticky=tk.W+tk.E)
    # output
    outportvar = tk.StringVar(root)
    setoutports = set(outports)
    outportvar.set(outports[0])
    outportlabel = tk.Label(root, text="OUT:")
    outportlabel.grid(row=1, column=0)
    outportmenu = tk.OptionMenu(root, outportvar, *setoutports)
    outportmenu.configure(width=len(max(outports, key=len)))
    outportmenu.grid(row=1, column=1, sticky=tk.W+tk.E)
    # keys
    keys = sorted({'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'})
    keyvar = tk.StringVar(root)
    keyvar.set("C")
    keylabel = tk.Label(root, text="KEY:")
    keylabel.grid(row=2, column=0)
    keymenu = tk.OptionMenu(root, keyvar, *keys)
    keymenu.grid(row=2, column=1, sticky=tk.W+tk.E)
    # scales
    scales = {"major", "minor"}
    scalevar = tk.StringVar(root)
    scalevar.set("major")
    scalelabel = tk.Label(root, text="SCALE:")
    scalelabel.grid(row=3, column=0)
    scalemenu = tk.OptionMenu(root, scalevar, *scales)
    scalemenu.config()
    scalemenu.grid(row=3, column=1, sticky=tk.W+tk.E)
    # apply button
    applybutton = tk.Button(root, text=" Apply ", width=30, command=lambda: apply(inportvar.get(), outportvar.get(), scalevar.get(), keyvar.get(), inports, outports))
    applybutton.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.after(200, backgroundthread)

def runui():
    root.mainloop()