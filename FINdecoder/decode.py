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


#print (int(unpackedDataLength, 16))

sys.exit()


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
