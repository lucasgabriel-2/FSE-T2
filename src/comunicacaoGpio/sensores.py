import RPi.GPIO as gpio

# Configurações gerais 
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

class Sensor:
    def __init__(self, pino_gpio):
        self.pino = pino_gpio
        gpio.setup(self.pino, gpio.IN, pull_up_down = gpio.PUD_DOWN)
        gpio.add_event_detect(self.pino, gpio.RISING)

    def detectaEvento(self):
        return gpio.event_detected(self.pino)
    
    def desligaSensor(self):
        gpio.cleanup()