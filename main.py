#!/usr/bin/env python
import PySimpleGUI as sg
from PIL import Image, ImageTk
from ks0108b import KS0108
import ks0108b
import io
import base64
import history


# parse checkboxes into binary number
def getData():
    data = 0
    for i, value in enumerate(values.values()):
        if i < 5:
            pass
        else:
            data += 2 ** (9 - (i - 5)) * value
    return data


# change simulator output to something tk can display
def convertImage(displays, scale):
    scale_size = 64 * scale
    displays_number = len(displays)
    out = Image.new("1", (scale_size * displays_number, scale_size))
    for i, display in enumerate(displays):
        img = display.generateImage().resize((scale_size, scale_size), Image.LANCZOS)
        out.paste(img, (scale_size * i, 0))
    bio = io.BytesIO()
    out.save(bio, format="PNG")
    return bio


def createDisplays(n):
    return [KS0108() for x in range(n)]


scale = 5
displays = createDisplays(3)
cs = 0
display = displays[cs]
bio = convertImage(displays, scale)


# Define the window's contents
layout = [
    [
        sg.Column(
            [[sg.Image(key="image", data=bio.getvalue())]], justification="center"
        ),
    ],
    [
        sg.Text("Chips:", size=(6, 1)),
        sg.Combo([1, 2, 3], default_value=3, size=(2, 1), key="dn", enable_events=True),
        sg.Text("Scale:", size=(6, 1)),
        sg.Combo(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            default_value=5,
            size=(2, 1),
            key="scale",
            enable_events=True,
        ),
        sg.Text("Data IN: ", size=(13, 1), key="din"),
        sg.Text("Data OUT: ", size=(15, 1), key="dout"),
        sg.Text("Command: ", size=(40, 1), key="cmd", expand_x=True),
        sg.Text("Y address: ", size=(16, 1), key="y"),
        sg.Text("X address: ", size=(16, 1), key="x"),
        sg.Text("Z address: ", size=(16, 1), key="z"),
    ],
    [
        [
            sg.Button("E", key="e"),
            sg.Button("Reset", key="reset"),
            sg.Radio("CS0", "cs", key="cs0", default=True, enable_events=True),
            sg.Radio("CS1", "cs", key="cs1", enable_events=True),
            sg.Radio("CS2", "cs", key="cs2", enable_events=True),
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
            sg.Button("Show Memory", key="ram", expand_x=True),
            sg.Button("History", key="cmds", expand_x=True),
        ],
    ],
]

# Create the window
window = sg.Window("KS0108B simulator", layout, icon=icon, finalize=True)
window.bind("<Return>", "enter")


# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break

    # change number of drivers
    if event == "dn":
        dn = int(values["dn"])
        for i in range(3):
            if i >= dn:
                window[f"cs{i}"].update(disabled=True)
            else:
                window[f"cs{i}"].update(disabled=False)
        displays = createDisplays(dn)
        display = displays[0]
        bio = convertImage(displays, scale)
        window["image"].update(data=bio.getvalue())

    # change scale
    if event == "scale":
        scale = int(values["scale"])
        bio = convertImage(displays, scale)
        window["image"].update(data=bio.getvalue())

    # change chip
    if event in ["cs0", "cs1", "cs2"]:
        for i in range(len(displays)):
            if values[f"cs{i}"] == True:
                cs = i
                display = displays[i]
        window["y"].update(f"Y address: {hex(display.y_address)}")
        window["x"].update(f"X address: {hex(display.x_address)}")
        window["z"].update(f"Z address: {hex(display.z_address)}")

    # display ram modal
    if event == "ram":
        layout2 = []
        for i, display in enumerate(displays):
            layout2.append([sg.Text(f"CS{i}:")])
            layout2.append(
                [sg.Text(f"{display.displayRam()}", font="Monospace 8", key="r")]
            )
        window_ram = sg.Window("RAM", layout2, icon=icon, modal=True)
        while True:
            event, values = window_ram.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

        window_ram.close()

    # display commands modal
    if event == "cmds":
        layout3 = [
            [sg.Text(history.print())],
            [sg.Button("Save commands", key="save", expand_x=True)],
        ]
        window_cmd = sg.Window("Command history", layout3, icon=icon, modal=True)
        while True:
            event, values = window_cmd.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "save":
                history.saveHumanReadable("commands.txt")

        window_cmd.close()
    # reset chip
    if event == "reset":
        displays[cs] = KS0108()
        display = displays[cs]
        dout = 0
        history.clear()
        bio = convertImage(displays, scale)
        window["image"].update(data=bio.getvalue())
        window["dout"].update(f"Data OUT: {hex(dout)}")
        window["y"].update(f"Y address: {hex(display.y_address)}")
        window["x"].update(f"X address: {hex(display.x_address)}")
        window["z"].update(f"Z address: {hex(display.z_address)}")

    # simulate pulse on enable pin (run command)
    if event in ["e", "enter"]:
        data = getData()
        history.add(cs, data)
        dout = display.runCommand(data)
        bio = convertImage(displays, scale)
        window["image"].update(data=bio.getvalue())
        window["dout"].update(f"Data OUT: {hex(dout)}")
        window["y"].update(f"Y address: {hex(display.y_address)}")
        window["x"].update(f"X address: {hex(display.x_address)}")
        window["z"].update(f"Z address: {hex(display.z_address)}")

    # update data and command display
    if event in ["rs", "rw", "db7", "db6", "db5", "db4", "db3", "db2", "db1", "db0"]:
        data = getData()
        window["din"].update(f"Data IN: {hex(data)}")
        window["cmd"].update(f"Command: {ks0108b.commandLookup(data)}")

# Finish up by removing from the screen
window.close()
