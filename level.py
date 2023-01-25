import json
import time
import pygame
from helperFunctions import *

bgTiles = 	{	'forest' 	:	pygame.image.load('gfx/hexTypes/hex_forest.png'),
				'grass' 	:	pygame.image.load('gfx/hexTypes/hex_grass.png'),
				'hills' 	:	pygame.image.load('gfx/hexTypes/hex_hills.png'),
				'house' 	:	pygame.image.load('gfx/hexTypes/hex_house.png'),
				'mud' 		:	pygame.image.load('gfx/hexTypes/hex_mud.png'),
				'test'	  	: 	pygame.image.load('gfx/hexTypes/hex_test.png'),
				'stone'  	: 	pygame.image.load('gfx/hexTypes/hex_stone.png'),
				'mountain'  : 	pygame.image.load('gfx/hexTypes/hex_mountain.png'),
				'water'  	: 	pygame.image.load('gfx/hexTypes/hex_water.png'),
				'hqN'	  	: 	pygame.image.load('gfx/hexTypes/hex_hqN.png'),
				'hqS'  		: 	pygame.image.load('gfx/hexTypes/hex_hqS.png'),
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

unitsIcons = 	{		'infantryG' 	:	pygame.image.load('gfx/units/german_infantry.png'),
						'infantryF' 	:	pygame.image.load('gfx/units/french_infantry.png')
				}


class HexSquare():
	""" Representation of one hex """

	def __init__(self, background, changeable, unit):
		self.background = background	 						# The fundamental type of hex, e.g. Forest
		self.changeable = changeable if changeable else None	# one of 1) Road, 2) Railroad 3) Trenches 	(overlay gfx)
		self.unit = unit if unit else None						# any unit occupying the square, e.g. Infantry
		self.fogofwar = None									# one of 1) Black, 2) Semi transparent (e.g. seen before, but not currently)


class Level():
	""" Representation of the background """

	def __init__(self, parent, levelNo):
		self.parent = parent
		# read data
		with open('levels/level' + str(levelNo) + '.json') as json_file:
			jsonLevelData = json.load(json_file)
		self.mapWidth = len(jsonLevelData["tiles"]["line1"]) * 142
		self.mapHeight = len(jsonLevelData["tiles"]) * 40
		self.map = []
		# build up level
		for value in jsonLevelData['tiles'].values():
			line = []
			for square in value:
				line.append(HexSquare(bgTiles[square[0]], square[1], square[2]))
			self.map.append(line)


	def update(self):
		self.parent.display.fill([68,136,77])
		for x, line in enumerate(self.map):
			for y, square in enumerate(line):
				forskydning = 71 if (x % 2) != 0 else 0
				self.parent.display.blit(square.background, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])















