import platform
import sys
from datetime import datetime
from timeit import default_timer as timer

FULL_LOAD = True
if platform.uname().machine == "x86_64":
    FULL_LOAD = False

if FULL_LOAD:
    import RPi.GPIO as GPIO


class BusGPIO:
    if FULL_LOAD:
        GPIO.setmode(GPIO.BCM)

        @staticmethod
        def setup_out(pin):
            GPIO.setup(pin, GPIO.OUT)

        @staticmethod
        def setup_in(pin):
            GPIO.setup(pin, GPIO.IN)

        @staticmethod
        def output(pin, signal):
            GPIO.output(pin, signal)

        @staticmethod
        def cleanup():
            GPIO.cleanup()

    else:
        @staticmethod
        def setup_out(pin):
            pass

        @staticmethod
        def setup_in(pin):
            pass

        @staticmethod
        def output(pin, signal):
            pass

        @staticmethod
        def cleanup():
            pass

class Bus:

    def __init__(self, name):
        if type(name) in (tuple, list):
            self.name = [x for x in name]
        else:
            self.name = [name]

    def child(self, name):
        child = Bus(self.name)
        child.name.append(name)
        return child

    def log(self, msg, now=None):
        if now is None:
            now = datetime.now()

        print("[{:%Y-%m-%d %H:%M:%S.%f}][{}] {}".format(now, "][".join(self.name), msg))
        sys.stdout.flush()

    def debug(self, msg, now=None):
        self.log(msg, now)


class Metering:
    def __init__(self, steps_per_loop=20):
        self.steps_per_loop = steps_per_loop
        self._step = 0
        self.start_timer = timer()

    def start(self):
        self.start_timer = timer()
        self._step = 0

    def step(self, step=1) -> (int, float):
        self._step += step
        if self._step >= self.steps_per_loop:
            return self.loop()
        return None

    def loop(self) -> (int, float):
        end = timer()
        result = (self._step, end - self.start_timer)
        self.start_timer = timer()
        self._step = 0
        return result
