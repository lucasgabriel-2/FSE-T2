class Crc:

  def __init__(self) -> None:
    pass

  def calcular_crc(self, commands):
    crc = 0
    for command in commands:
      crc = self.CRC16(crc, command)
    return crc.to_bytes(2, 'little')

  def CRC16(self, crc, data):
    crc ^= data & 0xFF
    for _ in range(8):
      if crc & 1:
        crc = (crc >> 1) ^ 0xA001
      else:
        crc >>= 1
    return crc

  def verificaCRC(self, mensagem):      
      #dois ultimos
      mensagem1 = mensagem[-2:]

      #todos menos os dois ultimos
      mensagem2 = mensagem[:-2]
      mensagem2 = self.calcular_crc(mensagem2)


      if mensagem1 == mensagem2:
          return True
      return False