import _thread
import gc
import ubinascii
import machine
from machine import Pin, UART
from utime import sleep
import time
import json
import board
from common import Common


finish_server = False


class BoardServer(Common):

    SELF_RELOAD_EXEC = "import sys\ndel sys.modules['server']\nimport server\nserver.BoardServer().start()\n"

    def __init__(self):
        super().__init__("SERVER", False, False)
        self.uart = UART(0, baudrate=76800, bits=8, tx=Pin(0), rx=Pin(1), timeout=2)
        #self.uart = UART(0, baudrate=9600, bits=8, tx=Pin(0), rx=Pin(1), timeout=2)
        #self.uart = UART(0, baudrate=115200, bits=8, tx=Pin(0), rx=Pin(1), timeout=2)
        self.id = ubinascii.hexlify(machine.unique_id()).decode()
        self.start_time = time.ticks_ms()
        self.system_status = {
            "id": self.id,
            "freq": machine.freq()/1_000_000,
        }
        board.reader_data.id = self.id

    def log(self, msg):
        print("[SERVER {}] {}".format(self.id, msg))

    def handle_put(self, msg):
        s = msg.split()
        if len(s) != 3:
            return "[ER] USAGE: PUT filename size"
        filename = s[1]

        if not s[2].isdigit():
            return "[ER] cannot convert to integer: {}".format(s[1])
        bytes = int(s[2])

        self.uart.write("ready for putting {} bytes to the {} file\n".format(bytes, filename).encode())
        self.uart.flush()

        with open(filename, "w") as f:
            b = None
            while b is None:
                b = self.uart.read(bytes)

            f.write(b.decode())
        return "put completed: {}".format(filename)

    def start(self):
        self.log("START")
        restart = False
        global finish_server

        while not finish_server and not restart:
            b = self.uart.readline()
            if b:
                raw_msg = b.decode()
                self.log("IN : {}".format(raw_msg))
                msg = raw_msg.strip().upper()

                if msg == "READ":
                    answer = json.dumps(board.reader_data.readings)

                elif msg == "INFO":
                    answer = json.dumps(board.reader_data.__dict__)

                elif msg == "UPTIME":
                    answer = "OS up: {}, server up: {}".format(
                        self.format_uptime(time.ticks_ms() // 1000),
                        self.format_uptime((time.ticks_ms() - self.start_time) // 1_000))

                elif msg == "DEV":
                    try:
                        answer = "dev todo"
                    except BaseException as e:
                        answer = str(e)

                elif msg == "EXIT":
                    finish_server = True
                    board.reader_data.go_exit = True
                    answer = "BYE"

                elif msg == "RESTART":
                    restart = True
                    board.reader_data.go_exit = True
                    answer = "call restart"

                elif msg == "REBOOT":
                    machine.reset()
                    answer = "call reboot"

                elif msg.startswith("PUT"):
                    answer = self.handle_put(raw_msg)

                elif msg == "STATUS":
                    gc.collect()
                    self.system_status["os_uptime"] = time.ticks_ms() // 1000
                    self.system_status["server_uptime"] = (time.ticks_ms() - self.start_time) // 1_000
                    self.system_status["mem_alloc"] = gc.mem_alloc()
                    self.system_status["mem_free"] = gc.mem_free()
                    answer = json.dumps(self.system_status)

                elif msg == "GO":
                    if board.reader_data.is_alive:
                        answer = "already started..."
                    else:
                        board.reader_data.go_exit = False
                        _thread.start_new_thread(board.BoardReader().start, ())
                        answer = "call board reader start"

                elif msg == "NOGO":
                    if board.reader_data.is_alive:
                        board.reader_data.go_exit = True
                        answer = "call board reader finish"
                    else:
                        answer = "not alive..."

                else:
                    answer = "unknown command"

                self.log("OUT: {}".format(answer))
                self.uart.write("{}\n".format(answer).encode())
                self.uart.flush()

        self.log("Exit")
        if restart:
            sleep(1)
            exec(self.SELF_RELOAD_EXEC)

# exec("import server\nserver.BoardServer().start()")
# exec(open("main.py").read())

