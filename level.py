import json
import time
import pygame
from helperFunctions import *

developerMode = False

bgTiles = 	{	'forest'	 	:	pygame.image.load('gfx/hexTypes/hex_forest.png'),
				'grass' 		:	pygame.image.load('gfx/hexTypes/hex_grass.png'),
				'hills' 		:	pygame.image.load('gfx/hexTypes/hex_hills.png'),
				'house' 		:	pygame.image.load('gfx/hexTypes/hex_house.png'),
				'mud' 			:	pygame.image.load('gfx/hexTypes/hex_mud.png'),
				'test'	 	 	: 	pygame.image.load('gfx/hexTypes/hex_test.png'),
				'stone'  		: 	pygame.image.load('gfx/hexTypes/hex_stone.png'),
				'mountain'		: 	pygame.image.load('gfx/hexTypes/hex_mountain.png'),
				'water'  		: 	pygame.image.load('gfx/hexTypes/hex_water.png'),
				'waterStones'	: 	pygame.image.load('gfx/hexTypes/hex_waterStones.png'),
				'hqN'	  		: 	pygame.image.load('gfx/hexTypes/hex_hqN.png'),
				'hqS'  			: 	pygame.image.load('gfx/hexTypes/hex_hqS.png'),
				'hqC'  			: 	pygame.image.load('gfx/hexTypes/hex_hqC.png'),
				'hqNE'  		: 	pygame.image.load('gfx/hexTypes/hex_hqNE.png'),
				'hqNW'  		: 	pygame.image.load('gfx/hexTypes/hex_hqNW.png'),
				'hqSE'  		: 	pygame.image.load('gfx/hexTypes/hex_hqSE.png'),
				'hqSW'  		: 	pygame.image.load('gfx/hexTypes/hex_hqSW.png'),
				'cmpN'  		: 	pygame.image.load('gfx/hexTypes/hex_campN.png'),
				'cmpS'  		: 	pygame.image.load('gfx/hexTypes/hex_campS.png'),
				'cmpE'  		: 	pygame.image.load('gfx/hexTypes/hex_campE.png'),
				'cmpW'  		: 	pygame.image.load('gfx/hexTypes/hex_campW.png'),
				'mountN'  		: 	pygame.image.load('gfx/hexTypes/hex_mountainN.png'),
				'mountS'  		: 	pygame.image.load('gfx/hexTypes/hex_mountainS.png'),
				'mountE'  		: 	pygame.image.load('gfx/hexTypes/hex_mountainE.png'),
				'mountW'  		: 	pygame.image.load('gfx/hexTypes/hex_mountainW.png'),
				'stream35' 		: 	pygame.image.load('gfx/hexTypes/hex_stream35.png'),
				'stream46' 		: 	pygame.image.load('gfx/hexTypes/hex_stream46.png'),
				'stream14' 		: 	pygame.image.load('gfx/hexTypes/hex_stream14.png'),
				'stream13' 		: 	pygame.image.load('gfx/hexTypes/hex_stream13.png'),
				'stream15' 		: 	pygame.image.load('gfx/hexTypes/hex_stream15.png'),
				'stream24' 		: 	pygame.image.load('gfx/hexTypes/hex_stream24.png'),
				'stream25' 		: 	pygame.image.load('gfx/hexTypes/hex_stream25.png'),
				'stream26' 		: 	pygame.image.load('gfx/hexTypes/hex_stream26.png'),
				'stream36'		: 	pygame.image.load('gfx/hexTypes/hex_stream36.png'),
				'lakeside12'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside12.png'),
				'lakeside16'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside16.png'),
				'lakeside23'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside23.png'),
				'lakeside34'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside34.png'),
				'lakeside56'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside56.png'),
				'lakeside123'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside123.png'),
				'lakeside126'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside126.png'),
				'lakeside156'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside156.png'),
				'lakeside3456'	: 	pygame.image.load('gfx/hexTypes/hex_lakeside3456.png')

			}


infraIcons = 	{	'' 			:	None,
					'road13' 	:	pygame.image.load('gfx/infrastructure/road13.png'),
					'road14' 	:	pygame.image.load('gfx/infrastructure/road14.png'),
					'road15' 	:	pygame.image.load('gfx/infrastructure/road15.png'),
					'road25'	:	pygame.image.load('gfx/infrastructure/road25.png'),
					'road35' 	:	pygame.image.load('gfx/infrastructure/road35.png'),
					'road36' 	:	pygame.image.load('gfx/infrastructure/road36.png'),
					'road46' 	:	pygame.image.load('gfx/infrastructure/road46.png'),
					'road124'	:	pygame.image.load('gfx/infrastructure/road124.png'),
					'road236' 	:	pygame.image.load('gfx/infrastructure/road236.png'),
					'road346' 	:	pygame.image.load('gfx/infrastructure/road346.png'),
					'road14' 	:	pygame.image.load('gfx/infrastructure/road14.png'),
					'path13' 	:	pygame.image.load('gfx/infrastructure/path13.png'),
					'path14' 	:	pygame.image.load('gfx/infrastructure/path14.png'),
					'path25' 	:	pygame.image.load('gfx/infrastructure/path25.png'),
					'path36' 	:	pygame.image.load('gfx/infrastructure/path36.png'),
					'path46' 	:	pygame.image.load('gfx/infrastructure/path46.png'),
					'bridge25' 	:	pygame.image.load('gfx/infrastructure/bridge25.png'),
					'bridge36' 	:	pygame.image.load('gfx/infrastructure/bridge36.png')
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
				if developerMode:
					text = self.parent.devModeFont.render(str(x + 1) + '/' + str(y + 1), True, (255,0,0))
					image = pygame.Surface((96, 80), pygame.SRCALPHA)
					textRect = text.get_rect()
					textRect.topleft = (20, 20)
					image.blit(text, textRect)
					self.parent.display.blit(image, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
















