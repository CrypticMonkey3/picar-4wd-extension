from datetime import datetime
from typing import *
import subprocess
import evdev
import sys
from os import getlogin

sys.path.insert(1, f"/home/{getlogin()}/picar-4wd/picar_4wd/")

from picar_4wd import PiCar

# PRESS '(SQUARE) X + POWER'

# Right Trigger accelerate/forward
# Left Trigger reverse
# Left Joystick + Left buttons direction
# Right Joystick ultrasonic movement
# Right Bumper increase top speed
# Left Bumper decrease top speed

# ENSURE THAT CONTROLLER IS CONNECTED TO RPI BEFORE EXECUTING.
# To do this follow the steps below, and remove connectivity from controller if you have it already connected:
# 1. Go to Terminal and type in 'ls /dev/input', remember the number of events there, if any.
# 2. Go to Terminal and type in 'bluetoothctl'.
# 3. Type in 'scan on'
# 4. Find the MAC address related to your controller, this is usually identified by seeing the controller name, and type in 'connect [Controller MAC Address]'
# 5 Once successful, type 'scan off'
# 6. Type 'quit'
# 7. Type 'ls /dev/input' again, and if there's more events than at the start you're good to run this program.
# If there's no more events than when you started, and you don't have any other connection for the controller, than the controller is incompatible.
# If there are other connection methods, try them.
# If worst case everything still doesn't want to connect, try powering on and off the pi and redo all the steps above until it works.


def connect_controller(mac_address: str, timeout: datetime) -> Union[evdev.InputDevice, None]:
    """
    Tries to connect to a controller.
    :param str mac_address: The MAC address of the controller to connect to.
    :param datetime timeout: How long the time out has been for, if any.
    :return: evdev.InputDevice
    """
    # get a list of all connected devices to the RPI, and filter those with no MAC Addresses
    connected_devices = list(filter(lambda x: len(x) > 0, [evdev.InputDevice(device).uniq.upper() for device in evdev.list_devices()]))
    device_history = subprocess.run(["bluetoothctl", "devices"], capture_output=True).stdout.decode()  # all the devices the RPI has connected to before
    
    # if the MAC Address of the Controller is not currently connected but the Controller MAC address has already been paired with the RPI before.
    if mac_address not in connected_devices and mac_address in device_history:
        # Then just wait for the controller to reconnect by itself with the RPI.
        num_points = int((datetime.now() - timeout).total_seconds()) % 4
        print(f"\033[1;31mWaiting for controller to connect{'.' * num_points if num_points != 0 else '   '}\033[0m", end="\r")
        return
    
    # else if the Controller MAC Address hasn't been connected to the RPI before.
    elif mac_address not in device_history:
        print("\033[1;31mSet up bluetooth connection using Terminal!\033[0m", end="\r")
        return
    
    # to make it here the controller must be connected
    device = evdev.InputDevice(evdev.list_devices()[connected_devices.index(mac_address)])  # gets the connected controller

    if (datetime.now() - timeout).total_seconds() > 0.5:
        print(connected_devices)
        print()
    print("\033[1;32mSuccessfully connected!\033[0m")
    print(f"DEVICE PATH:\t{device.path}\nDEVICE NAME:\t{device.name}\nDEVICE MAC:\t{device.uniq.upper()}")
    return device  # The device and an events generator for the controller
    

class PiCarExtension(PiCar):
    def __init__(self, controller_mac: str):
        try:
            super().__init__()
        except OSError:
            raise Exception("Developer's Message: 'Turn on PiCar-4WD'.")

        self.__controller_mac = controller_mac
        self.__controller_last_active = datetime.now()
        
        self.__controller = connect_controller(controller_mac, self.__controller_last_active)
        while self.__controller is None:
            self.__controller = connect_controller(controller_mac, self.__controller_last_active)
        
        self.__events_gen = self.__controller.read_loop()
        self.__running = True
        
    def __check_events(self) -> None:
        """
        Checks and executes any events coming from the controller.
        :return: None
        """
        try:
            next_event = next(self.__events_gen)
            self.__controller_last_active = datetime.now()
        
        except (OSError, StopIteration):  # only occurs when the controller disconnects mid session
            self.__controller = connect_controller(self.__controller_mac, self.__controller_last_active)  # tries to reconnect with controller, or gives some feedback on how to.
            if self.__controller is not None:  # if the controller has been found again
                self.__events_gen = self.__controller.read_loop()  # create the a new generator for the InputDevice
            
            return
        
        # if a button or trigger was pressed on the controller 
        if next_event and next_event.type == evdev.ecodes.EV_KEY:
            print(evdev.categorize(next_event))
            print()
        
        # for axial movements from joysticks, or the D-Pad
        elif next_event and next_event.type == evdev.ecodes.EV_ABS:
            print(next_event)
            print("Abs ^")
        
        
    def __process(self) -> None:
        """
        The method that interlinks all methods required to make the car function.
        :return: None
        """
        self.__check_events()
        
    def run(self) -> None:
        """
        Method to call to run the PiCar.
        :return: None
        """
        while self.__running:
            self.__process()


if __name__ == "__main__":
    picar_extension = PiCarExtension("03:D0:D3:68:27:03")
    picar_extension.run()
