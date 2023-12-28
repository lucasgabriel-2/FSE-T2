import board
import adafruit_bmp280

class I2c:
    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c, 0X76)

    def lerTemperatura(self):
        temperatura = self.sensor.temperature
        return temperatura