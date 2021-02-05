""" Template for Project 1: Morse code """

from GPIOSimulator_v1 import *
import time

GPIO = GPIOSimulator()
GPIO.setup(PIN_BTN, GPIO.IN, GPIO.PUD_UP)

MORSE_CODE = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g',
              '....': 'h', '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n',
              '---': 'o', '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u',
              '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y', '--..': 'z', '.----': '1',
              '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
              '---..': '8', '----.': '9', '-----': '0'}

# Chosen interval.
T = 0.350

text_encoded = "... --- ..."

# Specific intervals of time to register what type of signal is being sent
DURATIONS = {'.': T, '-': 3 * T, 'Short pause': 1.75 * T, 'Medium pause': 5 * T, 'Long pause': 8 * T,
             'Very long pause': 12.5 * T}


class MorseDecoder:
    """ Morse code class """
    __current_word: str

    def __init__(self):
        """ initialize your class """
        self.__current_symbol = ""  # Dots and dashes that together becomes a letter or number
        self.__current_word = ""  # Word composed of multiple letters created by the dots/dashes
        self.__sentence = ""  # Final sentence
        self.loop = False  # Boolean value for deciding if the loop should continue or not, only declared in constructor

    def reset(self):
        """ reset the variable for a new run """
        self.__current_word = ""
        self.__current_symbol = ""
        self.__sentence = ""

    def decoding_loop(self):
        """
        the main decoding loop.
        Continue to read input from GPIO with intervals to avoid collision of signals.
        Decide how long button is pressed with a current_time.

        Based on length of the current_time, change signal value to dot/dash.
        Based on current_time_pause decide if the time between signals is a short/medium/long pause
        """
        self.loop = True
        prev_signal = 0  # Start signal set to 0
        start_time = time.time()  # start_time started before while loop
        end_time = time.time()  # End time also started before loop
        while self.loop:

            current_signal = self.read_one_signal()

            # If button is pressed signal == 1, and if the prev_signal == 0 it means there has been a new message.
            if current_signal == 1 and prev_signal == 0:
                start_time = time.time()
                current_time_pause = start_time - end_time

                # Depending on how long since last button press, decide what type of pause it is
                pause = ""
                if current_time_pause >= DURATIONS['Very long pause']:
                    pause = "Very long pause"
                elif current_time_pause >= DURATIONS['Long pause']:
                    pause = "Long pause"
                elif current_time_pause >= DURATIONS['Medium pause']:
                    pause = "Medium pause"

                self.process_signal(pause)

            # If signal is 0 and previous signal is 1 it means that the button was pressed and has now been released.
            if current_signal == 0 and prev_signal == 1:
                end_time = time.time()
                current_time = end_time - start_time

                # Depending on how long the PIN_BTN was pressed decide whether it is a dot or a dash.
                message = ""
                if current_time >= DURATIONS['-']:
                    message = '-'
                elif current_time >= DURATIONS['.']:
                    message = '.'

                self.process_signal(message)

            prev_signal = current_signal
            time.sleep(DURATIONS['Short pause'])  # 1 tick every short pause

    @staticmethod
    def read_one_signal():
        """ read a signal from Raspberry Pi"""
        return GPIO.input(PIN_BTN)

    def process_signal(self, signal):
        """ handle the signals using corresponding functions """

        if signal == "." or signal == "-":
            self.update_current_symbol(signal)

            # It seems that the project description is mirrored, it says there are three BLUE LEDs and one RED LED
            # But in our case theres three RED LEDs, so its reversed.

            # self.handle_led(signal) # <-------------

        elif signal == 'Medium pause':
            self.handle_symbol_end()

        elif signal == 'Long pause':
            self.handle_word_end()

        elif signal == "Very long pause":
            self.show_message()

    @staticmethod
    def handle_led(signal):
        """Turn on and off led lights corresponding to what type of signal is being sent."""
        if signal == ".":
            GPIO.output(PIN_BLUE_LED, True)
            time.sleep(DURATIONS['Medium pause'])
            GPIO.output(PIN_BLUE_LED, False)

        elif signal == "-":
            GPIO.output(PIN_RED_LED_0, True)
            GPIO.output(PIN_RED_LED_1, True)
            GPIO.output(PIN_RED_LED_2, True)
            time.sleep(DURATIONS['Medium pause'])
            GPIO.output(PIN_RED_LED_0, False)
            GPIO.output(PIN_RED_LED_1, False)
            GPIO.output(PIN_RED_LED_2, False)

        time.sleep(DURATIONS['Short pause'])

    def update_current_symbol(self, signal):
        """ append the signal to current symbol code """
        self.__current_symbol += signal
        print("Current symbol: " + self.__current_symbol)

    def handle_symbol_end(self):
        """ process when a symbol ending appears """
        if self.__current_symbol == "":
            return

        elif self.__current_symbol not in MORSE_CODE:
            print("Do not recognize your symbol")
            print("Resetting symbol")

        else:
            translated_letter = MORSE_CODE[self.__current_symbol]  # Handle what the letter/number the symbol is
            self.update_current_word(translated_letter)
        self.__current_symbol = ""

    def update_current_word(self, letter):
        self.__current_word += letter
        print("Current word: " + self.__current_word)

    def handle_word_end(self):
        """process when a word ending appears. If current_word is blank don't add it"""
        self.handle_symbol_end()
        print("Final word: " + self.__current_word)

        if self.__current_word != "":
            self.__sentence += " " + self.__current_word
        self.__current_word = ""

    def handle_reset(self):
        """ process when a reset signal received """
        self.reset()
        GPIO.cleanup()

    def show_message(self):
        """
        print the current decoded message.
        Ask user if he/she wants to continue. If no then stop loop with loop = False and start main again
        """

        self.handle_word_end()
        print("Current message: " + self.__sentence)
        print("                 ")

        # Temporary stop the loop, if the user says no then continue to reset, if user says yes, restart loop.
        # This is to avoid the decoder being confused about current and previous signal
        self.loop = False
        if input("Do you want to continue? (y/n): ") == "n":
            self.handle_reset()

        else:
            self.decoding_loop()

    def start_program(self):
        """Output message to users who wishes to use the MorseDecoder"""
        print("Welcome to Morse Coder program!")
        print(f"For '.' press space for approx. ({round(DURATIONS['.'], 2)}s) for '-' press space for approx "
              f"({round(DURATIONS['-'], 2)}s)")
        print(f"""
        Short pauses are between symbols ({round(DURATIONS['Short pause'], 2)}s).

        Medium pauses are between letters ({round(DURATIONS['Medium pause'], 2)}s).

        Long pauses are between words ({round(DURATIONS['Long pause'], 2)}s).

        Very long pauses are for ending the message ({round(DURATIONS['Very long pause'], 2)}s).
        """)

        if input("Do you want to send a morse code? (y/n): ") == "y":
            self.decoding_loop()


def main():
    """
    The main function
    Keyboard interrupt is for when using the program in CMD, then you can press Ctrl + C
    When using in PyCharm or IDE, you can instead wait for very long pause.
    """
    try:
        decoder = MorseDecoder()
        decoder.start_program()
    except KeyboardInterrupt:
        print("Keyboard interrupt; quit the program")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
