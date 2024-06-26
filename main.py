#!/usr/bin/env python
import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageOps
from ks0108b import KS0108
from icon import icon
import ks0108b
import io
import base64
import history
import arduino
import display
import convert
from pathlib import Path


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
        sg.Combo(
            [1, 2, 3],
            default_value=display.default_display_amount,
            size=(2, 1),
            key="dn",
            enable_events=True,
        ),
        sg.Text("Scale:", size=(6, 1)),
        sg.Combo(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            default_value=display.default_scale,
            size=(2, 1),
            key="scale",
            enable_events=True,
        ),
        sg.Checkbox(
            "Invert",
            key="invert",
            default=display.default_invert,
            enable_events=True,
        ),
        sg.Text("Data IN: ", size=(13, 1), key="din"),
        sg.Text("Data OUT: ", size=(15, 1), key="dout"),
        sg.Text("Command: ", size=(30, 1), key="cmd", expand_x=True),
        sg.Text("Y address: ", size=(16, 1), key="y"),
        sg.Text("X address: ", size=(16, 1), key="x"),
        sg.Text("Z address: ", size=(16, 1), key="z"),
        sg.Combo(
            ports,
            expand_x=True,
            enable_events=True,
            readonly=True,
            key="port",
            default_value="",
        ),
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


dn = display.getDriversAmount()

# disable radio buttons for unused cs
for i in range(3):
    if i >= dn:
        window[f"cs{i}"].update(disabled=True)
    else:
        window[f"cs{i}"].update(disabled=False)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break

    if event == "port":
        ports = arduino.getPorts()
        window["port"].update(values=ports, value=values["port"])

    if event == "invert":
        display.setInvert(values["invert"])
        updateDataOut()

    if event == "arduino" or "port":
        if values["arduino"]:
            arduino.arduinoInit(values["port"])
        else:
            arduino.arduinoClose()

    # change number of drivers
    if event == "dn":
        # get amount of set drivers
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
        if arduino.enabled:
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
                # sg.Button("Save commands to .txt", key="saveHuman", expand_x=True),
                # sg.Button("Save commands to .json", key="save", expand_x=True),
                # sg.Button("Load from .json", key="load", expand_x=True),
                sg.Button("Save", key="save", expand_x=True),
                sg.Button("Load", key="load", expand_x=True),
            ],
        ]
        window_cmd = sg.Window("Command history", history_layout, icon=icon, modal=True)
        cmd_filename = ""
        while True:
            event, values = window_cmd.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "cmd_path":
                cmd_filename = values["cmd_path"]
                if not Path(cmd_filename).is_file():
                    continue

                window_cmd["cmd_path"].update(cmd_filename)

            if event == "save":
                cmd_filename = sg.popup_get_file(
                    "Save history",
                    no_window=True,
                    save_as=True,
                    file_types=[("Json", "*.json")],
                )

                if cmd_filename == () or cmd_filename == "":
                    continue

                history.save(cmd_filename)

            if event == "load":
                cmd_filename = sg.popup_get_file(
                    "Load history",
                    no_window=True,
                    file_types=[("Json", "*.json")],
                )

                if cmd_filename == () or cmd_filename == "":
                    continue

                history.load(cmd_filename)
                # reset drivers and run all loaded commands on the,
                for cs, cmds in enumerate(history.commands):
                    if cs >= display.getDriversAmount():
                        break
                    display.changeActiveDriver(cs)
                    display.resetActiveDriver()
                    for cmd in cmds:
                        dout = display.runCommandOnActiveDriver(cmd)
                        if arduino.enabled:
                            arduino.sendCommand(cs, cmd)

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
        if arduino.enabled:
            arduino.arduinoClose()
            arduino.arduinoInit(values["port"])
        updateDataOut()

    # simulate pulse on enable pin (run command)
    if event in ["e", "enter"]:
        data = getData()
        history.add(display.getActiveDriver(), data)
        dout = display.runCommandOnActiveDriver(data)
        if arduino.enabled:
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
                    [[sg.Image(key="convert_image")]],
                    # [[sg.Image(key="con_image")]],
                    justification="center",
                ),
            ],
            [
                sg.Text("Threshold:", size=(10, 1)),
                sg.Slider(
                    (0, 256),
                    orientation="horizontal",
                    default_value=127,
                    key="tres",
                    # disable_number_display=True,
                ),
                sg.Checkbox("Invert", key="convert_invert"),
                sg.Checkbox("Dithering", key="convert_dither", enable_events=True),
                sg.Push(),
                sg.Button("Open", key="open"),
                sg.Button("Convert", key="convert"),
            ],
        ]
        window_convert = sg.Window(
            "Load Image",
            image_layout,
            icon=icon,
            modal=True,
        )

        convert_filename = ""

        while True:
            event, values = window_convert.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "convert_dither":
                dith = values["convert_dither"]
                window_convert["tres"].update(value=0 if dith else 127)
                window_convert.refresh()
                window_convert["tres"].update(disabled=dith)

            if event == "open":
                convert_filename = sg.popup_get_file(
                    "",
                    no_window=True,
                    file_types=[("Image", "*.png *.jpeg *.jpg *.ppm")],
                )
                if convert_filename == () or convert_filename == "":
                    window_convert["convert_image"].update()
                    continue

                im = Image.open(convert_filename)
                # im.thumbnail((1200, 1000))
                im = ImageOps.contain(im, (800, 600))
                b = io.BytesIO()
                im.save(b, format="PNG")
                window_convert["convert_image"].update(data=b.getvalue())

            if event == "convert":
                # if not Path(convert_filename).is_file():
                #    continue
                tres = values["tres"]
                inv = values["convert_invert"]
                dith = values["convert_dither"]
                convert.convertMultipleChips(
                    convert_filename, display.getDriversAmount(), tres, inv, dith
                )
                # reset drivers and run all loaded commands on the,
                for cs, cmds in enumerate(history.commands):
                    if cs >= display.getDriversAmount():
                        break
                    display.changeActiveDriver(cs)
                    display.resetActiveDriver()
                    for cmd in cmds:
                        dout = display.runCommandOnActiveDriver(cmd)
                        if arduino.enabled:
                            arduino.sendCommand(cs, cmd)

                updateDataOut()

                # change active driver to 0
                display.changeActiveDriver(0)
                window["cs0"].update(value=True)
                window_convert.close()

# Finish up by removing from the screen
window.close()
