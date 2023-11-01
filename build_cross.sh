#!/bin/bash
wine /home/$(whoami)/.wine/drive_c/users/$(whoami)/AppData/Local/Programs/Python/Python312/Scripts/pyinstaller.exe -F main.py
mv dist/main.exe dist/KS0108BSimulator_windows.exe

