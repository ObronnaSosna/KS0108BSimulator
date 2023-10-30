#KS0108B Simulator

##INSTALL
~~~~
git clone https://github.com/ObronnaSosna/KS0108BSimulator
cd KS0108BSimulator
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
~~~~

##RUN
~~~~
python main.py
~~~~

##PACKAGE
~~~~
pip install pyinstaller
pyinstaller -F main.py
~~~~
Executable will be in dist/main

#CREDITS
- ICON chip by Matej Design from https://thenounproject.com/browse/icons/term/chip/
