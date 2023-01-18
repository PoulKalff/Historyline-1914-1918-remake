import json
import time
import pygame

from helperFunctions import *

class Level():
	""" Representation of the background """

	def __init__(self, parent, levelNo):
		self.parent = parent
		self.tiles = { 'test'  :  pygame.image.load('gfx/hexTypes/hex_test.png'),
					   'grass' :  pygame.image.load('gfx/hexTypes/hex_grass.png'),
		 }
		# read data
		with open('level' + str(levelNo) + '.json') as json_file:
			self.levelData = json.load(json_file)


	def update(self):
		self.parent.display.fill([68,136,77])
		for y in range(len(self.levelData["tiles"])):
			for x in range(len(self.levelData["tiles"][str(y)])):
				forskydning = 36 if (y % 2) != 0 else 0
				hexTile = self.tiles[self.levelData["tiles"][str(y)][x]]
				self.parent.display.blit(hexTile, [x * 72 + forskydning, y * 20])

















