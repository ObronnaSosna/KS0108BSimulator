#!/usr/bin/env python
import PySimpleGUI as sg
from PIL import Image, ImageTk
from ks0108b import KS0108
import io
import base64


# parse checkboxes into binary number
def getData():
    data = 0
    for i, value in enumerate(values.values()):
        if i < 3:
            pass
        else:
            data += 2 ** (9 - (i - 3)) * value
    return data


# change simulator output to something tk can display
def convertImage(displays):
    img = displays[0].generateImage()
    img2 = displays[1].generateImage()
    img3 = displays[2].generateImage()
    img = img.resize((320, 320), Image.LANCZOS)
    img2 = img2.resize((320, 320), Image.LANCZOS)
    img3 = img3.resize((320, 320), Image.LANCZOS)
    out = Image.new("1", (960, 320))
    out.paste(img, (0, 0))
    out.paste(img2, (320, 0))
    out.paste(img3, (640, 0))
    bio = io.BytesIO()
    out.save(bio, format="PNG")
    return bio


displays = [KS0108(), KS0108(), KS0108()]
for display in displays:
    display.display_on_off(1)
bio = convertImage(displays)

# Define the window's contents
layout = [
    [
        sg.Column(
            [[sg.Image(key="image", data=bio.getvalue())]], justification="center"
        ),
    ],
    [
        sg.Text("Data IN: ", size=(13, 1), key="din"),
        sg.Text("Data OUT: ", size=(15, 1), key="dout"),
        sg.Text("Command: ", size=(40, 1), key="cmd"),
        sg.Text("Y address: ", size=(16, 1), key="y"),
        sg.Text("X address: ", size=(16, 1), key="x"),
        sg.Text("Z address: ", size=(16, 1), key="z"),
    ],
    [
        sg.Button("E", key="e"),
        sg.Radio("CS0", "cs", key="cs0", default=True),
        sg.Radio(
            "CS1",
            "cs",
            key="cs1",
        ),
        sg.Radio(
            "CS2",
            "cs",
            key="cs2",
        ),
        sg.Checkbox("RS", key="rs", enable_events=True),
        sg.Checkbox("R/W", key="rw", enable_events=True),
        sg.Checkbox("DB7", key="db7", enable_events=True),
        sg.Checkbox("DB6", key="db6", enable_events=True),
        sg.Checkbox("DB5", key="db5", enable_events=True),
        sg.Checkbox("DB4", key="db4", enable_events=True),
        sg.Checkbox("DB3", key="db3", enable_events=True),
        sg.Checkbox("DB2", key="db2", enable_events=True),
        sg.Checkbox("DB1", key="db1", enable_events=True),
        sg.Checkbox("DB0", key="db0", enable_events=True),
        sg.Button("Show Memory", key="ram"),
    ],
]

# Create the window
window = sg.Window("KS0108B simulator", layout)


# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break

    if event == "ram":
        layout2 = [
            [sg.Text("CS0:")],
            [sg.Text(f"{displays[0].displayRam()}", font="Monospace 8", key="r")],
            [sg.Text("CS1:")],
            [sg.Text(f"{displays[1].displayRam()}", font="Monospace 8", key="r")],
            [sg.Text("CS2:")],
            [sg.Text(f"{displays[2].displayRam()}", font="Monospace 8", key="r")],
        ]
        window_ram = sg.Window("RAM", layout2, modal=True)
        while True:
            event, values = window_ram.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

        window_ram.close()

    # simulate pulse on enable pin (run command)
    if event == "e":
        if values["cs0"] == True:
            display = displays[0]
        if values["cs1"] == True:
            display = displays[1]
        if values["cs2"] == True:
            display = displays[2]
        data = getData()
        dout = display.runCommand(data)
        bio = convertImage(displays)
        window["image"].update(data=bio.getvalue())
        window["dout"].update(f"Data OUT: {hex(dout)}")
        window["y"].update(f"Y address: {hex(display.y_address)}")
        window["x"].update(f"X address: {hex(display.x_address)}")
        window["z"].update(f"Z address: {hex(display.z_address)}")

    # update data and command display
    if event in ["rs", "rw", "db7", "db6", "db5", "db4", "db3", "db2", "db1", "db0"]:
        data = getData()
        window["din"].update(f"Data IN: {hex(data)}")
        window["cmd"].update(f"Command: {display.commandLookup(data)}")

# Finish up by removing from the screen
window.close()
