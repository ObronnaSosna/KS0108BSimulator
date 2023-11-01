#!/bin/bash
source venv/bin/activate
pyinstaller -F --noconsole  main.py
mv dist/main dist/KS0108BSimulator_linux
deactivate

