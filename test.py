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
    
def threesEncode(data):
    for b in range(len(data)):
        data.insert(len(data)-b ,data[len(data)-b])
        data.insert(len(data)-b ,data[len(data)-b])
    return data

#def bitflip(packet):
#    byte_num = random.randint(0, len(packet) - 1)
#    bit_num = random.randint(0, 7)
#    packet[byte_num] ^= (1 << bit_num)

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
    
def threesDecode(packet):
    count = 0
    dataToReturn = bytearray(len(packet)/3)
    for x in range(0, len(packet), 3):
        zeroCount = 0 
        oneCount = 0
        for b in range(3):
            if(packet[x+b] == 0):
                zeroCount += 1
            else:
                oneCount += 1
        if(oneCount > zeroCount):
            dataToReturn[x/3] = 1
        else:
            dataToReturn[x/3] = 0
    return dataToReturn

    

        


# make BCH_BITS errors
#for _ in range(BCH_BITS):
#    if random.random() < error_chance:
#        bitflip(packet)
#        errors += 1
def bscTransmit(packet, error_chance, errors):
    for b in range(len(packet)):
        if random.random() < error_chance:
            errors += 1
            if packet[b] == 0:
                packet[b] = 1
            else:
                packet[b] = 0
    return packet, errors

print('Wybierz kodowanie: \n1) bch\n2) reed-solomon \n3) potrajanie bitu \n')
inputValue = input()
if inputValue == 2:
    packet = rsEncode(data)
    packet, errors = bscTransmit(packet, error_chance, errors)
    packet = rsDecode(packet)
if inputValue == 3:
    packet = threesEncode(data)
    packet, errors = bscTransmit(packet, error_chance, errors)
    packet = threesDecode(packet)
else:
    packet = bchEncode(data)
    packet, errors = bscTransmit(packet, error_chance, errors)
    packet, ecc = bchDecode(packet)




initial_data_len = len(set(initial_data))
compared_data_len = len(set(initial_data) & set(packet))
packet_len = len(set(packet))
overflow_generated = packet_len - initial_data_len

# print('bitflips: %d' % (bitflips))
print('\nerrors generated: %d' % (errors))
print('data elements generated: %d' % (initial_data_len))
print('data elements correct after operation: %d' % (compared_data_len))
print('overflow generated: %d' % (overflow_generated))

print('Correct percentage: ' + str((float(compared_data_len)/initial_data_len) * 100))