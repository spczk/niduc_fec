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

error_chance = 0.32
errors = 0


# BCH
ecc = bch.encode(data)
packet = data + ecc


#RS
# packet = rs.encode(data)

def bitflip(packet):
    byte_num = random.randint(0, len(packet) - 1)
    bit_num = random.randint(0, 7)
    packet[byte_num] ^= (1 << bit_num)

# make BCH_BITS errors
for _ in range(BCH_BITS):
    if random.random() < error_chance:
        bitflip(packet)
        errors += 1

# print hash of packet
# sha1_corrupt = hashlib.sha1(packet)
# print('sha1: %s' % (sha1_corrupt.hexdigest(),))

# de-packetize
data, ecc = packet[:-bch.ecc_bytes], packet[-bch.ecc_bytes:]

# correct

#BCH
bitflips = bch.decode_inplace(data, ecc)

#RS
# packet = rs.decode(packet)

initial_data_len = len(set(initial_data))
compared_data_len = len(set(initial_data) & set(packet))


# print('bitflips: %d' % (bitflips))
print('errors generated: %d' % (errors))
print('data elements generated: %d' % (initial_data_len))
print('data elements correct after operation: %d' % (compared_data_len))

# packetize
packet = data + ecc


print('Correct percentage: ' + str((compared_data_len/initial_data_len) * 100))