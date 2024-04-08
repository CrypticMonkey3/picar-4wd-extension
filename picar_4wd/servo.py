# / ------------------------------------------------------------------------------------ \
# | Title: PiCar_4WD servo.py source code											     |
# | Author: Sunfounder																     |
# | Last update: 12 July 2023														     |
# | Availability: https://github.com/sunfounder/picar-4wd/blob/master/picar_4wd/servo.py |
# \ ------------------------------------------------------------------------------------ /

from utils import mapping

class Servo():
    PERIOD = 4095
    PRESCALER = 10
    MAX_PW = 2500
    MIN_PW = 500
    FREQ = 50
    ARR = 4095
    CPU_CLOCK = 72000000
    def __init__(self, pin, offset=0):
        self.pin = pin
        self.offset = offset
        self.pin.period(self.PERIOD)
        prescaler = int(float(self.CPU_CLOCK) / self.FREQ/ self.ARR)
        self.pin.prescaler(prescaler)

    def set_angle(self, angle):
        try:
            angle = int(angle)
        except:
            raise ValueError("Angle value should be int value, not %s"%angle)
        if angle < -90:
            angle = -90
        if angle > 90:
            angle = 90
        angle = angle + self.offset
        High_level_time = mapping(angle, -90, 90, self.MIN_PW, self.MAX_PW)
        pwr =  High_level_time / 20000
        value = int(pwr*self.PERIOD)
        self.pin.pulse_width(value)
