import RPi.GPIO as gpio

# Configurações gerais 
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

class PotenciaDoMotor:
    def __init__(self, pino_gpio):
        self.pino = pino_gpio
        gpio.setup(self.pino,gpio.OUT)
        self.pwmMotor = gpio.PWM(self.pino, 1000)
        self.pwmMotor.start(0)
    
    def acionaMotor(self, pid):
            self.pwmMotor.ChangeDutyCycle(pid)
    
    def desligaPotenciaDoMotor(self):
        self.pwmMotor.stop()
        gpio.cleanup()