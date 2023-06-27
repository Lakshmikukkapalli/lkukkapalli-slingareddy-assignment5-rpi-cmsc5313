import RPi.GPIO as GPIO
from time import sleep
from smbus import SMBus
import constant
import firebase_setup

# Setup firebase
collection = firebase_setup.db.collection(constant.COLLECTION_NAME)
doc_ref = collection.document(constant.JOYSTICK_STATUS)
doc_center = collection.document(constant.JOYSTICK_CENTER)


# Update firestore
def update_firestore(left, right, top, bottom):
    print('Updating firestore')
    print({
        u'LEFT': left,
        u'RIGHT': right,
        u'TOP': top,
        u'BOTTOM': bottom,
    })
    if left:
        turn_on_led(LEFT)
    elif right:
        turn_on_led(RIGHT)
    elif top:
        turn_on_led(Top)
    elif bottom:
        turn_on_led(BOTTOM)
    else:
        turn_on_led(0)

    doc_ref.update({
         u'LEFT': left,
         u'RIGHT': right,
         u'TOP': top,
         u'BOTTOM': bottom,
     })


# Update firestore center
def update_firestore_center(center):
    print({
        u'CENTER': center,
    })
    doc_center.update({
        u'CENTER': center,
    })


# ADS7830 address, 0x4b(74)
ads7830_commands = (0x84, 0xc4, 0x94, 0xd4, 0xa4, 0xe4, 0xb4, 0xf4)


# Read the ADS7830 chip using the I2C bus
def read_ads7830(pin):
    bus.write_byte(0x4b, ads7830_commands[pin])
    return bus.read_byte(0x4b)


# Setup the GPIO pins
GPIO.setmode(GPIO.BCM)
delayTime = 0.1

# start an SMBus object
bus = SMBus(1)

# Setup the GPIO pin for the button on the joystick
JOYSTICK_BUTTON = 18
GPIO.setup(JOYSTICK_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button_press_state = 1

# Setup the LED pins
LEFT = 5
RIGHT = 6
Top = 13
BOTTOM = 19
CENTER = 26

GPIO.setup(LEFT, GPIO.OUT)
GPIO.setup(RIGHT, GPIO.OUT)
GPIO.setup(Top, GPIO.OUT)
GPIO.setup(BOTTOM, GPIO.OUT)
GPIO.setup(CENTER, GPIO.OUT)


# Process joystick button click
def process_joystick_button_click():
    global button_press_state
    button_state_current = GPIO.input(JOYSTICK_BUTTON)
    #print("Button status ", button_state_current)

    if button_state_current == 0 and button_press_state == 1:
        button_press_state = 0
        update_firestore_center(True)
        GPIO.output(CENTER, True)

    elif button_state_current == 1 and button_press_state == 0:
        button_press_state = 1
        update_firestore_center(False)
        GPIO.output(CENTER, False)


def turn_on_led(led):
    GPIO.output(LEFT, False)
    GPIO.output(RIGHT, False)
    GPIO.output(Top, False)
    GPIO.output(BOTTOM, False)
    if led != 0:
        GPIO.output(led, True)


old_satus_dict = {
    'LEFT': False,
    'RIGHT': False,
    'TOP': False,
    'BOTTOM': False,
}


def process_joystick_status():
    global old_satus_dict
    x_value = read_ads7830(7)
    y_value = read_ads7830(6)

    # print out values
    #print('X, Y and Button Values: ', x_value, y_value)

    left = False
    right = False
    top = False
    bottom = False

    if x_value < 100:
        left = True
        GPIO.output(LEFT, True)
    else:
        GPIO.output(LEFT, False)

    if x_value > 150:
        right = True
        GPIO.output(RIGHT, True)
    else:
        GPIO.output(RIGHT, False)

    if y_value < 100:
        top = True
        GPIO.output(Top, True)
    else:
        GPIO.output(Top, False)

    if y_value > 150:
        bottom = True
        GPIO.output(BOTTOM, True)
    else:
        GPIO.output(BOTTOM, False)

    if left != old_satus_dict['LEFT'] or right != old_satus_dict['RIGHT'] or top != old_satus_dict['TOP'] or bottom != \
            old_satus_dict['BOTTOM']:
        update_firestore(left, right, top, bottom)
        old_satus_dict = {
            'LEFT': left,
            'RIGHT': right,
            'TOP': top,
            'BOTTOM': bottom,
        }


# where all the action happens
try:
    while True:
        process_joystick_button_click()
        process_joystick_status()
        sleep(delayTime)

except KeyboardInterrupt:
    GPIO.cleanup()
except OSError as e:
    print(e)
    GPIO.cleanup()    