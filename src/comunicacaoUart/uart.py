import serial
import time
import struct
from comunicacaoUart.crc import Crc
from leituraTemperatura.i2c import I2c

class Uart:
    
    def __init__(self):
        self.port = "/dev/serial0"
        self.baudrate = 115200
        self.timeout = 1
        self.matricula = b'\x02'+ b'\x01' + b'\x02' + b'\x03'
        self.UART = serial.Serial(self.port, self.baudrate, timeout = self.timeout)
        self.instancia_i2cTemperatura  = None
        self.instancia_crc = Crc()

    def envioDeMensagem(self, mensagem, tipoDeMensagem):
        #limpa o buffer utilizado para trazer os bytes
        # self.UART.flushInput()

        retorno = None
        if self.UART.isOpen():
            self.UART.write(mensagem)
            time.sleep(0.049)

            if(tipoDeMensagem == "lerEncoder"):
                # 9 = tamanho da mensagem (0x00 0x23 0xC1 + int (4 bytes) + crc (2 bytes))
                retorno = self.UART.read(9)
            if(tipoDeMensagem == "lerRegistradores"):
                # 15 = tamanho da mensagem (0x00 0x03 (0x00 ao 0x0A) + crc (2bytes))
                retorno = self.UART.read(15)
            if(tipoDeMensagem == "escreverRegistrador"):
                # 5 = tamanho da mensagem (0x00 0x03 (1 byte, o qual foi escrito) + crc (2bytes)
                retorno =  self.UART.read(5)
            if(tipoDeMensagem == "enviaTemperatura"):
                # 5 = tamanho da mensagem (0x00 0x16 0xD1 + crc (2bytes))
                retorno = self.UART.read(5)
            if(tipoDeMensagem == "envioSinalPWM"):
                # 5 = tamanho da mensagem (0x01 0x16 0xC2 + crc (2bytes))
                retorno = self.UART.read(5)

        return retorno

    def leituraValorEncoder(self):
        mensagem = b'\x01' + b'\x23' + b'\xC1' + self.matricula
        crc = self.instancia_crc.calcular_crc(mensagem)
        mensagem += crc

        resposta = self.envioDeMensagem(mensagem, "lerEncoder")
        # pega o intervalo de 3-7 que corresponde ao valor do encoder (valor entre 0 e 25500)
        # valorEncoder = int.from_bytes(resposta[3:7], byteorder="big", signed = False)
        valorEncoder = struct.unpack("i", resposta[3:7])[0]

        validadeCRC = self.instancia_crc.verificaCRC(resposta)

        if validadeCRC:
           return valorEncoder
        
        time.sleep(1)
        print("O valor do crc veio incorreto, tentando novamente...")
        return self.leituraValorEncoder()

    def leituraValorResgistradores(self):
        mensagem = b'\x01' + b'\x03' + b'\x00'+ b'\x0B' + self.matricula
        crc = self.instancia_crc.calcular_crc(mensagem)
        mensagem += crc

        resposta = self.envioDeMensagem(mensagem, "lerRegistradores")

        validadeCRC = self.instancia_crc.verificaCRC(resposta)

        if validadeCRC:
            # pega o intervalo de [2-14) que corresponde ao valor dos registradores
            valorRegisradores0 = int.from_bytes(resposta[2:3], byteorder="big", signed = False)
            valorRegisradores1 = int.from_bytes(resposta[3:4], byteorder="big", signed = False)
            valorRegisradores2 = int.from_bytes(resposta[4:5], byteorder="big", signed = False)
            valorRegisradores3 = int.from_bytes(resposta[5:6], byteorder="big", signed = False)
            valorRegisradores4 = int.from_bytes(resposta[6:7], byteorder="big", signed = False)
            valorRegisradores5 = int.from_bytes(resposta[7:8], byteorder="big", signed = False)
            valorRegisradores6 = int.from_bytes(resposta[8:9], byteorder="big", signed = False)
            valorRegisradores7 = int.from_bytes(resposta[9:10], byteorder="big", signed = False)
            valorRegisradores8 = int.from_bytes(resposta[10:11], byteorder="big", signed = False)
            valorRegisradores9 = int.from_bytes(resposta[11:12], byteorder="big", signed = False)
            valorRegisradoresA = int.from_bytes(resposta[12:13], byteorder="big", signed = False)

            valorRegisradores = [valorRegisradores0, valorRegisradores1, valorRegisradores2, valorRegisradores3, valorRegisradores4,
                                valorRegisradores5, valorRegisradores6, valorRegisradores7, valorRegisradores8, valorRegisradores9,
                                valorRegisradoresA]

            return valorRegisradores

        time.sleep(1)
        print("O valor do crc veio incorreto, tentando novamente...")
        return self.leituraValorResgistradores()

    #Registrador e Dado em hexadecimal
    def escreveNoRegistrador(self, enderecoRegistrador, dado):
        mensagem = b'\x01' + b'\x06' + enderecoRegistrador + b'\x01' + dado + self.matricula
        crc = self.instancia_crc.calcular_crc(mensagem)
        mensagem += crc

        resposta = self.envioDeMensagem(mensagem, "escreverRegistrador")
        
        validadeCRC = self.instancia_crc.verificaCRC(resposta)
        
        if validadeCRC:
            valorResgistador = int.from_bytes(resposta[2:3], byteorder="big", signed = False)
            return valorResgistador
        
        time.sleep(1)
        print("O valor do crc veio incorreto, tentando novamente...")
        return self.escreveNoRegistrador(enderecoRegistrador, dado)

    def escreveTemperatura(self):
        self.instancia_i2cTemperatura = I2c()
        temperatura = self.instancia_i2cTemperatura.lerTemperatura()
        temperatura_bytes = struct.pack('<f', temperatura)

        mensagem = b'\x01' + b'\x16' + b'\xD1' + temperatura_bytes + self.matricula
        crc = self.instancia_crc.calcular_crc(mensagem)
        mensagem += crc

        resposta = self.envioDeMensagem(mensagem, "enviaTemperatura")
        
        validadeCRC = self.instancia_crc.verificaCRC(resposta)
        if validadeCRC:
            return temperatura
        
        time.sleep(1)
        print("O valor do crc veio incorreto, tentando novamente...")
        return self.escreveTemperatura()
    
    def envioSinalPWM(self, potencia):
        potencia_bytes = struct.pack('<i', potencia)
        mensagem = b'\x01' + b'\x16' + b'\xC2' + potencia_bytes + self.matricula
        crc = self.instancia_crc.calcular_crc(mensagem)
        mensagem += crc

        resposta = self.envioDeMensagem(mensagem, "envioSinalPWM")
        
        validadeCRC = self.instancia_crc.verificaCRC(resposta)
        if validadeCRC:
            return potencia
        
        time.sleep(1)
        print("O valor do crc veio incorreto, tentando novamente...")
        return self.envioSinalPWM(potencia)