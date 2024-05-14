#!/bin/bash
wine /home/$(whoami)/.wine/drive_c/users/$(whoami)/AppData/Local/Programs/Python/Python312/Scripts/pyinstaller.exe -F --noconsole main.py --additional-hooks-dir 'C:\\users\\stefan\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\serial\\__init__.py'
mv dist/main.exe dist/KS0108BSimulator_windows.exe

