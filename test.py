import bchlib
import hashlib
import os
import random
from reedsolo import RSCodec

data_bytes = 240

# random data
data = bytearray(os.urandom(data_bytes))
initial_data = data
# print(data)

# create a bch object
BCH_POLYNOMIAL = 8219
BCH_BITS = 16
bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
rs = RSCodec(data_bytes)

error_chance = 0.01
errors = 0



# BCH
def bchEncode(data):
    ecc = bch.encode(data)
    return data + ecc

#RS
def rsEncode(data):
    return rs.encode(data)

def bitflip(packet):
   byte_num = random.randint(0, len(packet) - 1)
   bit_num = random.randint(0, 7)
   packet[byte_num] ^= (1 << bit_num)

# de-packetize - bch
def bchDecode(packet):
    data = packet[:-bch.ecc_bytes]
    ecc = packet[-bch.ecc_bytes:]
    # correct
    bch.decode_inplace(data, ecc)
    return packet, ecc

#RS
def rsDecode(packet):
    return rs.decode(packet)


# make BCH_BITS errors
#for _ in range(BCH_BITS):
#    if random.random() < error_chance:
#        bitflip(packet)
#        errors += 1
def bscTransmit(packet, error_chance, errors):
    for b in range(len(packet)):
        if random.random() < error_chance:
            bitflip(packet)
            errors += 1
            # if packet[b] == 0:
            #     packet[b] = 1
            # else:
            #     packet[b] = 0
    return packet, errors

print('Wybierz kodowanie: \n1) bch\n2) reed-solomon\n')
inputValue = input()
if inputValue == 2:
    packet = rsEncode(data)
    packet, errors = bscTransmit(packet, error_chance, errors)
    packet = rsDecode(packet)
else:
    packet = bchEncode(data)
    packet, errors = bscTransmit(packet, error_chance, errors)
    packet, ecc = bchDecode(packet)




initial_data_len = len(set(initial_data))
compared_data_len = len(set(initial_data) & set(packet))

# print('bitflips: %d' % (bitflips))
print('\nerrors generated: %d' % (errors))
print('data elements generated: %d' % (initial_data_len))
print('data elements correct after operation: %d' % (compared_data_len))


print('Correct percentage: ' + str((float(compared_data_len)/initial_data_len) * 100))