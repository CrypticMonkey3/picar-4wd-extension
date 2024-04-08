# / --------------------------------------------------------------------------------------- \
# | Title: PiCar_4WD __init__.py source code											    |
# | Author: Sunfounder																		|
# | Last update: 12 July 2023																|
# | Availability: https://github.com/sunfounder/picar-4wd/blob/master/picar_4wd/__init__.py |
# \ --------------------------------------------------------------------------------------- /

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwm import PWM
from adc import ADC
from pin import Pin
from motor import Motor
from servo import Servo
from ultrasonic import Ultrasonic 
from speed import Speed
from filedb import FileDB  
from utils import *
import time
from version import __version__


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result


class PiCar:
    ANGLE_RANGE = 180
    STEP = 18
    
    def __init__(self):
        soft_reset()
        time.sleep(0.2)

        # Config File:
        self.__config = FileDB("config")
        self.__left_front_reverse = self.__config.get('left_front_reverse', default_value = False)
        self.__right_front_reverse = self.__config.get('right_front_reverse', default_value = False)
        self.__left_rear_reverse = self.__config.get('left_rear_reverse', default_value = False)
        self.__right_rear_reverse = self.__config.get('right_rear_reverse', default_value = False)    
        self.__ultrasonic_servo_offset = int(self.__config.get('ultrasonic_servo_offset', default_value = 0)) 

        # Init motors
        self._left_front = Motor(PWM("P13"), Pin("D4"), is_reversed=self.__left_front_reverse) # motor 1
        self._right_front = Motor(PWM("P12"), Pin("D5"), is_reversed=self.__right_front_reverse) # motor 2
        self._left_rear = Motor(PWM("P8"), Pin("D11"), is_reversed=self.__left_rear_reverse) # motor 3
        self._right_rear = Motor(PWM("P9"), Pin("D15"), is_reversed=self.__right_rear_reverse) # motor 4

        # self.__left_front_speed = Speed(12)
        # self.__right_front_speed = Speed(16)
        self.__left_rear_speed = Speed(25)
        self.__right_rear_speed = Speed(4)  

        # Init Greyscale
        self._gs0 = ADC('A5')
        self._gs1 = ADC('A6')
        self._gs2 = ADC('A7')

        # Init Ultrasonic
        self._us = Ultrasonic(Pin('D8'), Pin('D9'))
        
        self.__us_step = self.STEP
        self.__angle_distance = [0, 0]
        self.__current_angle = 0
        self.__max_angle = self.ANGLE_RANGE / 2
        self.__min_angle = -self.ANGLE_RANGE / 2
        self.__scan_list = []

        self.__errors = []

        # Init Servo
        # print("Init Servo: %s" % ultrasonic_servo_offset)
        self._servo = Servo(PWM("P0"), offset=self.__ultrasonic_servo_offset)

    def start_speed_thread(self):
        # self.__left_front_speed.start()
        # self.__right_front_speed.start()
        self.__left_rear_speed.start()
        self.__right_rear_speed.start()

    # ------------ Grayscale -------------- #
    def get_grayscale_list(self):
        return [self._gs0.read(), self._gs1.read(), self._gs2.read()]

    @staticmethod
    def is_on_edge(ref, gs_list):
        return gs_list[2] <= int(ref) or gs_list[1] <= int(ref) or gs_list[0] <= int(ref)
    
    @staticmethod
    def get_line_status(ref, fl_list):#170<x<300
        ref = int(ref)
        if fl_list[1] <= ref:
            return 0
        
        elif fl_list[0] <= ref:
            return -1

        elif fl_list[2] <= ref:
            return 1

    # ------------ Ultrasonic -------------- #
    def do(self, msg="", cmd=""):
        print(" - %s..." % (msg), end='\r')
        print(" - %s... " % (msg), end='')
        status, result = eval(cmd)
        # print(status, result)
        
        if not status or status is None or not result:
            print(f'\033[32m{cmd}\nDone.\033[0m')
        else:
            print(f"\033[1;31mError!\nStatus: {status}\nMessage: {result}\033[0m")
            self.__errors.append("%s error:\n  Status:%s\n  Error:%s" %
                          (msg, status, result))

    def get_distance_at(self, angle):
        self._servo.set_angle(angle)
        time.sleep(0.04)

        distance = self._us.get_distance()
        self.__angle_distance = [angle, distance]
        
        return distance

    def get_status_at(self, angle, ref1=35, ref2=10):
        dist = self.get_distance_at(angle)
        
        if dist > ref1 or dist == -2:
            return 2
        elif dist > ref2:
            return 1
        
        return 0

    def scan_step(self, ref):
        self.__current_angle = max(0, min(self.__us_step + self.__current_angle, self.__max_angle))
        
        if self.__current_angle >= self.__max_angle:
            self.__us_step = -self.STEP
        
        elif self.__current_angle <= self.__min_angle:
            self.__us_step = self.STEP

        self.__scan_list.append(self.get_status_at(self.__current_angle, ref1=ref))
        
        if self.__current_angle == self.__min_angle or self.__current_angle == self.__max_angle:
            if self.__us_step < 0:
                self.__scan_list.reverse()
                
            # print(scan_list)
            tmp = self.__scan_list.copy()
            self.__scan_list = []
            return tmp
        
        return False

    # ------------ Motors -------------- #
    def forward(self, power):
        self._left_front.set_power(power)
        self._left_rear.set_power(power)
        self._right_front.set_power(power)
        self._right_rear.set_power(power)

    def backward(power):
        self._left_front.set_power(-power)
        self._left_rear.set_power(-power)
        self._right_front.set_power(-power)
        self._right_rear.set_power(-power)

    def turn_left(self, power):
        self._left_front.set_power(-power)
        self._left_rear.set_power(-power)
        self._right_front.set_power(power)
        self._right_rear.set_power(power)

    def turn_right(self, power):
        self._left_front.set_power(power)
        self._left_rear.set_power(power)
        self._right_front.set_power(-power)
        self._right_rear.set_power(-power)

    def stop(self):
        self._left_front.set_power(0)
        self._left_rear.set_power(0)
        self._right_front.set_power(0)
        self._right_rear.set_power(0)

    def set_motor_power(self, motor, power):
        if motor == 1:
            self._left_front.set_power(power)
        elif motor == 2:
            self._right_front.set_power(power)
        elif motor == 3:
            self._left_rear.set_power(power)
        elif motor == 4:
            self._right_rear.set_power(power)

    # def speed_val(*arg):
    #     if len(arg) == 0:
    #         return (left_front_speed() + left_rear_speed() + right_front_speed() + right_rear_speed()) / 4
    #     elif arg[0] == 1:
    #         return left_front_speed()
    #     elif arg[0] == 2:
    #         return right_front_speed()
    #     elif arg[0] == 3:
    #         return left_rear_speed()
    #     elif arg[0] == 4:
    #         return right_rear_speed()

    def speed_val(self):
        return (self.__left_rear_speed() + self.__right_rear_speed()) / 2.0


if __name__ == '__main__':
    picar = PiCar()
    picar.start_speed_thread()
    
    while True:
        picar.forward(500)
        #time.sleep(0.1)
        print(picar.speed_val())
