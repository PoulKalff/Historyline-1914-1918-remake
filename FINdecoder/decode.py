#!/usr/bin/python3

import sys

rawFile = open("00.FIN", "rb").read()
fileLength = len(rawFile)
mapHeight = int(rawFile[12])
mapWidth = int(rawFile[10])

print("Read file of", fileLength, "bytes OK")
print("Map size is", mapWidth, "X", mapHeight)

lineLength = 27


#firstLine = rawFile[13:13 + lineLength]

#secondLine = rawFile[13 + lineLength * 1:13 + lineLength * 2]

mapLines = []

for x in range(mapHeight):
    mapLines.append(rawFile[13 + lineLength * x:13 + lineLength * (x + 1) ])
    print("Read", len(mapLines[-1]), "bytes into string")



for line in mapLines:
    for b in line:
        print(hex(b), end=" ")
    print()
