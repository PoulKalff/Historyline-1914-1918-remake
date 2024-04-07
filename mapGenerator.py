#!/usr/bin/python3

height = 47
width = 12
name = 'test'
no = 0
player = 'test'


print('{')
print('\t"mapName" :\t"' + name + '",')
print('\t"mapNo" :\t' + str(no) + ',')
print('\t"player" :\t"' + player + '",')

print('\t"tiles"\t:{')
for x in range(height):
    print('\t\t\t\t"line' + str(x + 1) + '":\t[', end="")
    _width = width if x % 2 == 0 else width - 1 
    for y in range(_width):
        print('["i","",""]', end="")
        if y < _width - 1:
            print(', ', end="")
    print("]", end="")
    if x < height - 1:
        print(',')
    else:
        print()
print('\t\t}')
print('}')
