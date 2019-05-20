import bchlib
import hashlib
import os
import random
from reedsolo import RSCodec
from bitstring import BitArray

data_bytes = 512

# random data
data = bytearray(os.urandom(data_bytes))
initial_data = data
# print(data)

# create a bch object
BCH_POLYNOMIAL = 8219
BCH_BITS = 16
bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)
rs = RSCodec(10)

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
    c = BitArray(auto=data)
    bits = c.bin[2:]
    data_len = len(bits)
    new_data = ""
    for b in range(data_len):
        new_data+=str(bits[b])
        new_data+=str(bits[b])
        new_data+=str(bits[b])
        # data.insert(len(data)-b ,data[len(data)-b])
        # data.insert(len(data)-b ,data[len(data)-b])
    return new_data, bits

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
    dataToReturn = ""
    for x in range(0, len(packet), 3):
        zeroCount = 0 
        oneCount = 0
        for b in range(3):
            if(packet[x+b] == 0):
                zeroCount += 1
            else:
                oneCount += 1
        if(oneCount > zeroCount):
            dataToReturn+="1"
        else:
            dataToReturn+="0"
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


def gillbertTransmit(packet, error_chance, errors):
    leave_chance = 0.4
    inside = False
    for b in range(len(packet)):
        if random.random() < error_chance or inside:
            inside = True
            errors += 1
            if packet[b] == 0:
                packet[b] = 1
            else:
                packet[b] = 0
            if random.random() < leave_chance:
                inside = False
    return packet, errors

def chooseChannel(channel, packet, error_chance, errors):
    if channel == "2":
        return gillbertTransmit(packet, error_chance, errors)
    else:
        return bscTransmit(packet, error_chance, errors)

print('Wybierz kodowanie: \n1) BSC\n2) Gillberta \n')
channelValue = input()

print('Wybierz kodowanie: \n1) bch\n2) reed-solomon \n3) potrajanie bitu \n')
codingValue = input()
if codingValue == "2":
    packet = rsEncode(data)
    packet, errors = chooseChannel(channelValue,packet, error_chance, errors)
    packet = rsDecode(packet)
elif codingValue == "3":
    packet = threesEncode(data)
    packet, errors = chooseChannel(channelValue,packet, error_chance, errors)
    packet = threesDecode(packet)
else:
    packet = bchEncode(data)
    packet, errors = chooseChannel(channelValue,packet, error_chance, errors)
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
