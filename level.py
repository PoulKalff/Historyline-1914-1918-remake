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


infraIcons = 	{	'' 				:	None,
					'roadDiagUL'	:	pygame.image.load('gfx/infrastructure/roadDiagonalUpLeft.png'),
					'roadDUL' 		:	pygame.image.load('gfx/infrastructure/roadDownULeft.png'),
					'roadDUR' 		:	pygame.image.load('gfx/infrastructure/roadDownURight.png'),
					'roadCross1'	:	pygame.image.load('gfx/infrastructure/roadCross1.png')
				}


unitsIcons = 	{	'' 				:	None,
					'infantryG' 	:	pygame.image.load('gfx/units/german_infantry.png'),
					'eliteInfG'		:	pygame.image.load('gfx/units/german_eliteInfantry.png'),
					'cavalryG'		:	pygame.image.load('gfx/units/german_cavalry.png'),
					'lArtilleryG'	:	pygame.image.load('gfx/units/german_lightArtillery.png'),
					'mArtilleryG'	:	pygame.image.load('gfx/units/german_mediumArtillery.png'),
					'hArtilleryG'	:	pygame.image.load('gfx/units/german_heavyArtillery.png'),
					'supplyCarG' 	:	pygame.image.load('gfx/units/german_supplyCar.png'),
					'bunkerG'	 	:	pygame.image.load('gfx/units/german_bunker.png'),
					'infantryF'		:	pygame.image.load('gfx/units/french_infantry.png'),
					'eliteInfF'		:	pygame.image.load('gfx/units/french_eliteInfantry.png'),
					'cavalryF'		:	pygame.image.load('gfx/units/french_cavalry.png'),
					'lArtilleryF'	:	pygame.image.load('gfx/units/french_lightArtillery.png'),
					'mArtilleryF'	:	pygame.image.load('gfx/units/french_mediumArtillery.png'),
					'hArtilleryF'	:	pygame.image.load('gfx/units/french_heavyArtillery.png'),
					'supplyCarF' 	:	pygame.image.load('gfx/units/french_supplyCar.png'),
					'bunkerF'	 	:	pygame.image.load('gfx/units/french_bunker.png')
				}



class HexSquare():
	""" Representation of one hex """

	def __init__(self, background, infrastructure, unit):
		self.background = background	 						# The fundamental type of hex, e.g. Forest
		self.infra = infrastructure if infrastructure else None	# one of 1) Road, 2) Railroad 3) Trenches 	(overlay gfx)
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
					line.append(HexSquare(bgTiles[square[0]], infraIcons[square[1]], unitsIcons[square[2]]))
			self.map.append(line)


	def update(self):
		self.parent.display.fill([68,136,77])
		for x, line in enumerate(self.map):
			for y, square in enumerate(line):
				forskydning = 71 if (x % 2) != 0 else 0
				self.parent.display.blit(square.background, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
				if square.infra:	self.parent.display.blit(square.infra, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
				if square.unit:		self.parent.display.blit(square.unit, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
















