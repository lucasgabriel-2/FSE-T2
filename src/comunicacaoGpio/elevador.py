from comunicacaoUart.uart import Uart
from comunicacaoLcd.lcd import Lcd
from comunicacaoGpio.pid import PID
from comunicacaoGpio.sensores import Sensor
from comunicacaoGpio.motor import Motor
from comunicacaoGpio.potenciaDoMotor import PotenciaDoMotor
from time import sleep

class Elevador:

    def __init__(self, Uart):
        #Uart
        self.instancia_uart = Uart
        
        # Encoder
        self.valorEncoder = 0

        # Temperatura
        self.valorTemperatura = 0

        # Estado
        self.estado = "Parado"
        self.andarAtual = "T"
        self.estadoDeEmergencia = False
        
        # PID
        self.instancia_pid = PID()
        self.pidDutyCycle = 0

        # Sensores
        self.instancia_sensor_terreo = Sensor(18)
        self.instancia_sensor_1_andar = Sensor(23)
        self.instancia_sensor_2_andar = Sensor(24)
        self.instancia_sensor_3_andar = Sensor(25)

        # Motores
        self.instancia_motorSubida = Motor(20)
        self.instancia_motorDescida = Motor(21)
        
        # Potencia do motor
        self.instancia_potenciaMotor = PotenciaDoMotor(12)

        # Andares
        self.andar_terreo = 0
        self.andar_1 = 0
        self.andar_2 = 0
        self.andar_3 = 0
        self.posicaoAndarObjetivo = 0

        # Display
        self.instancia_lcd = Lcd()

    def modificaAndarObjetivo(self, novaPosicaoAndarObjetivo):
        self.posicaoAndarObjetivo = novaPosicaoAndarObjetivo
        return self.posicaoAndarObjetivo

    def atualizaValorEncoderElevador(self, atualValorDoEncoder):
        self.valorEncoder = atualValorDoEncoder
        return self.valorEncoder
    
    def freiaElevador(self):
            # Configuração de freio
            self.instancia_motorSubida.ativaMotor()
            self.instancia_motorDescida.ativaMotor()

    def deixaElevadorLivre(self):
            # Configuração do elevador livre
            self.instancia_motorSubida.desativaMotor()
            self.instancia_motorDescida.desativaMotor()
    
    def sobeElevador(self):
            # Configuração do elevador subindo
            self.instancia_motorSubida.ativaMotor()
            self.instancia_motorDescida.desativaMotor()

    def desceElevador(self):
            # Configuração do elevador descendo
            self.instancia_motorSubida.desativaMotor()
            self.instancia_motorDescida.ativaMotor()

    def calibraElevador(self):

        self.posicaoAndarObjetivo = 25500
        # Configuração de subida
        self.instancia_motorSubida.ativaMotor()
        self.instancia_motorDescida.desativaMotor()

        # Para calibrar usa o valor 1 no pwm, a fim de detectar os sensores
        self.pidDutyCycle = 1
        self.instancia_potenciaMotor.acionaMotor(self.pidDutyCycle)
        
        self.instancia_lcd.lcd_display_string("Calibrando...", 1)
        while True :
            if self.instancia_sensor_terreo.detectaEvento():
                self.andar_terreo = self.instancia_uart.leituraValorEncoder()
                print("andar terreo", end=" ")
                print(self.andar_terreo)

            if self.instancia_sensor_1_andar.detectaEvento():
                self.andar_1 = self.instancia_uart.leituraValorEncoder()
                print("primeiro andar", end=" ")
                print(self.andar_1)

            if self.instancia_sensor_2_andar.detectaEvento():
                self.andar_2 = self.instancia_uart.leituraValorEncoder()
                print("segundo andar", end=" ")
                print(self.andar_2)

            if self.instancia_sensor_3_andar.detectaEvento():
                self.andar_3 = self.instancia_uart.leituraValorEncoder()   
                print("terceiro andar", end=" ")
                print(self.andar_3)   
                self.deixaElevadorLivre()             
                break
            sleep(0.001)

    def verificaAndarAtualeAtualizaDashboard(self):

        if self.posicaoAndarObjetivo == self.andar_terreo:
            self.andarAtual = "T"
            self.instancia_uart.escreveNoRegistrador(b'\x00', b'\x00')
            self.instancia_uart.escreveNoRegistrador(b'\x07', b'\x00')
            
        if self.posicaoAndarObjetivo == self.andar_1:
            self.andarAtual = "1"
            self.instancia_uart.escreveNoRegistrador(b'\x01', b'\x00')
            self.instancia_uart.escreveNoRegistrador(b'\x02', b'\x00')
            self.instancia_uart.escreveNoRegistrador(b'\x08', b'\x00')

        if self.posicaoAndarObjetivo == self.andar_2:
            self.andarAtual = "2"    
            self.instancia_uart.escreveNoRegistrador(b'\x03', b'\x00')
            self.instancia_uart.escreveNoRegistrador(b'\x04', b'\x00')
            self.instancia_uart.escreveNoRegistrador(b'\x09', b'\x00')

        if self.posicaoAndarObjetivo == self.andar_3:
            self.andarAtual = "3"
            self.instancia_uart.escreveNoRegistrador(b'\x05', b'\x00')
            self.instancia_uart.escreveNoRegistrador(b'\x0A', b'\x00')

        if self.estadoDeEmergencia == True:
             self.estadoDeEmergencia = False
             self.instancia_uart.escreveNoRegistrador(b'\x06', b'\x00')
        return self.andarAtual
 
    def verificaEstadoAtual(self):

        diferenca = self.valorEncoder - self.posicaoAndarObjetivo
        if self.posicaoAndarObjetivo == self.valorEncoder or -50 <= diferenca <= 50:
                self.estado = "Parado"
                return "Parado"
        if self.posicaoAndarObjetivo > self.valorEncoder:
                self.estado = "Subindo"
                return "Subindo"
        if self.posicaoAndarObjetivo < self.valorEncoder:
                self.estado = "Descendo"
                return "Descendo"

    def configuraLCDeDashBoard(self):

        andarAtual = self.verificaAndarAtualeAtualizaDashboard()
        estadoAtual = self.verificaEstadoAtual()
        mensagemDisplay1 = "{}: {} ".format(andarAtual, estadoAtual)
        self.instancia_lcd.lcd_display_string(mensagemDisplay1, 1)

        self.valorTemperatura = self.instancia_uart.escreveTemperatura()
        temperaturaAtual = self.valorTemperatura
        temperaturaAtual = "{:.2f}".format(temperaturaAtual)
        mensagemDisplay2 = "Temp.: {} C".format(temperaturaAtual)
        self.instancia_lcd.lcd_display_string(mensagemDisplay2, 2)