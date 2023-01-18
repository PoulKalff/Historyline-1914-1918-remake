import json
import time
import pygame

from helperFunctions import *

class Level():
	""" Representation of the background """

	def __init__(self, parent, levelNo):
		self.parent = parent
		self.tiles = {	'forest' :  pygame.image.load('gfx/hexTypes/hex_forest.png'),
						'grass' :  pygame.image.load('gfx/hexTypes/hex_grass.png'),
						'hills' :  pygame.image.load('gfx/hexTypes/hex_hills.png'),
						'house' :  pygame.image.load('gfx/hexTypes/hex_house.png'),
						'mud' :  pygame.image.load('gfx/hexTypes/hex_mud.png'),
						'test'  :  pygame.image.load('gfx/hexTypes/hex_test.png')
		 }
		# read data
		with open('level' + str(levelNo) + '.json') as json_file:
			self.levelData = json.load(json_file)


	def update(self):
		self.parent.display.fill([68,136,77])
		for y in range(len(self.levelData["tiles"])):
			for x in range(len(self.levelData["tiles"][str(y)])):
				forskydning = 72 if (y % 2) != 0 else 0
				hexTile = self.tiles[self.levelData["tiles"][str(y)][x]]
				self.parent.display.blit(hexTile, [x * 144 + forskydning, y * 40])

















