import random
import keyboard
import sys

""" Self-defined contants """
PIN_BTN = 0
PIN_RED_LED_0 = 1
PIN_RED_LED_1 = 2
PIN_RED_LED_2 = 3
PIN_BLUE_LED = 4
valid_pins = {PIN_BTN, PIN_RED_LED_0, PIN_RED_LED_1, PIN_RED_LED_2, PIN_BLUE_LED}

NO_SIGNAL = -1
NO_SETUP = -1
RANDOMNESS = 0.01


def show_error_and_exit(error_message):
    print(error_message)
    sys.exit()


class GPIOSimulator:
    """ Simulator of Raspberry Pi GPIO for Project 1 """

    def __init__(self):
        self.pin_states = [NO_SIGNAL] * len(valid_pins)
        self.pin_modes = [NO_SETUP] * len(valid_pins)

        # GPIO constants
        self.PUD_DOWN = 1
        self.PUD_UP = 0
        self.LOW = 0
        self.HIGH = 1
        self.IN = 0
        self.OUT = 1

    def setup(self, pin, mode, state=0):
        """ setup the initial mode and state of a specific pin """
        if not (pin in valid_pins):
            show_error_and_exit("This pin is out of range! Please use valid pins!")
        else:
            if not (mode in {self.IN, self.OUT}):
                print('invalid mode')
                sys.exit()
            else:
                self.pin_modes[pin] = mode
                if mode == self.IN:
                    if not (state in {self.PUD_UP, self.PUD_DOWN, NO_SIGNAL}):
                        show_error_and_exit('invalid input state!')
                    else:
                        self.pin_states[pin] = state
                else:
                    if not (state in {self.LOW, self.HIGH, NO_SIGNAL}):
                        show_error_and_exit('invalid output state!')
                    else:
                        self.pin_states[pin] = state

    def cleanup(self):
        """ reset GPIO, i.e., clear mode and state of each pin """
        for pin in valid_pins:
            self.pin_modes[pin] = NO_SETUP
            self.pin_states[pin] = NO_SIGNAL

    def input(self, pin):
        """
        Read the state of the given pin.
        """
        if pin is not PIN_BTN:
            show_error_and_exit("Only PIN_BTN is allowed!")
        else:
            if random.random() < RANDOMNESS:
                self.pin_states[PIN_BTN] = random.choice([self.PUD_DOWN, self.PUD_UP])
            else:
                if keyboard.is_pressed('space'):
                    self.pin_states[PIN_BTN] = self.PUD_DOWN
                else:
                    self.pin_states[PIN_BTN] = self.PUD_UP

        return self.pin_states[PIN_BTN]

    def output(self, pin, state):
        """
        Set the state of the given pin.
        If pin is not among the LEDs or pin_modes[pin] is not OUT, do nothing.
        Otherwise use print() to show the LED action on screen and set pin_states[pin] to state
        """
        led_dict = {PIN_RED_LED_0: "The first red LED",
                    PIN_RED_LED_1: "The second red LED",
                    PIN_RED_LED_2: "The third red LED",
                    PIN_BLUE_LED: "The blue LED"}

        if not (pin in led_dict.keys()):
            show_error_and_exit("Output pin is out of range! Please use valid LED pins!")
        else:
            if not (state in {self.LOW, self.HIGH}):
                show_error_and_exit('invalid LED state!')
            else:
                state_str_dict = {self.HIGH: "ON", self.LOW: "OFF"}
                if self.pin_states[pin] != state:
                    verb = 'becomes'
                else:
                    verb = 'is still'
                print("%s %s %s." % (led_dict[pin], verb, state_str_dict[state]))
                self.pin_states[pin] = state
