import json
import time
import pygame

from helperFunctions import *

class Level():
	""" Representation of the background """

	def __init__(self, parent, levelNo):
		self.parent = parent
		self.tiles = {	'forest' 	:	pygame.image.load('gfx/hexTypes/hex_forest.png'),
						'grass' 	:	pygame.image.load('gfx/hexTypes/hex_grass.png'),
						'hills' 	:	pygame.image.load('gfx/hexTypes/hex_hills.png'),
						'house' 	:	pygame.image.load('gfx/hexTypes/hex_house.png'),
						'mud' 		:	pygame.image.load('gfx/hexTypes/hex_mud.png'),
						'test'	  	: 	pygame.image.load('gfx/hexTypes/hex_test.png'),
						'stone'  	: 	pygame.image.load('gfx/hexTypes/hex_stone.png'),
						'mountain'  : 	pygame.image.load('gfx/hexTypes/hex_mountain.png'),
						'water'  	: 	pygame.image.load('gfx/hexTypes/hex_water.png'),
						'hqDoor'  	: 	pygame.image.load('gfx/hexTypes/hex_hqDoor.png'),
						'hqC'  		: 	pygame.image.load('gfx/hexTypes/hex_hqC.png'),
						'hqNE'  	: 	pygame.image.load('gfx/hexTypes/hex_hqNE.png'),
						'hqNW'  	: 	pygame.image.load('gfx/hexTypes/hex_hqNW.png'),
						'hqSE'  	: 	pygame.image.load('gfx/hexTypes/hex_hqSE.png'),
						'hqSW'  	: 	pygame.image.load('gfx/hexTypes/hex_hqSW.png'),
						'cmpN'  	: 	pygame.image.load('gfx/hexTypes/hex_campN.png'),
						'cmpS'  	: 	pygame.image.load('gfx/hexTypes/hex_campS.png'),
						'cmpE'  	: 	pygame.image.load('gfx/hexTypes/hex_campE.png'),
						'cmpW'  	: 	pygame.image.load('gfx/hexTypes/hex_campW.png'),
						'mountN'  	: 	pygame.image.load('gfx/hexTypes/hex_mountainN.png'),
						'mountS'  	: 	pygame.image.load('gfx/hexTypes/hex_mountainS.png'),
						'mountE'  	: 	pygame.image.load('gfx/hexTypes/hex_mountainE.png'),
						'mountW'  	: 	pygame.image.load('gfx/hexTypes/hex_mountainW.png')
		 }
		# read data
		with open('level' + str(levelNo) + '.json') as json_file:
			self.levelData = json.load(json_file)


	def update(self):
		self.parent.display.fill([68,136,77])
		for y in range(len(self.levelData["tiles"])):
			for x in range(len(self.levelData["tiles"][str(y)])):
				forskydning = 71 if (y % 2) != 0 else 0
				hexTile = self.tiles[self.levelData["tiles"][str(y)][x]]
				self.parent.display.blit(hexTile, [self.parent.viewDsp[0] + (x * 142 + forskydning), self.parent.viewDsp[1] + (y * 40)])

















