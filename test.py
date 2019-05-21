import bchlib
import hashlib
import os
import random
from reedsolo import RSCodec
from bitstring import BitArray

# create a bch object
BCH_POLYNOMIAL = 8219
BCH_BITS = 16
bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)

error_chance = 0.01
errors = 0


def chunk(l, chunk_size):
    return [l[i:i + chunk_size] for i in range(0, len(l), chunk_size)]

def compare(a, b):
    correct = 0
    for i in range(len(a)):
        if a[i] == b[i]:
            correct = correct + 1
    return correct

# BCH
def bchEncode(data):
    ecc = bch.encode(data)
    return data + ecc

#RS
def rsEncode(data):
    return rs.encode(data)
    
def threesEncode(data):
    c = BitArray(auto=data)
    bits = c.bin
    data_len = len(bits)
    new_data = list()
    for b in range(data_len):
        new_data.append(int(bits[b]))
        new_data.append(int(bits[b]))
        new_data.append(int(bits[b]))
    return new_data

def bchDecode(packet):
    data = packet[:-bch.ecc_bytes]
    ecc = packet[-bch.ecc_bytes:]
    # correct
    bch.decode_inplace(data, ecc)
    return data, ecc

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
    c = BitArray(bin=dataToReturn)
    return c.bytes

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

print ('Jak duzo danych chcesz wygenerowac i przeslac (w bajtach)?')
data_bytes = int(input())
too_big = False
if data_bytes > 512:
    too_big = True
# random data
data = bytearray(os.urandom(data_bytes))

if too_big:
    initial_data = chunk(data, 512)
    codec_num = int(data_bytes/1000) + 10
    rs = RSCodec(codec_num)
else:
    initial_data = data
    rs = RSCodec(10)

initial_data_len = len(data)

print('Wybierz kodowanie: \n1) BSC\n2) Gillberta \n')
channelValue = input()

print('Wybierz kodowanie: \n1) bch\n2) reed-solomon \n3) potrajanie bitu \n')
codingValue = input()
if codingValue == "2":
    if too_big:
        packet = bytearray()
        errors = 0
        err = 0
        overflow_generated = 0
        for chunk in initial_data:
            piece = rsEncode(chunk)
            overflow_generated = overflow_generated + (len(piece) - len(chunk))
            piece, err = chooseChannel(channelValue,piece, error_chance, err)
            piece = rsDecode(piece)
            packet = packet + piece
            errors = errors + err 
    else:
        packet = rsEncode(initial_data)
        packet_len = len(packet)
        overflow_generated = packet_len - initial_data_len
        packet, errors = chooseChannel(channelValue,packet, error_chance, errors)
        packet = rsDecode(packet)
elif codingValue == "3":
    if too_big:
        packet = bytearray()
        errors = 0
        err = 0
        overflow_generated = 0
        for chunk in initial_data:
            piece = threesEncode(chunk)
            bitstr = ''.join(str(x) for x in piece)
            p = BitArray(bin=bitstr)
            overflow_generated = overflow_generated + (len(p.bytes) - len(chunk))
            piece, err = chooseChannel(channelValue,piece, error_chance, err)
            piece = threesDecode(piece)
            packet = packet + piece
            errors = errors + err 
    else:
        packet = threesEncode(initial_data)
        bitstr = ''.join(str(x) for x in packet)
        p = BitArray(bin=bitstr)
        packet_len = len(p.bytes)
        overflow_generated = packet_len - initial_data_len
        packet, errors = chooseChannel(channelValue,packet, error_chance, errors)
        packet = threesDecode(packet)
else:
    if too_big:
        packet = bytearray()
        errors = 0
        err = 0
        overflow_generated = 0
        for chunk in initial_data:
            piece = bchEncode(chunk)
            overflow_generated = overflow_generated + (len(piece) - len(chunk))
            piece, err = chooseChannel(channelValue,piece, error_chance, err)
            piece, ecc = bchDecode(piece)
            packet = packet + piece
            errors = errors + err
    else:
        packet = bchEncode(initial_data)
        packet_len = len(packet)
        overflow_generated = packet_len - initial_data_len
        packet, errors = chooseChannel(channelValue,packet, error_chance, errors)
        packet, ecc = bchDecode(packet)


compared_data_len = compare(data, packet)

print('\nerrors generated: %d' % (errors))
print('data elements generated: %d' % (initial_data_len))
print('data elements correct after operation: %d' % (compared_data_len))
print('overflow generated: %d' % (overflow_generated))

print('Correct percentage: ' + str((float(compared_data_len)/initial_data_len) * 100))