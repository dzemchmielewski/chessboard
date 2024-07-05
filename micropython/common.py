import time


class Metering:
    def __init__(self, steps_per_loop=1):
        self.steps_per_loop = steps_per_loop
        self._step = 0
        self.start_timer = time.ticks_ms()

    def start(self):
        self.start_timer = time.ticks_ms()
        self._step = 0

    def step(self, step=1) -> (int, float):
        self._step += step
        if self._step >= self.steps_per_loop:
            return self.loop()
        return None

    def loop(self) -> (int, float):
        end = time.ticks_ms()
        result = (self._step, end - self.start_timer)
        self.start_timer = time.ticks_ms()
        self._step = 0
        return result


class Common:
    def __init__(self, name, debug=False, metering=False):
        self.name = name
        self.enableDebug = debug
        self.enableMetering = metering
        self.metering = None

    def debug(self, message):
        if self.enableDebug:
            print("[{}][DEBUG] {}".format(self.name, message))

    def log(self, message):
        print("[{}] {}".format(self.name, message))

    def metering_start(self):
        if self.enableMetering:
            self.metering = Metering()
        return self.metering

    def metering_print(self, message):
        if self.enableMetering:
            self.log("[METERING] {} {}".format(message, self.metering.step()))

    @staticmethod
    def format_uptime(uptime):
        (minutes, seconds) = divmod(uptime, 60)
        (hours, minutes) = divmod(minutes, 60)
        (days, hours) = divmod(hours, 24)
        result = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        if days:
            result = "{:d} days ".format(days) + " " + result
        return result


if __name__ == "__main__":
    c = Common("test", True)
    c.log("test")
    c.debug("dupa")
    c.log("end")


# >>> timeInit = int(time.time())
# >>> timeDiff = timeDiff - 86400
# >>> timeDiff = timeDiff - 3600
# >>> timeDiff = timeDiff - 1800
# >>> timeDiff
# -91708.86072897911
# >>> timeInit = int(time.time())
# >>> timeInit = timeInit - 88000
# >>>
# >>>
# >>>
# >>>
# >>>
# >>>

# >>>