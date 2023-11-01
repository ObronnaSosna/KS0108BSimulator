#!/bin/bash
source venv/bin/activate
pyinstaller -F main.py
mv dist/main dist/KS0108BSimulator_linux
deactivate

