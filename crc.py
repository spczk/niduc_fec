from PyCRC.CRC16 import CRC16
from PyCRC.CRC32 import CRC32

input = '12345'
print(CRC32().calculate(input))
print(CRC16().calculate(input))