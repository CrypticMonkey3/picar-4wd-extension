# picar-4wd-extension
An extension for the PiCar-4WD which supports the original functionality but with controller and phone control instead of it entirely from the web.

## Equipment
_Note that the equipment linked, may not be the cheapest that can be found find but act as a visual guide of all the parts required_.
- [PiCar-4WD Car Kit](https://www.sunfounder.com/products/raspberry-pi-car-robot-kit-4wd?variant=43805575839979)
- [Raspberry Pi 3b+ Model](https://www.amazon.co.uk/Raspberry-Pi-3-Model-B/dp/B07BDR5PDW/ref=sr_1_2?crid=YGJYRDAXUSJ5&dib=eyJ2IjoiMSJ9.QRQnlDldrZ1kG52N6yCs7nxOXdbEU2xF61v3PeJEOOsXIvt2YY4bNasUeAbeSKFahCu1jBe2H7slJ4HIvp5575SaW-3u1smMaZLvCYP_drKE7kmMHGXfdI2IaguU9hLG0d8adRX0ESRI_yILf7voiVbwqNSLBs1cQ_kabpzYkqGndcyxokRn3vo324PjXMIkyXT-72bbvClxRW1qMcOlHjWCONfViYjuyO1e6NE3Zv0.mpLVrNmZ15D4OhnQEZNthCxZvr9DRf7DKrghaj6WXMw&dib_tag=se&keywords=raspberry+pi+3b%2B&qid=1712531351&sprefix=raspberry+pi+3b%2B%2Caps%2C90&sr=8-2)
- [2x 18650 Li Rechargeable batteries](https://www.amazon.co.uk/PAISUE-Capacity-Rechargeable-Batteries-Charging/dp/B0B2LL2FL4/ref=sr_1_9?crid=2918FB8U2O8EQ&dib=eyJ2IjoiMSJ9.h459TbWMkV2eSdFy4dHgtGBCo2uWh_9P3_07C0pfFxxDZeE7vKivbJDh4-g0z56uExpCZtVzH0S_ZuuNKCdj0SXFYmcIY2UqkG8oYsEGhR9jJpfCL2lN155Sqc0npEMyRe22BMj4M1Pm6k8vQc-vYTMyHoFznj7IUht7IvZC_8Z3UgR-A8OWdXlSiagPC1T5MnPzjIhzQvmpRda_dYcdXmzI5IBskG2OgYw6sCQaP-4.HzVrTc5LvWPi26pPIjDO2y66T9h0KPqwTZy84HSFxcQ&dib_tag=se&keywords=18650+rechargeable+battery+3.7V&qid=1712531287&sprefix=18650+rechargeable+battery+3.7v%2Caps%2C86&sr=8-9)
- [Stretchable controller for mobile phone](https://www.amazon.co.uk/dp/B0BSR6D2C5?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- Raspberry Pi Camera

## Controller
Best connection method for Majestech stretchable controller: PRESS '(SQUARE) X + POWER'.

### Bluetooth Setup
**ENSURE THAT CONTROLLER IS CONNECTED TO RPI BEFORE EXECUTING!**
To do this follow the steps below, and remove connectivity from controller if it is already connected:
1. Go to Terminal and type in 'ls /dev/input', remember the number of events there, if any.
2. Go to Terminal and type in 'bluetoothctl'.
3. Type in 'scan on'
4. Find the MAC address related to your controller, this is usually identified by seeing the controller name, and type in 'connect [Controller MAC Address]'
5 Once successful, type 'scan off'
6. Type 'quit'
7. Type 'ls /dev/input' again, and if there's more events than at the start you're good to run this program.
If there's no more events than when you started, and you don't have any other connection for the controller, than the controller is incompatible.
If there are other connection methods, try them.
If worst case everything still does not connect, try powering on and off the pi and redo all the steps above until it works.

### Actions
- Right Trigger accelerate/forward
- Left Trigger reverse
- Left Joystick + Left buttons direction
- Right Joystick ultrasonic movement
- Right Bumper increase top speed
- Left Bumper decrease top speed
