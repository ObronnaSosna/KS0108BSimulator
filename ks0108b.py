from PIL import Image


class KS0108:
    x_address: int = 0
    y_address: int = 0
    z_address: int = 0
    on: bool = 0
    ram = [[0 for y in range(64)] for x in range(8)]

    def runCommand(self, data: int):
        # 10 bit input
        # rs rw db7 db6 db5 db4 db3 db2 db1 db0
        if format(data, "010b")[0:9] == "000011111":  # display on/off
            self.display_on_off(int(format(data, "010b")[9:10], 2))

        if format(data, "010b")[0:4] == "0001":  # set y address (address)
            self.setYaddress(int(format(data, "010b")[4:10], 2))

        if format(data, "010b")[0:7] == "0010111":  # set x address (page)
            self.setXaddress(int(format(data, "010b")[7:10], 2))

        if format(data, "010b")[0:4] == "0011":  # set z address (display line)
            self.setZaddress(int(format(data, "010b")[4:10], 2))

        if format(data, "010b")[0:2] == "01":  # write data
            self.writeData(int(format(data, "010b")[2:10], 2))

    def setYaddress(self, address):
        self.y_address = address

    def setXaddress(self, address):
        self.x_address = address

    def setZaddress(self, address):
        self.z_address = address

    def display_on_off(self, toggle):
        self.on = toggle

    def writeData(self, data):
        self.ram[self.x_address][self.y_address] = data
        if self.y_address >= 63:
            self.y_address = 0
        else:
            self.y_address += 1

    def generateImage(self):
        img = Image.new("1", (64, 64))
        for y, page in enumerate(display.ram):
            for x, bits in enumerate(page):
                for i in range(8):
                    if self.on:
                        img.putpixel((x, y * 8 + i), (bits >> i) & 1)
        return img


display = KS0108()
display.runCommand(0b0000111111)  # turn on


img = display.generateImage()
img.save("out.bmp")
