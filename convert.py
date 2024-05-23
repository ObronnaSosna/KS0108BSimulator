from PIL import Image
import numpy as np
import history


def prepareImage(image, threshold=127):
    # Grayscale
    image = image.convert("L")
    # Threshold
    image = image.point(lambda p: 255 if p > threshold else 0)
    # To mono
    image = image.convert("1")
    # to 64x64
    image = image.resize((64, 64))

    return image


def splitIntoEights(image):
    array = np.array(image)
    flat_array = array.ravel()
    eights = []
    for x in range(8):
        for y in range(64):
            eight = []
            for i in range(8):
                eight.append(flat_array[y + i * 64 + (x * 64 * 8)])
            eights.append(eight)
    return eights


def eightToNumber(eight):
    # for i, v in enumerate(eight):
    #    print(i, v, v ** int(i))
    #    number += v ** int(i)
    s = "".join("1" if c else "0" for c in eight)
    s = s[::-1]
    number = int(s, 2)
    return number


def convertToCommands(image, cs, threshold):
    image = prepareImage(image, threshold)
    eights = splitIntoEights(image)
    for i, eight in enumerate(eights):
        if i % 64 == 0:
            command = 184 + i // 64
            history.add(cs, command)
        command = 512 + eightToNumber(eight)
        history.add(cs, command)
    # history.save("commands.json")


def convertMultipleChips(filename, cs, threshold=127):
    image = Image.open(filename)
    history.clear()
    if cs == 1:
        convertToCommands(image, 0, threshold)
    if cs == 2:
        x, y = image.size
        box1 = (0, 0, x // 2, y)
        box2 = (x // 2, 0, x, y)
        half1 = image.crop(box1)
        half2 = image.crop(box2)
        convertToCommands(half1, 0, threshold)
        convertToCommands(half2, 1, threshold)
    if cs == 3:
        x, y = image.size
        box1 = (0, 0, x // 3, y)
        box2 = (x // 3, 0, (x // 3) * 2, y)
        box3 = ((x // 3) * 2, 0, x, y)
        half1 = image.crop(box1)
        half2 = image.crop(box2)
        half3 = image.crop(box3)
        convertToCommands(half1, 0, threshold)
        convertToCommands(half2, 1, threshold)
        convertToCommands(half3, 2, threshold)


# image = Image.open("test3.png")
# convertMultipleChips(image, 2, 220)
