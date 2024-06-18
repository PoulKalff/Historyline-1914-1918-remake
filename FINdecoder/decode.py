#!/usr/bin/python3

import sys

rawFile = open("00.FIN", "rb").read()
fileLength = len(rawFile)
unpackedDataLength = int.from_bytes(rawFile[4:8], "little")
mapHeight = int(rawFile[12])
mapWidth = int(rawFile[10])
payload = rawFile[13:]

print("Read file of", fileLength, "bytes OK")
print("Map size is", mapWidth, "X", mapHeight)
print("Unpacked data length:", unpackedDataLength)
print()
#print(rawFile)

for x in range(50):
    print(hex(payload[x]), end="  ")



# iterate each byte of payload
hexNr = 1
for index in range(0, fileLength, 2):
    valueHex = payload[index]
    unitHex = payload[index + 1]
    print("   %s           Square            Unit" % (hexNr))   
    print("   ----------------------------------------")
    print("   Byte Hex:   %s              %s" % (hex(valueHex), hex(unitHex)))
    print("   Byte Int:   %s                %s" % (valueHex, unitHex))
    print("   Byte Bit:   %s          %s" % (bin(valueHex)[2:].zfill(8), bin(unitHex)[2:].zfill(8)))
    hexNr += 1
    input1 = input()





sys.exit()


# Dette er den første linie af kortet, som den skal se ud hvis den er ukomprimeret (skabt ved at se på kortet)
#                1          2          3          4         5          6          7          8          9          10         11         12         13         14         15         
uncomprString = "0x50 0xff  0x8e 0xff  0x37 0xff  0x0 0xff  0x38 0xff  0x39 0xff  0x38 0xff  0x38 0xff  0x38 0xff  0x39 0xff  0x38 0xff  0x31 0xff  0x50 0xff  0x50 0xff  0x38 0xff"
#                0x50 0xff  0x8e 0xff
#                                (0x01)
#                                      0x37 0xff  0x0 0xff  0x38 0xff  0x39
#                                      (0x0  0x4  0xc4  0x1  0x2  0x1  0x8  0x31)  
#                                                                           0xff  
#                                                                           (0x50  0x0  0x2)  
#                                                                                  0x38  0xff  0x0  0xae  0xff  0x2b"




# Felt 1:      0x50              0xff
# Felt 2:      0x8e              0xff        0x1
# Felt 3:      0x37              0xff
# Felt 4:      0x00              0xff
# Felt 5:      0x38              0xff
# Felt 6:      0x39              0xff
# Felt 7:
# Felt 8:
# Felt 9:
# Felt 10:
# Felt 11:
# Felt 12:
# Felt 13:
# Felt 14:
# Felt 15:
















print()
breaker = 0
for b in payload:
    breaker += 1
    print(hex(b), end=" ")
    if breaker == 28:
        print()
        breaker = 0






    print()
    sys.exit()


#firstLine = rawFile[13:13 + lineLength]
#secondLine = rawFile[13 + lineLength * 1:13 + lineLength * 2]
lineLength = 27		# forkert. Jeg ved ikke hvad linie lægden er, dj ejg ikke har udpakket data
mapLines = []
for x in range(mapWidth):
    mapLines.append(rawFile[13 + lineLength * x:13 + lineLength * (x + 1) ])
    print("Read", len(mapLines[-1]), "bytes into string")



for line in mapLines:
    for b in line:
        print(hex(b), end=" ")
    print()
