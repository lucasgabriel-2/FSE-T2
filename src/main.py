from comunicacaoUart.uart import Uart
from comunicacaoGpio.elevador import Elevador
import threading
from time import sleep
from collections import deque

class Main:

    def atualizaValorEncoderEplotaGraficoPWM(self):
        while True:
            self.lock.acquire()
            valorEncoder = self.instancia_uart.leituraValorEncoder()
            self.instancia_elevador.atualizaValorEncoderElevador(valorEncoder)
            self.instancia_uart.envioSinalPWM(int(self.instancia_elevador.pidDutyCycle))
            self.lock.release()
            sleep(0.16)

    def atualizaLCDeDashboard(self):
        while True:
            self.lock.acquire()
            self.instancia_elevador.configuraLCDeDashBoard()
            self.lock.release()
            sleep(1)

    def processaComandosUsuario(self):
        if(len(self.queue) != 0):
            botaoApertado = self.queue.popleft()

            if botaoApertado == (b'\x00'):
                self.moveElevador(self.instancia_elevador.andar_terreo)

            if botaoApertado == (b'\x01'):
                self.moveElevador(self.instancia_elevador.andar_1)

            if botaoApertado == (b'\x02'):
                self.moveElevador(self.instancia_elevador.andar_1)

            if botaoApertado == (b'\x03'):
                self.moveElevador(self.instancia_elevador.andar_2)

            if botaoApertado == (b'\x04'):
                self.moveElevador(self.instancia_elevador.andar_2)

            if botaoApertado == (b'\x05'):
                self.moveElevador(self.instancia_elevador.andar_3)

            if botaoApertado == (b'\x06'):                
                self.instancia_elevador.freiaElevador()
                print("O modo de emergencia foi acionado, aguarde 5s até que a equeipe de resgate te leve ate o terreo")
                sleep(5)
                self.moveElevador(self.instancia_elevador.andar_terreo)
                self.instancia_elevador.estadoDeEmergencia = True

            if botaoApertado == (b'\x07'):
                self.moveElevador(self.instancia_elevador.andar_terreo)

            if botaoApertado == (b'\x08'):
                self.moveElevador(self.instancia_elevador.andar_1)

            if botaoApertado == (b'\x09'):
                self.moveElevador(self.instancia_elevador.andar_2)

            if botaoApertado == (b'\x0A'):
                self.moveElevador(self.instancia_elevador.andar_3)
            
    def trataComandosUsuario(self, valorBotoes):

        if valorBotoes[0] == False:
            self.queue.append(b'\x00')
            
        if valorBotoes[1] == False:
            self.queue.append(b'\x01')

        if valorBotoes[2] == False:
            self.queue.append(b'\x02')

        if valorBotoes[3] == False:
            self.queue.append(b'\x03')

        if valorBotoes[4] == False:
            self.queue.append(b'\x04')

        if valorBotoes[5] == False:
            self.queue.append(b'\x05')

        if valorBotoes[6] == False:
            self.queue.append(b'\x06')

        if valorBotoes[7] == False:
            self.queue.append(b'\x07')

        if valorBotoes[8] == False:
            self.queue.append(b'\x08')

        if valorBotoes[9] == False:
            self.queue.append(b'\x09')

        if valorBotoes[10] == False:
            self.queue.append(b'\x0A')

        thread4 = threading.Thread(target=self.processaComandosUsuario)
        thread4.start()
    
    def verificaComandoUsuario(self):
        while True:
            self.lock.acquire()
            registradoresAtuais = self.instancia_uart.leituraValorResgistradores()

            if registradoresAtuais != self.registradores:
            
                presionaBotaoTerreoSobe = (self.registradores[0] == registradoresAtuais[0])
                presionaBotao1AndDesc = (self.registradores[1] == registradoresAtuais[1])
                presionaBotao1AndSobe = (self.registradores[2] == registradoresAtuais[2])
                presionaBotao2AndDesc = (self.registradores[3] == registradoresAtuais[3])
                presionaBotao2AndSobe = (self.registradores[4] == registradoresAtuais[4])
                presionaBotao3AndDesc = (self.registradores[5] == registradoresAtuais[5])
                presionaBotaoElevadorEmerg = (self.registradores[6] == registradoresAtuais[6])
                presionaBotaoElevadorT = (self.registradores[7] == registradoresAtuais[7])
                presionaBotaoElevador1 = (self.registradores[8] == registradoresAtuais[8])
                presionaBotaoElevador2 = (self.registradores[9] == registradoresAtuais[9])
                presionaBotaoElevador3 = (self.registradores[10] == registradoresAtuais[10])

                valorBotoes = [presionaBotaoTerreoSobe, presionaBotao1AndDesc, presionaBotao1AndSobe, presionaBotao2AndDesc, presionaBotao2AndSobe,
                                    presionaBotao3AndDesc, presionaBotaoElevadorEmerg, presionaBotaoElevadorT, presionaBotaoElevador1, presionaBotaoElevador2,
                                    presionaBotaoElevador3]
                
                self.trataComandosUsuario(valorBotoes)

            self.registradores = registradoresAtuais
            self.lock.release()
            sleep(0.01)

    def atualizaPidElevador(self):
        while True:
            self.lock.acquire()
            self.instancia_elevador.pidDutyCycle = self.instancia_elevador.instancia_pid.pid_controle(self.instancia_elevador.valorEncoder)

            # O pidDutyCycle pode retorna um valor negativo para o elevador descer, porém DutyCycle aceita apenas valores positivos
            if self.instancia_elevador.pidDutyCycle < 0:
                self.instancia_elevador.pidDutyCycle = abs(self.instancia_elevador.pidDutyCycle)
                # Configuração de descida
                self.instancia_elevador.desceElevador()
                self.instancia_elevador.instancia_potenciaMotor.acionaMotor(self.instancia_elevador.pidDutyCycle)
                self.instancia_elevador.estado = "Descendo"

            else:
                # Configuração de subida
                self.instancia_elevador.sobeElevador()
                self.instancia_elevador.instancia_potenciaMotor.acionaMotor(self.instancia_elevador.pidDutyCycle)
                self.instancia_elevador.estado = "Subindo"
            self.lock.release()
            sleep(0.05)

            if self.instancia_elevador.andar_terreo == self.instancia_elevador.posicaoAndarObjetivo:
                sensor = self.instancia_elevador.instancia_sensor_terreo
            if self.instancia_elevador.andar_1 == self.instancia_elevador.posicaoAndarObjetivo:
                sensor = self.instancia_elevador.instancia_sensor_1_andar
            if self.instancia_elevador.andar_2 == self.instancia_elevador.posicaoAndarObjetivo:
                sensor = self.instancia_elevador.instancia_sensor_2_andar
            if self.instancia_elevador.andar_3 == self.instancia_elevador.posicaoAndarObjetivo:
                sensor = self.instancia_elevador.instancia_sensor_3_andar

            if self.instancia_elevador.pidDutyCycle == 0 or sensor.detectaEvento():
                self.instancia_elevador.freiaElevador()
                
                if self.instancia_elevador.posicaoAndarObjetivo == self.instancia_elevador.andar_terreo:
                    self.instancia_elevador.andarAtual = "T"

                if self.instancia_elevador.posicaoAndarObjetivo == self.instancia_elevador.andar_terreo:
                    self.instancia_elevador.andarAtual = "1"

                if self.instancia_elevador.posicaoAndarObjetivo == self.instancia_elevador.andar_terreo:
                    self.instancia_elevador.andarAtual = "2"    

                if self.instancia_elevador.posicaoAndarObjetivo == self.instancia_elevador.andar_terreo:
                    self.instancia_elevador.andarAtual = "3"
                break
            
    def moveElevador(self, novaPosicaoAndarObjetivo):
        self.instancia_elevador.modificaAndarObjetivo(novaPosicaoAndarObjetivo)

        # PID
        self.instancia_elevador.instancia_pid.pid_configura_constantes(0.1, 0.01, 0.50)

        # PID - Atualizo o valor do andar que quero ir (valor do encoder) 
        self.instancia_elevador.instancia_pid.pid_atualiza_referencia(self.instancia_elevador.posicaoAndarObjetivo)

        # PID - Atualizo o valor do andar em que estou (valor atual do encoder)    
        # Retorna o PID que devo colocar no meu DutyCycle da Potencia do motor
        self.atualizaPidElevador()

    def __init__(self):
        try:
            self.queue = deque()
            self.lock = threading.Lock()
            self.instancia_uart = Uart()
            self.instancia_elevador = Elevador(self.instancia_uart)
            self.instancia_elevador.deixaElevadorLivre()

            # Calibração
            self.instancia_elevador.calibraElevador()

            self.instancia_elevador.instancia_lcd.lcd_clear()
            self.instancia_elevador.instancia_lcd.lcd_display_string("Calibragem", 1)
            self.instancia_elevador.instancia_lcd.lcd_display_string("concluida", 2)
            sleep(3)
            self.instancia_elevador.instancia_lcd.lcd_clear()

            # Salva os valores dos registradores
            self.registradores  = self.instancia_uart.leituraValorResgistradores()

            # Thread (atualiza valor temperatura (dash e lcd) e andar e estado (lcd) a cada 1s)
            thread1 = threading.Thread(target=self.atualizaLCDeDashboard)

            # Thread (ler grafico de pwm e atualiza a variável self.valorEncoder do elevador a cada 200ms )
            thread2 = threading.Thread(target=self.atualizaValorEncoderEplotaGraficoPWM)

            # Thread (le comandos do usario a cada 50ms adiciona na fila e os trata)
            thread3 = threading.Thread(target=self.verificaComandoUsuario)

            thread1.start()
            thread2.start()
            thread3.start()

            # Posiciona elevador no andar Terreo para que o primeiro usuário possa utilizar
            self.moveElevador(self.instancia_elevador.andar_terreo)

        except KeyboardInterrupt:
            # Sensor de temperatura (I2C)
            self.instancia_uart.instancia_i2cTemperatura.i2c.deinit()

            # Display (I2C)
            self.instancia_elevador.instancia_lcd.lcd_clear()
            self.instancia_elevador.instancia_lcd.lcd_device.close()

            # GPIO/PWM
            self.instancia_elevador.instancia_sensor_terreo.desligaSensor()
            self.instancia_elevador.instancia_sensor_1_andar.desligaSensor()
            self.instancia_elevador.instancia_sensor_2_andar.desligaSensor()
            self.instancia_elevador.instancia_sensor_3_andar.desligaSensor()
            self.instancia_elevador.instancia_motorDescida.desligaMotor()
            self.instancia_elevador.instancia_motorSubida.desligaMotor()
            self.instancia_elevador.instancia_potenciaMotor.desligaPotenciaDoMotor()

            # UART
            self.instancia_uart.close()

Main()