from reedsolo import RSCodec

rs = RSCodec(10)
print (rs.encode(b'hello world'))
print (rs.decode(b'heXXo worXd\xed%T\xd4\xfdX\x89\xf3\xa8\xaa') )