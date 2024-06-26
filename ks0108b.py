from PIL import Image


def commandLookup(data: int):
    # 10 bit bus
    # rs rw db7 db6 db5 db4 db3 db2 db1 db0
    data = format(data, "010b")
    if data[0:9] == "000011111":  # display on/off
        return "display on/off"

    if data[0:2] == "01" and data[3] == "0" and data[6:10] == "0000":  # status read
        return "status read"

    if data[0:4] == "0001":  # set y address (address)
        return "set y address (address)"

    if data[0:7] == "0010111":  # set x address (page)
        return "set x address (page)"

    if data[0:4] == "0011":  # set z address (display line)
        return "set z address (display line)"

    if data[0:2] == "10":  # write data
        return "write data"

    if data[0:2] == "11":  # read data
        return "read data"
    else:
        return "no valid command"


class KS0108:
    def __init__(self):
        self.x_address: int = 0
        self.y_address: int = 0
        self.z_address: int = 0
        self.on: bool = 1
        self.ram = [[0 for y in range(64)] for x in range(8)]

    def runCommand(self, data: int):
        # 10 bit bus
        # rs rw db7 db6 db5 db4 db3 db2 db1 db0
        if commandLookup(data) == "display on/off":
            self.display_on_off(int(format(data, "010b")[9:10], 2))
            return data

        if commandLookup(data) == "status read":
            return int(f"0b0100{int(not self.on)}00000", 2)

        if commandLookup(data) == "set y address (address)":
            self.setYaddress(int(format(data, "010b")[4:10], 2))
            return data

        if commandLookup(data) == "set x address (page)":
            self.setXaddress(int(format(data, "010b")[7:10], 2))
            return data

        if commandLookup(data) == "set z address (display line)":
            self.setZaddress(int(format(data, "010b")[4:10], 2))
            return data

        if commandLookup(data) == "write data":
            self.writeData(int(format(data, "010b")[2:10], 2))
            return data

        if commandLookup(data) == "read data":
            return 0b1100000000 + self.readData()

        return data

    def setYaddress(self, address):
        if address in range(64):
            self.y_address = address

    def setXaddress(self, address):
        if address in range(8):
            self.x_address = address

    def setZaddress(self, address):
        if address in range(64):
            self.z_address = address

    def display_on_off(self, toggle):
        self.on = toggle

    def writeData(self, data):
        self.ram[self.x_address][self.y_address] = data
        if self.y_address >= 63:
            self.y_address = 0
        else:
            self.y_address += 1

    def readData(self):
        return self.ram[self.x_address][self.y_address]

    def setPixel(self, x, y):
        page = y // 8
        self.ram[page][x] = self.ram[page][x] | (1 << (y % 8))

    def clearPixel(self, x, y):
        page = y // 8
        self.ram[page][x] = self.ram[page][x] & (0xFF - (1 << (y % 8)))

    def generateImage(self):
        img = Image.new("1", (64, 64))
        for y, page in enumerate(self.ram):
            for x, bits in enumerate(page):
                for i in range(8):
                    if self.on:
                        img.putpixel(
                            (x, ((y * 8 + i) - self.z_address) % 64), (bits >> i) & 1
                        )
        return img

    def displayRam(self):
        out_string = ""
        for i in self.ram:
            out_string += " ".join([format(x, "02x") for x in i]) + "\n"
        return out_string


# d = KS0108()
# print(d.displayRam())
