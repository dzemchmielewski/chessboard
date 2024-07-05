import machine
from utime import sleep
from common import Common


class ShiftRegister(Common):
    def __init__(self, length=8, data_pin: int = None, clock_pin: int = None, latch_pin: int = None, delay: float = None,
                 debug: bool = False):
        super().__init__("SHIFREG", debug, False)
        self.log("INIT")
        self.length = length
        self.delay = delay
        self.latch_pin = machine.Pin(latch_pin, machine.Pin.OUT)
        self.clock_pin = machine.Pin(clock_pin, machine.Pin.OUT)
        self.data_pin = machine.Pin(data_pin, machine.Pin.OUT)
        for pin in [self.latch_pin, self.clock_pin, self.data_pin]:
            pin.value(0)

    def _pulse(self, pin: machine.Pin):
        for signal in [1, 0]:
            pin.value(signal)
            if self.delay > 0:
                sleep(self.delay)

    def set(self, value):
        for _ in range(self.length):
            self.debug("data pin: {}".format(value & 1))
            self.data_pin.value(value & 1)
            self._pulse(self.clock_pin)
            value = value >> 1
        self._pulse(self.latch_pin)


class BitMatrix(Common):

    def __init__(self, rows: int, cols: int):
        super().__init__("BITMTRX", False, False)
        self.rows = rows
        self.cols = cols
        self.number = 0
        self.bit_format = "{{:#0{}b}}".format(rows * cols + 2)

    def _validate(self, x, y, bit):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            raise ValueError("Provided coordination: ({}, {}) is out of bounds: ({}, {})".format(x, y, self.rows, self.cols))
        if bit not in [0, 1]:
            raise ValueError("Invalid bit argument. Given: {}, required one off: {}".format(bit, [0, 1]))

    def _get(self, x, y):
        return (self.number >> ((x * self.cols) + y)) & 1

    def _set(self, x, y, bit):
        pos = (x * self.cols) + y
        mask = 1 << pos
        self.number = (self.number & ~mask) | ((bit << pos) & mask)
        return self

    def set(self, x: int, y: int, bit):
        self._validate(x, y, bit)
        return self._set(x, y, bit)

    def get(self, x, y) -> int:
        self._validate(x, y, 0)
        return self._get(x, y)

    def __str__(self) -> str:
        rows = [" ".join(["."] + ["|"] + [str(i) for i in range(0, self.cols)]), "-".join(["-"] * 2 + ["-"] * self.cols)]
        for x in range(0, self.rows):
            rows.append(" ".join([str(x), "|"] + [str(self._get(x, y)) for y in range(0, self.cols)]))
        return "\n".join(rows)

    def to_int(self) -> int:
        return self.number

    def to_bits(self) -> str:
        return self.bit_format.format(self.number)


if __name__ == "__main__":

    # Example usage:

    # BitMatrix:
    matrix = BitMatrix(4, 3)
    (matrix
     .set(0, 1, 1)
     .set(3,1,1)
     .set(3,2,1)
     .set(0,1,1))
    print(matrix)
    print("SIZE: {} x {}, NUMBER: {}, BITS: {}".format(matrix.rows, matrix.cols, matrix.to_int(), matrix.to_bits()))
    n = matrix.to_int()
    for i in range(16):
        print("bit by bit [{}]: {}".format(i, n & 1))
        n = n >> 1

    def bits(n, len=8):
        return ("{{:#0{}b}}".format(len+2)).format(n)

    def set_channel(channel: int):
        length = 8
        # print("AAAA" + bits(2 ** (length) - 1))
        return (1 << channel) ^ (2 ** length - 1)

    for i in range(8):
        c = set_channel(i)
        print("Channel {}: int {} bin {}".format(i, c, bits(c)))

