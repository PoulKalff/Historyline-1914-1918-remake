#!/usr/bin/python3

height = 6
width = 12
name = 'test'
no = 0
player = 'test'


print('{')
print('\t"mapName" :\t"' + name + '",')
print('\t"mapNo" :\t' + str(no) + ',')
print('\t"player" :\t"' + player + '",')

print('\t"tiles"\t:{')
for x in range(height + 1):
    print('\t\t\t\t"line' + str(x + 1) + '":\t[', end="")
    for y in range(width):
        print('["g","",""]', end="")
        if y < width - 1:
            print(', ', end="")
    print("]", end="")
    if x < height:
        print(',')
    else:
        print()
print('\t\t}')
print('}')
