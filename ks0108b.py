def set_bit(value, bit):
    return value | (1 << bit)


def clear_bit(value, bit):
    return value & ~(1 << bit)


class KS0108:
    rs: bool = 0
    rw: bool = 0
    db: int = 0
    x_address: int = 0
    y_address: int = 0
    z_address: int = 0
    ram = [[0 for x in range(64)] for y in range(8)]

    def getRS(self) -> bool:
        return self.rs

    def getRW(self) -> bool:
        return self.rw

    def getDB(self) -> int:
        return self.db

    def getDBbit(self, mask) -> bool:
        return mask & self.db

    def setRS(self, b: bool):
        self.rs = b

    def setRW(self, b: bool):
        self.rw = b

    def setDB(self, b: int):
        self.db = b

    def setDBbit(self, mask):
        self.db = set_bit(self.db, mask)

    def clearDBbit(self, mask):
        self.db = clear_bit(self.db, mask)

    def runCommand(self):
        if (
            self.getRS() == 0
            and self.getRW() == 0
            and (self.getDB() == 0b00111111 or self.getDB() == 0b00111110)
        ):
            self.display_on_off(self.getDBbit(0b00000001))

    def setYaddress(self, address):
        self.y_address = address

    def setXaddress(self, address):
        self.X_address = address

    def setZaddress(self, address):
        self.Z_address = address

    def display_on_off(self, toggle):
        print(toggle)

    def writeData(self):


display = KS0108()
