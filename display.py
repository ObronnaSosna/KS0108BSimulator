from ks0108b import KS0108
from PIL import Image, ImageTk
import io


def resetActiveDriver():
    displays[cs] = KS0108()


def createDisplays(n):
    return [KS0108() for x in range(n)]


def changeDriverAmount(dn):
    global cs, displays
    displays = createDisplays(dn)
    cs = 0


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


def getImage():
    return convertImage(displays, scale)


def setScale(s):
    global scale
    scale = s


def getDriversAmount():
    return len(displays)


def getActiveDriver():
    return cs


def changeActiveDriver(c):
    global cs
    if c > getDriversAmount():
        return
    cs = c


def getActiveDriverRegisters():
    return {
        "x": displays[cs].x_address,
        "y": displays[cs].y_address,
        "z": displays[cs].z_address,
    }


def getDriversRam():
    return [d.displayRam() for d in displays]


def runCommandOnActiveDriver(command):
    global displays
    return displays[cs].runCommand(command)


scale = 5
displays = createDisplays(3)
cs = 0
scale = 5
