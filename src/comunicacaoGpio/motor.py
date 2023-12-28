import RPi.GPIO as gpio

# Configurações gerais 
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

class Motor:
    def __init__(self, pino_gpio):
        self.gpio = gpio
        self.pino = pino_gpio
        self.gpio.setup(self.pino,gpio.OUT)
    
    def ativaMotor(self):
        self.gpio.output(self.pino, 1)

    def desativaMotor(self):
        self.gpio.output(self.pino, 0)    

    def desligaMotor(self):
        self.gpio.cleanup()