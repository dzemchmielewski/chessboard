from mfrc522 import MFRC522, PINCSHandler
from common import Common, Metering


class ReaderData:
    def __init__(self):
        self.id = None
        self.is_alive = False
        self.go_exit = False
        self.stats = []
        self.message = None
        self.readings = {
        }


reader_data = ReaderData()


class BoardReader(Common):
    CS_CONFIGURATION = {
        "A1": 17,"A2": 21,
         "A3": 22, "A4": 26,
        # "B1": 17, "B2": 17, "B3": 17, "B4": 17,
        # "C1": 17, "C2": 17, "C3": 17, "C4": 17,
        # "D1": 17, "D2": 17, "D3": 17, "D4": 17,
        # 17 21 22 26
    }

    def __init__(self, debug=True):
        super().__init__("BRDRDR", debug, False)
        self.log("INIT")
        global reader_data
        self.fields_readers = {}
        for id, value in self.CS_CONFIGURATION.items():
            self.fields_readers[id] = MFRC522(spi_id=0, sck=18, miso=16, mosi=19, cs_handler=PINCSHandler(value), rst=20)
        reader_data.readings = {}
        for id, reader in self.fields_readers.items():
            reader.init()
            reader_data.readings[id] = None
        self.switch_counter = 0
        self.catch_miss = 0
        reader_data.stats = []

    def start(self):
        self.log("START")
        global reader_data
        metering = Metering(steps_per_loop=1600)
        reader_data.is_alive = True

        while not reader_data.go_exit:
            for id, fr in self.fields_readers.items():
                if reader_data.go_exit:
                    break
                value = fr.read_uid()
                if (stat := metering.step()) is not None:
                    reader_data.stats.append(stat)
                    self.log("Steps: {}, time: {}".format(stat[0], stat[1]))

                if value != reader_data.readings[id]:
                    # When we detect that the tag was removed...
                    if reader_data.readings[id] != "" and value == "":
                        # ... then let's make sure it was really removed,
                        # not just one-time read miss
                        # so, read again:
                        value = fr.read_uid()
                        if value == reader_data.readings[id]:
                            self.catch_miss += 1
                            reader_data.message = "caught miss: {},  switches: {}".format(self.catch_miss, self.switch_counter)

                if value != reader_data.readings[id]:
                    reader_data.readings[id] = value
                    self.switch_counter += 1
                    reader_data.message = "caught miss: {},  switches: {}".format(self.catch_miss, self.switch_counter)
                    self.debug(reader_data.__dict__)

        reader_data.is_alive = False
        self.log("EXIT")


if __name__ == '__main__':
    try:
        BoardReader().start()
    except KeyboardInterrupt:
        pass

# exec(open("board.py").read())


# from board import MFRC522Reader
# print("UID: {}".format(MFRC522Reader().read_uid()))
