#!/usr/bin/env python
import PySimpleGUI as sg
from PIL import Image, ImageTk
from ks0108b import KS0108
from icon import icon
import ks0108b
import io
import base64
import history
import arduino
import display
from time import sleep
import convert
from pathlib import Path

ard = False


# parse checkboxes into binary number
def getData():
    data = 0
    for key, value in values.items():
        if "db" in key:
            i = int(key.replace("db", ""))
            data += 2**i * value
        if "rw" in key:
            i = 8
            data += 2**i * value
        if "rs" in key:
            i = 9
            data += 2**i * value
    return data


def updateDataOut():
    # update image data out and registers
    bio = display.getImage()
    registers = display.getActiveDriverRegisters()
    window["image"].update(data=bio.getvalue())
    window["dout"].update(f"Data OUT: {hex(dout)}")
    window["y"].update(f"Y address: {hex(registers['y'])}")
    window["x"].update(f"X address: {hex(registers['x'])}")
    window["z"].update(f"Z address: {hex(registers['z'])}")


bio = display.getImage()
ports = arduino.getPorts()
dout = 0

# Define the window's contents
main_window_layout = [
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
        sg.Text("Command: ", size=(30, 1), key="cmd", expand_x=True),
        sg.Text("Y address: ", size=(16, 1), key="y"),
        sg.Text("X address: ", size=(16, 1), key="x"),
        sg.Text("Z address: ", size=(16, 1), key="z"),
        sg.Combo(ports, expand_x=True, enable_events=True, readonly=True, key="port"),
        sg.Checkbox("Arduino", key="arduino", enable_events=True),
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
            sg.Button("Load Image", key="img", expand_x=True),
            sg.Button("Show Memory", key="ram", expand_x=True),
            sg.Button("History", key="cmds", expand_x=True),
        ],
    ],
]

# Create the window
window = sg.Window("KS0108B simulator", main_window_layout, icon=icon, finalize=True)
window.bind("<Return>", "enter")


# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break

    if event == "arduino" or "port":
        if values["arduino"]:
            ard = True
            arduino.arduinoInit(values["port"])
        else:
            ard = False
            arduino.arduinoClose()

    # change number of drivers
    if event == "dn":
        # get amount of drivers
        dn = int(values["dn"])

        # disable radio buttons for unused cs
        for i in range(3):
            if i >= dn:
                window[f"cs{i}"].update(disabled=True)
            else:
                window[f"cs{i}"].update(disabled=False)

        # change nuber of drivers
        display.changeDriverAmount(dn)
        history.clear()

        # set cs to 0
        display.changeActiveDriver(0)
        window["cs0"].update(value=True)

        # reset arduino
        if ard:
            arduino.arduinoClose()
            arduino.arduinoInit(values["port"])

        updateDataOut()

    # change scale
    if event == "scale":
        # set scale
        scale = int(values["scale"])
        display.setScale(scale)

        # update image
        bio = display.getImage()
        window["image"].update(data=bio.getvalue())

    # change chip
    if event in ["cs0", "cs1", "cs2"]:
        # change active driver
        for i in range(display.getDriversAmount()):
            if values[f"cs{i}"] == True:
                display.changeActiveDriver(i)

        updateDataOut()

    # display ram modal
    if event == "ram":
        layout2 = []
        for i, ram in enumerate(display.getDriversRam()):
            layout2.append([sg.Text(f"CS{i}:")])
            layout2.append([sg.Text(f"{ram}", font="Monospace 8", key="r")])
        window_ram = sg.Window("RAM", layout2, icon=icon, modal=True)
        while True:
            event, values = window_ram.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

        window_ram.close()

    # display commands modal
    if event == "cmds":
        history_layout = [
            [
                sg.Column(
                    [
                        [
                            sg.Text(history.print(), key="history"),
                        ]
                    ],
                    scrollable=True,
                    vertical_scroll_only=True,
                    size=(600, 300),
                )
            ],
            [
                sg.Button("Save commands to .txt", key="saveHuman", expand_x=True),
                sg.Button("Save commands to .json", key="save", expand_x=True),
            ],
            [sg.Button("Load from .json", key="load", expand_x=True)],
        ]
        window_cmd = sg.Window("Command history", history_layout, icon=icon, modal=True)
        while True:
            event, values = window_cmd.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "saveHuman":
                history.saveHumanReadable("commands.txt")

            if event == "save":
                history.save("commands.json")

            if event == "load":
                history.load("commands.json")
                # reset drivers and run all loaded commands on the,
                for cs, cmds in enumerate(history.commands):
                    if cs >= display.getDriversAmount():
                        break
                    display.changeActiveDriver(cs)
                    display.resetActiveDriver()
                    for cmd in cmds:
                        dout = display.runCommandOnActiveDriver(cmd)
                        if ard:
                            arduino.sendCommand(cs, cmd)
                            sleep(0.0005)

                updateDataOut()

                # change active driver to 0 and update history
                display.changeActiveDriver(0)
                window["cs0"].update(value=True)
                window_cmd["history"].update(history.print())

        window_cmd.close()
    # reset chip
    if event == "reset":
        display.resetActiveDriver()
        dout = 0
        history.clearCs(display.getActiveDriver())
        if ard:
            arduino.arduinoClose()
            arduino.arduinoInit(values["port"])
        updateDataOut()

    # simulate pulse on enable pin (run command)
    if event in ["e", "enter"]:
        data = getData()
        history.add(display.getActiveDriver(), data)
        dout = display.runCommandOnActiveDriver(data)
        if ard:
            arduino.sendCommand(display.getActiveDriver(), data)

        updateDataOut()

    # update data and command display
    if event in ["rs", "rw", "db7", "db6", "db5", "db4", "db3", "db2", "db1", "db0"]:
        data = getData()
        window["din"].update(f"Data IN: {hex(data)}")
        window["cmd"].update(f"Command: {ks0108b.commandLookup(data)}")

    if event == "img":
        image_layout = [
            [
                sg.Column(
                    [[sg.Image(key="convert_image", size=(400, 300))]],
                    # [[sg.Image(key="con_image")]],
                    justification="center",
                ),
            ],
            [
                sg.Text("Threshold:", size=(10, 1)),
                sg.Slider(
                    (0, 256), orientation="horizontal", default_value=127, key="tres"
                ),
                sg.Text("Choose image", size=(50, 1), key="path"),
                sg.Button("Browse", key="file"),
                sg.Button("Convert", key="convert"),
            ],
        ]
        window_convert = sg.Window(
            "Load Image",
            image_layout,
            icon=icon,
            modal=True,
        )
        while True:
            event, values = window_convert.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "file":
                filename = sg.popup_get_file("", no_window=True)
                if not Path(filename).is_file():
                    continue

                window_convert["path"].update(filename)

                im = Image.open(filename)
                im.thumbnail((500, 400))
                b = io.BytesIO()
                im.save(b, format="PNG")
                window_convert["convert_image"].update(data=b.getvalue())

            if event == "convert":
                if not Path(filename).is_file():
                    continue
                tres = values["tres"]
                convert.convertMultipleChips(filename, display.getDriversAmount(), tres)
                # reset drivers and run all loaded commands on the,
                for cs, cmds in enumerate(history.commands):
                    if cs >= display.getDriversAmount():
                        break
                    display.changeActiveDriver(cs)
                    display.resetActiveDriver()
                    for cmd in cmds:
                        dout = display.runCommandOnActiveDriver(cmd)
                        if ard:
                            arduino.sendCommand(cs, cmd)
                            sleep(0.0005)

                updateDataOut()

                # change active driver to 0
                display.changeActiveDriver(0)
                window["cs0"].update(value=True)
                window_convert.close()

# Finish up by removing from the screen
window.close()
