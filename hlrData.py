import sys
import json
import time
import math
import numpy
import pygame

# --- Variables / Ressources ----------------------------------------------------------------------

pygame.init()

font20 = pygame.font.Font('freesansbold.ttf', 20)
font30 = pygame.font.Font('freesansbold.ttf', 30)
font40 = pygame.font.Font('freesansbold.ttf', 40)
font50 = pygame.font.Font('freesansbold.ttf', 50)
font60 = pygame.font.Font('freesansbold.ttf', 60)

flagIndex = {'Germany' : 0, 'France' : 1}

bgTilesModifiers =  {   'forest'        :   [3, 43, 8],           # movement cost (0 = not accessible) (0-10),  battle advantage (0-100), sight hindrance (0-10)
						'forest_w'      :   [3, 43, 8],
						'grass'         :   [2, 4, 0],
						'grass_w'       :   [2, 4, 0],
						'rough_w'       :   [3, 4, 0],
						'shelled_w'     :   [3, 4, 0],
						'stoney_w'      :   [3, 4, 0],
						'hills'         :   [3, 52, 8],
						'house'         :   [None, None, 2],
						'house_w'       :   [None, None, 2],
						'mud'           :   [3, 38, 0],
						'stone'         :   [3, 27, 0],
						'mountain'      :   [5, 63, 10],
						'mountain_w'    :   [5, 63, 10],
						'water'         :   [0, 0, 0],
						'waterStones'   :   [None, None, 0],
						'trenches'      :   [None, None, 0],    # no map tile yet
						'barbedWire'    :   [4, 0, 1],          # no map tile yet
						'hqN'           :   [None, None, 7],
						'hqS'           :   [None, None, 7],
						'hqC'           :   [None, None, 7],
						'hqNE'          :   [None, None, 7],
						'hqNW'          :   [None, None, 7],
						'hqSE'          :   [None, None, 7],
						'hqSW'          :   [None, None, 7],
						'hqN_w'         :   [None, None, 7],
						'hqS_w'         :   [None, None, 7],
						'hqC_w'         :   [None, None, 7],
						'hqNE_w'        :   [None, None, 7],
						'hqNW_w'        :   [None, None, 7],
						'hqSE_w'        :   [None, None, 7],
						'hqSW_w'        :   [None, None, 7],
						'cmpN'          :   [None, None, 7],
						'cmpS'          :   [None, None, 7],
						'cmpE'          :   [None, None, 7],
						'cmpW'          :   [None, None, 7],
						'cmpN_w'        :   [None, None, 7],
						'cmpS_w'        :   [None, None, 7],
						'cmpE_w'        :   [None, None, 7],
						'cmpW_w'        :   [None, None, 7],
						'factoryN_w'    :   [None, None, 7],
						'factoryS_w'    :   [None, None, 7],
						'factoryE_w'    :   [None, None, 7],
						'factoryW_w'    :   [None, None, 7],
						'mountN'        :   [None, None, 10],
						'mountS'        :   [None, None, 10],
						'mountE'        :   [None, None, 10],
						'mountW'        :   [None, None, 10],
						'mountN_w'      :   [None, None, 10],
						'mountS_w'      :   [None, None, 10],
						'mountE_w'      :   [None, None, 10],
						'mountW_w'      :   [None, None, 10],
						'stream35'      :   [None, None, 0],
						'stream46'      :   [None, None, 0],
						'stream14'      :   [None, None, 0],
						'stream13'      :   [None, None, 0],
						'stream15'      :   [None, None, 0],
						'stream24'      :   [None, None, 0],
						'stream25'      :   [None, None, 0],
						'stream26'      :   [None, None, 0],
						'stream36'      :   [None, None, 0],
						'stream13_w'    :   [None, None, 0],
						'stream14_w'    :   [None, None, 0],
						'stream25_w'    :   [None, None, 0],
						'stream26_w'    :   [None, None, 0],
						'stream35_w'    :   [None, None, 0],
						'stream36_w'    :   [None, None, 0],
						'stream46_w'    :   [None, None, 0],
						'stream135_w'   :   [None, None, 0],
						'stream15_w'    :   [None, None, 0],
						'stream246_w'   :   [None, None, 0],
						'stream24_w'    :   [None, None, 0],
						'lakeside12'    :   [None, None, 0],
						'lakeside16'    :   [None, None, 0],
						'lakeside23'    :   [None, None, 0],
						'lakeside34'    :   [None, None, 0],
						'lakeside56'    :   [None, None, 0],
						'lakeside123'   :   [None, None, 0],
						'lakeside126'   :   [None, None, 0],
						'lakeside156'   :   [None, None, 0],
						'lakeside3456'  :   [None, None, 0],                   
						'unseen'		:   [None, None, 0]
					}


bgTiles =   {   'forest'        :   pygame.image.load('gfx/hexTypes/hex_forest.png'),
				'forest_w'      :   pygame.image.load('gfx/hexTypes/hex_forest_winter.png'),
				'grass'         :   pygame.image.load('gfx/hexTypes/hex_grass.png'),
				'grass_w'       :   pygame.image.load('gfx/hexTypes/hex_grass_winter.png'),
				'rough_w'       :   pygame.image.load('gfx/hexTypes/hex_rough_winter.png'),
				'stoney_w'      :   pygame.image.load('gfx/hexTypes/hex_stoney_winter.png'),
				'shelled_w'     :   pygame.image.load('gfx/hexTypes/hex_shelled_winter.png'),
				'house_w'       :   pygame.image.load('gfx/hexTypes/hex_house_winter.png'),
				'hills'         :   pygame.image.load('gfx/hexTypes/hex_hills.png'),
				'house'         :   pygame.image.load('gfx/hexTypes/hex_house.png'),
				'mud'           :   pygame.image.load('gfx/hexTypes/hex_mud.png'),
				'stone'         :   pygame.image.load('gfx/hexTypes/hex_stone.png'),
				'mountain'      :   pygame.image.load('gfx/hexTypes/hex_mountain.png'),
				'mountain_w'    :   pygame.image.load('gfx/hexTypes/hex_mountain_winter.png'),
				'water'         :   pygame.image.load('gfx/hexTypes/hex_water.png'),
				'waterStones'   :   pygame.image.load('gfx/hexTypes/hex_waterStones.png'),
				'hqN'           :   pygame.image.load('gfx/hexTypes/hex_hqN.png'),
				'hqS'           :   pygame.image.load('gfx/hexTypes/hex_hqS.png'),
				'hqC'           :   pygame.image.load('gfx/hexTypes/hex_hqC.png'),
				'hqNE'          :   pygame.image.load('gfx/hexTypes/hex_hqNE.png'),
				'hqNW'          :   pygame.image.load('gfx/hexTypes/hex_hqNW.png'),
				'hqSE'          :   pygame.image.load('gfx/hexTypes/hex_hqSE.png'),
				'hqSW'          :   pygame.image.load('gfx/hexTypes/hex_hqSW.png'),
				'hqN_w'         :   pygame.image.load('gfx/hexTypes/hex_hqN_winter.png'),
				'hqS_w'         :   pygame.image.load('gfx/hexTypes/hex_hqS_winter.png'),
				'hqC_w'         :   pygame.image.load('gfx/hexTypes/hex_hqC_winter.png'),
				'hqNE_w'        :   pygame.image.load('gfx/hexTypes/hex_hqNE_winter.png'),
				'hqNW_w'        :   pygame.image.load('gfx/hexTypes/hex_hqNW_winter.png'),
				'hqSE_w'        :   pygame.image.load('gfx/hexTypes/hex_hqSE_winter.png'),
				'hqSW_w'        :   pygame.image.load('gfx/hexTypes/hex_hqSW_winter.png'),
				'cmpN'          :   pygame.image.load('gfx/hexTypes/hex_campN.png'),
				'cmpS'          :   pygame.image.load('gfx/hexTypes/hex_campS.png'),
				'cmpE'          :   pygame.image.load('gfx/hexTypes/hex_campE.png'),
				'cmpW'          :   pygame.image.load('gfx/hexTypes/hex_campW.png'),
				'factoryN_w'    :   pygame.image.load('gfx/hexTypes/hex_factoryN_winter.png'),
				'factoryS_w'    :   pygame.image.load('gfx/hexTypes/hex_factoryS_winter.png'),
				'factoryE_w'    :   pygame.image.load('gfx/hexTypes/hex_factoryE_winter.png'),
				'factoryW_w'    :   pygame.image.load('gfx/hexTypes/hex_factoryW_winter.png'),
				'cmpN_w'        :   pygame.image.load('gfx/hexTypes/hex_campN_winter.png'),
				'cmpS_w'        :   pygame.image.load('gfx/hexTypes/hex_campS_winter.png'),
				'cmpE_w'        :   pygame.image.load('gfx/hexTypes/hex_campE_winter.png'),
				'cmpW_w'        :   pygame.image.load('gfx/hexTypes/hex_campW_winter.png'),
				'mountN'        :   pygame.image.load('gfx/hexTypes/hex_mountainN.png'),
				'mountS'        :   pygame.image.load('gfx/hexTypes/hex_mountainS.png'),
				'mountE'        :   pygame.image.load('gfx/hexTypes/hex_mountainE.png'),
				'mountW'        :   pygame.image.load('gfx/hexTypes/hex_mountainW.png'),
				'mountN_w'      :   pygame.image.load('gfx/hexTypes/hex_mountainN_winter.png'),
				'mountS_w'      :   pygame.image.load('gfx/hexTypes/hex_mountainS_winter.png'),
				'mountE_w'      :   pygame.image.load('gfx/hexTypes/hex_mountainE_winter.png'),
				'mountW_w'      :   pygame.image.load('gfx/hexTypes/hex_mountainW_winter.png'),
				'stream35'      :   pygame.image.load('gfx/hexTypes/hex_stream35.png'),
				'stream46'      :   pygame.image.load('gfx/hexTypes/hex_stream46.png'),
				'stream14'      :   pygame.image.load('gfx/hexTypes/hex_stream14.png'),
				'stream13'      :   pygame.image.load('gfx/hexTypes/hex_stream13.png'),
				'stream15'      :   pygame.image.load('gfx/hexTypes/hex_stream15.png'),
				'stream24'      :   pygame.image.load('gfx/hexTypes/hex_stream24.png'),
				'stream25'      :   pygame.image.load('gfx/hexTypes/hex_stream25.png'),
				'stream26'      :   pygame.image.load('gfx/hexTypes/hex_stream26.png'),
				'stream36'      :   pygame.image.load('gfx/hexTypes/hex_stream36.png'),
				'stream13_w'    :   pygame.image.load('gfx/hexTypes/hex_stream13_winter.png'),
				'stream14_w'    :   pygame.image.load('gfx/hexTypes/hex_stream14_winter.png'),
				'stream25_w'    :   pygame.image.load('gfx/hexTypes/hex_stream25_winter.png'),
				'stream26_w'    :   pygame.image.load('gfx/hexTypes/hex_stream26_winter.png'),
				'stream35_w'    :   pygame.image.load('gfx/hexTypes/hex_stream35_winter.png'),
				'stream36_w'    :   pygame.image.load('gfx/hexTypes/hex_stream36_winter.png'),
				'stream46_w'    :   pygame.image.load('gfx/hexTypes/hex_stream46_winter.png'),
				'stream135_w'   :   pygame.image.load('gfx/hexTypes/hex_stream135_winter.png'),
				'stream15_w'    :   pygame.image.load('gfx/hexTypes/hex_stream15_winter.png'),
				'stream246_w'   :   pygame.image.load('gfx/hexTypes/hex_stream246_winter.png'),
				'stream24_w'    :   pygame.image.load('gfx/hexTypes/hex_stream24_winter.png'),
				'lakeside12'    :   pygame.image.load('gfx/hexTypes/hex_lakeside12.png'),
				'lakeside16'    :   pygame.image.load('gfx/hexTypes/hex_lakeside16.png'),
				'lakeside23'    :   pygame.image.load('gfx/hexTypes/hex_lakeside23.png'),
				'lakeside34'    :   pygame.image.load('gfx/hexTypes/hex_lakeside34.png'),
				'lakeside56'    :   pygame.image.load('gfx/hexTypes/hex_lakeside56.png'),
				'lakeside123'   :   pygame.image.load('gfx/hexTypes/hex_lakeside123.png'),
				'lakeside126'   :   pygame.image.load('gfx/hexTypes/hex_lakeside126.png'),
				'lakeside156'   :   pygame.image.load('gfx/hexTypes/hex_lakeside156.png'),
				'lakeside3456'  :   pygame.image.load('gfx/hexTypes/hex_lakeside3456.png'),
				'unseen'        :   pygame.image.load('gfx/hexTypes/hex_unseen.png')
			}


infraIcons =    {   ''          :   None,
					'cross1'	:   pygame.image.load('gfx/infrastructure/crossRail36Path14.png'),
					'cross2'	:   pygame.image.load('gfx/infrastructure/crossRail36Road14.png'),
					'cross3'	:   pygame.image.load('gfx/infrastructure/crossRail36Road25.png'),
					'cross4'	:   pygame.image.load('gfx/infrastructure/crossRail14Path36.png'),
					'trench0'   :   pygame.image.load('gfx/infrastructure/trench0.png'),
					'trench1'   :   pygame.image.load('gfx/infrastructure/trench1.png'),
					'trench4'   :   pygame.image.load('gfx/infrastructure/trench4.png'),
					'trench5'   :   pygame.image.load('gfx/infrastructure/trench5.png'),
					'trench5a'  :   pygame.image.load('gfx/infrastructure/trench5a.png'),
					'trench12'  :   pygame.image.load('gfx/infrastructure/trench12.png'),
					'trench14'  :   pygame.image.load('gfx/infrastructure/trench14.png'),
					'trench24'  :   pygame.image.load('gfx/infrastructure/trench24.png'),
					'trench25'  :   pygame.image.load('gfx/infrastructure/trench25.png'),
					'trench124' :   pygame.image.load('gfx/infrastructure/trench124.png'),
					'trench125' :   pygame.image.load('gfx/infrastructure/trench125.png'),
					'trench15'  :   pygame.image.load('gfx/infrastructure/trench15.png'),
					'rail26'    :   pygame.image.load('gfx/infrastructure/rail26.png'),
					'rail13'    :   pygame.image.load('gfx/infrastructure/rail13.png'),
					'rail35'    :   pygame.image.load('gfx/infrastructure/rail35.png'),
					'rail46'    :   pygame.image.load('gfx/infrastructure/rail46.png'),
					'rail15'    :   pygame.image.load('gfx/infrastructure/rail15.png'),
					'rail24'    :   pygame.image.load('gfx/infrastructure/rail24.png'),
					'rail36'    :   pygame.image.load('gfx/infrastructure/rail36.png'),
					'rail14'    :   pygame.image.load('gfx/infrastructure/rail14.png'),
					'rail25'    :   pygame.image.load('gfx/infrastructure/rail25.png'),
					'rail346'   :   pygame.image.load('gfx/infrastructure/rail346.png'),
					'rail356'   :   pygame.image.load('gfx/infrastructure/rail356.png'),
					'road13'    :   pygame.image.load('gfx/infrastructure/road13.png'),
					'road14'    :   pygame.image.load('gfx/infrastructure/road14.png'),
					'road15'    :   pygame.image.load('gfx/infrastructure/road15.png'),
					'road25'    :   pygame.image.load('gfx/infrastructure/road25.png'),
					'road35'    :   pygame.image.load('gfx/infrastructure/road35.png'),
					'road36'    :   pygame.image.load('gfx/infrastructure/road36.png'),
					'road46'    :   pygame.image.load('gfx/infrastructure/road46.png'),
					'road26'    :   pygame.image.load('gfx/infrastructure/road26.png'),
					'road125'   :   pygame.image.load('gfx/infrastructure/road125.png'),
					'path125'   :   pygame.image.load('gfx/infrastructure/path125.png'),
					'road124'   :   pygame.image.load('gfx/infrastructure/road124.png'),
					'road145'   :   pygame.image.load('gfx/infrastructure/road145.png'),
					'road236'   :   pygame.image.load('gfx/infrastructure/road236.png'),
					'road346'   :   pygame.image.load('gfx/infrastructure/road346.png'),
					'road356'   :   pygame.image.load('gfx/infrastructure/road356.png'),
					'path356'   :   pygame.image.load('gfx/infrastructure/path356.png'),
					'path135'   :   pygame.image.load('gfx/infrastructure/path135.png'),
					'road135'   :   pygame.image.load('gfx/infrastructure/road135.png'),
					'road14'    :   pygame.image.load('gfx/infrastructure/road14.png'),
					'road15'    :   pygame.image.load('gfx/infrastructure/road15.png'),
					'road24'    :   pygame.image.load('gfx/infrastructure/road24.png'),
					'road35'    :   pygame.image.load('gfx/infrastructure/road35.png'),
					'path15'    :   pygame.image.load('gfx/infrastructure/path15.png'),
					'path24'    :   pygame.image.load('gfx/infrastructure/path24.png'),
					'path35'    :   pygame.image.load('gfx/infrastructure/path35.png'),
					'path13'    :   pygame.image.load('gfx/infrastructure/path13.png'),
					'path14'    :   pygame.image.load('gfx/infrastructure/path14.png'),
					'path25'    :   pygame.image.load('gfx/infrastructure/path25.png'),
					'path36'    :   pygame.image.load('gfx/infrastructure/path36.png'),
					'path46'    :   pygame.image.load('gfx/infrastructure/path46.png'),
					'path346'   :   pygame.image.load('gfx/infrastructure/path346.png'),
					'bridge25'  :   pygame.image.load('gfx/infrastructure/bridge25.png'),
					'bridge36'  :   pygame.image.load('gfx/infrastructure/bridge36.png')
				}


unitsParameters =   {   ''              :   None,
						'CP_infantry'   :   {   'name'          : 'Infantry',
												'country'       : 'Germany',
												'armour'        : 20,
												'speed'         : 3,
												'weight'        : 1,
												'storageMax'    : 0,
												'sight'         : 3,
												'fuel'          : 30,
												'exp'           : 0,
												'skills'        : [1],
												'movementType'  : 0,		# 0 : normal, 1 : only move on tracks, 2: only move on water
												'weapons'       : ['bayonet', 'lugerp08', 'gewehr98', None],
												'icon'          : pygame.image.load('gfx/units/icons/infantry.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/infantry.png')
											},
						'EC_infantry'   :   {   'name'          : 'Infantry',
												'country'       : 'France',
												'armour'        : 20,
												'speed'         : 3,
												'weight'        : 1,
												'storageMax'    : 0,
												'sight'         : 3,
												'fuel'          : 30,
												'exp'           : 0,
												'skills'        : [1],
												'movementType'  : 0,
												'weapons'       : ['bayonet', 'revolveur', 'leeEnfield', None],
												'icon'          : pygame.image.load('gfx/units/icons/infantry.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/infantry.png')
											},
						'CP_eliteInf'   :   {   'name'          : 'Elite Infantry',
												'country'       : 'Germany',
												'armour'        : 25,
												'speed'         : 6,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 3,
												'fuel'          : 30,
												'exp'           : 0,
												'skills'        : [1],
												'movementType'  : 0,
												'weapons'       : ['trenchKnife', 'maxim', None, None],
												'icon'          : pygame.image.load('gfx/units/icons/eliteInfantry.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/eliteInfantry.png')
											},
						'EC_eliteInf'   :   {   'name'          : 'Elite Infantry',
												'country'       : 'France',
												'armour'        : 25,
												'speed'         : 6,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 3,
												'fuel'          : 30,
												'exp'           : 0,
												'skills'        : [1],
												'movementType'  : 0,
												'weapons'       : ['trenchKnife', 'wickers', None, None],
												'icon'          : pygame.image.load('gfx/units/icons/eliteInfantry.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/eliteInfantry.png')

											},
						'CP_cavalry'    :   {   'name'          : 'Cavalry',
												'country'       : 'Germany',
												'armour'        : 20,
												'speed'         : 6,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 3,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [1],
												'movementType'  : 0,
												'weapons'       : ['sabre', 'gewehr98', None, None],
												'icon'          : pygame.image.load('gfx/units/icons/cavalry.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/cavalry.png')
											},
						'EC_cavalry'    :   {   'name'          : 'Cavalry',
												'country'       : 'France',
												'armour'        : 20,
												'speed'         : 6,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 3,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [1],
												'movementType'  : 0,
												'weapons'       : [ 'sabre', 'leeEnfield', None, None],
												'icon'          : pygame.image.load('gfx/units/icons/cavalry.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/cavalry.png')
											},
						'CP_lArtillery' :   {   'name'          : 'Light Artillery',
												'country'       : 'Germany',
												'armour'        : 25,
												'speed'         : 2,
												'weight'        : 3,
												'storageMax'    : 0,
												'sight'         : 2,
												'fuel'          : 25,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 0,
												'weapons'       : ['feldkanone16', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/lightArtillery.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/lightArtillery.png')
											},
						'EC_lArtillery' :   {   'name'          : 'Light Artillery',
												'country'       : 'France',
												'armour'        : 25,
												'speed'         : 2,
												'weight'        : 3,
												'storageMax'    : 0,
												'sight'         : 2,
												'fuel'          : 20,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 0,
												'weapons'       : ['m1902', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/lightArtillery.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/lightArtillery.png')
											},
						'CP_mArtillery' :   {   'name'          : 'Medium Artillery',
												'country'       : 'Germany',
												'armour'        : 27,
												'speed'         : 1,
												'weight'        : 4,
												'storageMax'    : 0,
												'sight'         : 2,
												'fuel'          : 20,
												'exp'           : 0,
												'skills'        : [5],
												'movementType'  : 0,
												'weapons'       : ['lefh', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/mediumArtillery.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/mediumArtillery.png')
											},
						'EC_mArtillery' :   {   'name'          : 'Medium Artillery',
												'country'       : 'France',
												'armour'        : 27,
												'speed'         : 1,
												'weight'        : 4,
												'storageMax'    : 0,
												'sight'         : 2,
												'fuel'          : 20,
												'exp'           : 0,
												'skills'        : [5],
												'movementType'  : 0,
												'weapons'       : ['canon75', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/mediumArtillery.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/mediumArtillery.png')
											},
						'CP_hArtillery' :   {   'name'          : 'Heavy Artillery',
												'country'       : 'Germany',
												'armour'        : 25,
												'speed'         : 1,
												'weight'        : 5,
												'storageMax'    : 0,
												'sight'         : 2,
												'fuel'          : 20,
												'exp'           : 0,
												'skills'        : [5],
												'movementType'  : 0,
												'weapons'       : ['morser', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/heavyArtillery.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/heavyArtillery.png')
											},
						'EC_hArtillery' :   {   'name'          : 'Heavy Artillery',
												'country'       : 'France',
												'armour'        : 25,
												'speed'         : 1,
												'weight'        : 5,
												'storageMax'    : 0,
												'sight'         : 2,
												'fuel'          : 20,
												'exp'           : 0,
												'skills'        : [5],
												'movementType'  : 0,
												'weapons'       : ['canon155', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/heavyArtillery.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/heavyArtillery.png')
											},
						'CP_supplyCar'  :   {   'name'          : 'Supplycar',
												'country'       : 'Germany',
												'armour'        : 20,
												'speed'         : 7,
												'weight'        : 4,
												'storageMax'    : 5,
												'sight'         : 1,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 0,
												'weapons'       : [None, None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/supplyCar.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/supplyCar.png')
											},
						'EC_supplyCar'  :   {   'name'          : 'Supplycar',
												'country'       : 'France',
												'armour'        : 20,
												'speed'         : 7,
												'weight'        : 4,
												'storageMax'    : 5,
												'sight'         : 1,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 0,
												'weapons'       : [None, None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/supplyCar.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/supplyCar.png')
											},
						'CP_bunker'     :   {   'name'          : 'Bunker',
												'country'       : 'Germany',
												'armour'        : 85,
												'speed'         : 0,
												'weight'        : 0,
												'storageMax'    : 2,
												'sight'         : 1,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [7],
												'movementType'  : 0,
												'weapons'       : ['feldkanone16', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/bunker.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/bunker.png')
											},
						'EC_bunker'     :   {   'name'          : 'Bunker',
												'country'       : 'France',
												'armour'        : 85,
												'speed'         : 0,
												'weight'        : 0,
												'storageMax'    : 2,
												'sight'         : 1,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [7],
												'movementType'  : 0,
												'weapons'       : ['m1902', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/bunker.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/bunker.png')
											},
						'EC_charron' :		{   'name'          : 'Charron',
												'country'       : 'France',
												'armour'        : 25,
												'speed'         : 5,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 7,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 0,
												'weapons'       : ['wickers', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/charron.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/charron.png')
											},
						'CP_armCar' :	{   	'name'          : 'Armored Car',
												'country'       : 'Germany',
												'armour'        : 25,
												'speed'         : 5,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 7,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 0,
												'weapons'       : ['maxim', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/armoredCar.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/armoredCar.png')
											},
						'EC_patrolBoat' :	{   'name'          : 'Speedboat',
												'country'       : 'France',
												'armour'        : 15,
												'speed'         : 8,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 7,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 2,	# Only move on water
												'weapons'       : ['wickers', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/patrolBoat.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/patrolBoat.png')
											},
						'CP_patrolBoat' :	{   'name'          : 'Speedboat',
												'country'       : 'Germany',
												'armour'        : 15,
												'speed'         : 8,
												'weight'        : 2,
												'storageMax'    : 0,
												'sight'         : 7,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 2,	# Only move on water
												'weapons'       : ['wickers', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/patrolBoat.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/patrolBoat.png')
											},
						'CP_transTrain' :	{   'name'          : 'Transport Train',
												'country'       : 'Germany',
												'armour'        : 45,
												'speed'         : 7,
												'weight'        : 7,
												'storageMax'    : 8,
												'sight'         : 1,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 1,	# Only move on tracks
												'weapons'       : [None, None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/transportTrain.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/transportTrain.png')
											},
						'EC_armTrain' :		{   'name'          : 'Armored Train',
												'country'       : 'France',
												'armour'        : 75,
												'speed'         : 7,
												'weight'        : 7,
												'storageMax'    : 2,
												'sight'         : 3,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 1,	# Only move on tracks
												'weapons'       : ['m1902', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/armoredTrain.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/armoredTrain.png')
											},
						'CP_armTrain' :		{   'name'          : 'Armored Train',
												'country'       : 'Germany',
												'armour'        : 75,
												'speed'         : 7,
												'weight'        : 7,
												'storageMax'    : 2,
												'sight'         : 3,
												'fuel'          : 50,
												'exp'           : 0,
												'skills'        : [],
												'movementType'  : 1,	# Only move on tracks
												'weapons'       : ['lefh', None, None, None],
												'icon'          : pygame.image.load('gfx/units/icons/armoredTrain.png'),
												'picture'       : pygame.image.load('gfx/units/pictures/armoredTrain.png')
											}
					}


weaponsParameters =     {   'bayonet'   :       {   'name'      : 'Bayonet',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 10,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : None,
													'picture'   : pygame.image.load('gfx/weapons/bayonet.png'), 
												},
							'sabre'     :       {   'name'      : 'Cavalry Sabre',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 15,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : None,
													'picture'   : pygame.image.load('gfx/weapons/sabre.png'), 
												},
							'trenchKnife'   :   {   'name'      : 'TrenchKnife',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 10,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : None,
													'picture'   : pygame.image.load('gfx/weapons/trenchKnife.png'), 
												},
							'revolveur' :       {   'name'      : 'revolveurM1892',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 15,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/revolveurM1892.png'), 
												},
							'lugerp08' :        {   'name'      : 'Luger P08',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 15,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/lugerP08.png'), 
												},
							'gewehr98' :        {   'name'      : 'Gewehr 98',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 30,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 3,
													'picture'   : pygame.image.load('gfx/weapons/gewehr98.png'), 
												},
							'leeEnfield'    :   {   'name'      : 'Lee-Enfield',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 30,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 3,
													'picture'   : pygame.image.load('gfx/weapons/leeEnfield.png'), 
												},
							'maxim'     :       {   'name'      : 'Maxim Machinegun',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 430,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/maximMachineGun.png'), 
												},
							'wickers'   :       {   'name'      : 'Wickers Machinegun',
													'rangeMin'  : 1,
													'rangeMax'  : 1,
													'power'     : 43,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/wickersMachineGun.png'), 
												},
							'feldkanone16'  :   {   'name'      : '7.7 cm Feldkanone 16',
													'note'      : 'Central Powers Light Artillery',
													'rangeMin'  : 1,
													'rangeMax'  : 3,
													'power'     : 45,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/feldkanone16.png'), 
												},
							'm1902'     :       {   'name'      : '3-inch M1902',
													'note'      : 'Entente Light Artillery',
													'rangeMin'  : 1,
													'rangeMax'  : 3,
													'power'     : 45,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/m1902.png'), 
												},
							'lefh'  :           {   'name'      : '10.5 cm leichte Feldhaubitze 16',
													'note'      : 'Central Powers Medium Artillery',
													'rangeMin'  : 2,
													'rangeMax'  : 5,
													'power'     : 55,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/lefh.png'), 
												},
							'canon75'   :       {   'name'      : 'Wickers Machinegun',
													'note'      : 'Entente Medium Artillery',
													'rangeMin'  : 2,
													'rangeMax'  : 5,
													'power'     : 55,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/canon75.png'),
												},
							'morser'    :       {   'name'      : 'Morser 16',
													'note'      : 'Central Powers heavy artillery',
													'rangeMin'  : 2,
													'rangeMax'  : 6,
													'power'     : 70,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/moerser16.png'), 
												},
							'canon155'  :       {   'name'      : 'Canon de 155 L',
													'note'      : 'Entente heavy artillery',
													'rangeMin'  : 2,
													'rangeMax'  : 6,
													'power'     : 70,
													'air'       : False,
													'ground'    : True,
													'water'     : False,
													'ammo'      : 5,
													'picture'   : pygame.image.load('gfx/weapons/canon155.png'), 
												}
						}


# --- Functions -----------------------------------------------------------------------------------


def rot_center(image, angle):
	""" rotate an image while keeping its center and size """
	orig_rect = image.get_rect()
	rot_image = pygame.transform.rotate(image, angle)
	rot_rect = orig_rect.copy()
	rot_rect.center = rot_image.get_rect().center
	rot_image = rot_image.subsurface(rot_rect).copy()
	return rot_image


def createPathInfraIcons(allIcons):
	""" iterates through infrastructure icons and creates a path-icon equivalent from each road icon """
	pathIcons = []
	for icon in allIcons:
		if icon[0].startswith('road'):
			pathIcons.append(icon)
	# process each icon, put back in list

# RAW LINES FROM DIFFERENT FUCNTION!

	self.icon = self.rawIcon.copy()
	if owner == 0:		# unowned
		arr = pygame.surfarray.pixels3d(self.icon)
		for i in range(48):
			for j in range(48): # loop over the 2d array
				if numpy.array_equal(arr[i, j], [164, 132, 112]):
					arr[i, j] = [72, 72, 72]
				elif numpy.array_equal(arr[i, j], [80, 68, 52]):
					arr[i, j] = [24, 24, 24]
				elif numpy.array_equal(arr[i, j], [216, 188, 160]):
					arr[i, j] = [148, 148, 148]
				elif numpy.array_equal(arr[i, j], [144, 112,  88]):
					arr[i, j] = [56, 56, 56]
				elif numpy.array_equal(arr[i, j], [180, 148, 124]):
					arr[i, j] = [88, 88, 88]




def greyscale(surface: pygame.Surface):
	surface_copy = surface.copy()
	arr = pygame.surfarray.pixels3d(surface_copy)
	mean_arr = numpy.dot(arr, [0.216, 0.587, 0.144])
	arr[:, :, 0] = mean_arr
	arr[:, :, 1] = mean_arr
	arr[:, :, 2] = mean_arr
	return surface_copy


def adjacentHexes(x, y, maxX, maxY):
	""" returns a list of 6 pairs of coords of the hexes that borders hex of coord given """
	checked = []
	if (x % 2) == 1: 
		neighbors = [(x - 1, y + 1), (x + 1, y + 1), (x + 2, y), (x + 1, y), (x - 1, y), (x - 2, y)]
	else:
		neighbors = [(x - 1, y), (x + 1, y), (x + 2, y), (x + 1, y - 1), (x - 1, y - 1), (x - 2, y)]
	# filter invalid coordinates
	for coord in neighbors:
		if coord[0] > -1 and coord[0] < maxY:
			if coord[1] > -1:
				if coord[0] % 2 == 0:
					if coord[1] < maxX:
						checked.append(coord)
				else:
					if coord[1] < maxX - 1:
						checked.append(coord)
	return checked


# --- Classes -------------------------------------------------------------------------------------

class colors:
	black =             (0, 0, 0)
	white =             (255, 255, 255)
	red =               (255, 0, 0)
	darkRed =           (165, 32, 32)
	cyan =              (0, 255, 255)
	green =             (0, 255, 0)
	grey =              (150, 150, 150)
	darkGrey =          (50, 50, 50)
	almostBlack =       (20, 20, 20)
	orange =            (220, 162, 57)
	green =             (70, 180, 50)
	blue =              (80, 120, 250)
	background =        (55, 55, 55)
	yellow =            (255, 255, 0)
	bi3 =               (68, 136, 77)
	historylineDark =   (49, 48, 33)
	historylineLight =  (107, 105, 90)



class Info():
	""" contains all info about the active game """

	nameDict =  {   0 : 'None', 
					1 : 'Central Powers', 
					2 : 'Entente Cordial', 
						'None' : 0, 
						'Central Powers' : 1, 
						'Entente Cordial' : 2 }

	def __init__(self, _mapName, _mapNo, _player, _tiles):
		self.player = self.nameDict[_player]
		self.opponent = 1 if self.player == 2 else 2
		self.mapName = _mapName
		self.mapNumber = _mapNo
		self.mapWidth = len(_tiles["line1"])
		self.mapHeight = len(_tiles)



class Content():
	""" Representation of content of a unit or hex """

	def __init__(self, _max):
		self.units = [[False for x in range(9)], [False for x in range(9)]]
		self.storageMax = _max

	def storageActual(self):
		row1 = sum([x.weight for x in self.units[0] if x])
		row2 = sum([x.weight for x in self.units[1] if x])
		return row1 + row2

	def addUnit(self, _unit):
		_delivered = False
		for y in range(9):
			for x in range(2):
				if not _delivered and not self.units[x][y]:
					_delivered = True
					self.units[x][y] =_unit



class Weapon():
	""" Representation of one weapon """

	def __init__(self, key):
		if key:
			data = weaponsParameters[key]
			self.name = data['name']    
			self.rangeMin = data['rangeMin']
			self.rangeMax = data['rangeMax']
			self.power = data['power']
			self.air = data['air']
			self.ground = data['ground']
			self.water = data['water']
			self.ammo = data['ammo']
			self.picture = data['picture']





class Unit():
	""" Representation of one unit  """

	def __init__(self, key):
		if key:
			data = unitsParameters[key]
			self.name = data['name']
			self.country = data['country'] 
			self.armour = data['armour']
			self.speed = data['speed']
			self.weight = data['weight']
			self.sight = data['sight']
			self.fuel = data['fuel']
			self.experience = 0
			self.skills = data['skills']
			self.movementType = data['movementType']
			self.weapons = []
			self.weaponsGfx = []
			self.maxSize = 10       # all units size 10?
			self.currentSize = 10
			self.faction = 1 if self.country in ['Germany', 'Austria', 'Bulgaria', 'Ottoman'] else 2
			self.content = Content(data['storageMax']) if data['storageMax'] > 0 else False
			for w in data['weapons']:
				if w:
					self.weapons.append(Weapon(w))
				else:
					self.weapons.append(None)
			self.picture = data['picture']
			self.rawIcon = data['icon']
			self.changeColour(self.faction)
			self.mapIcon = self.allIcons[3] if self.faction == 1 else self.allIcons[0]
			self.updateWeaponsGfx()


	def changeColour(self, owner):
		self.icon = self.rawIcon.copy()
		if owner == 0:		# unowned
			arr = pygame.surfarray.pixels3d(self.icon)
			for i in range(48):
				for j in range(48): # loop over the 2d array
					if numpy.array_equal(arr[i, j], [164, 132, 112]):
						arr[i, j] = [72, 72, 72]
					elif numpy.array_equal(arr[i, j], [80, 68, 52]):
						arr[i, j] = [24, 24, 24]
					elif numpy.array_equal(arr[i, j], [216, 188, 160]):
						arr[i, j] = [148, 148, 148]
					elif numpy.array_equal(arr[i, j], [144, 112,  88]):
						arr[i, j] = [56, 56, 56]
					elif numpy.array_equal(arr[i, j], [180, 148, 124]):
						arr[i, j] = [88, 88, 88]
		elif owner == 1:		# central powers
			arr = pygame.surfarray.pixels3d(self.icon)
			for i in range(48):
				for j in range(48): # loop over the 2d array
					if numpy.array_equal(arr[i, j], [164, 132, 112]):
						arr[i, j] = [72, 88, 52]
					elif numpy.array_equal(arr[i, j], [80, 68, 52]):
						arr[i, j] = [24, 40, 20]
					elif numpy.array_equal(arr[i, j], [216, 188, 160]):
						arr[i, j] = [148, 168, 100]
					elif numpy.array_equal(arr[i, j], [144, 112,  88]):
						arr[i, j] = [56, 72, 36]
					elif numpy.array_equal(arr[i, j], [180, 148, 124]):
						arr[i, j] = [88, 104, 36]
	    # create all other icon variants
		self.contentIcon = self.icon.copy()
		self.icon = pygame.transform.scale2x(self.icon)
		self.allIcons = [   self.icon,
							rot_center(self.icon, 60),
							rot_center(self.icon, 120),
							rot_center(self.icon, 180),
							rot_center(self.icon, 240),
							rot_center(self.icon, 300),
						 ]



	def updateWeaponsGfx(self):
		""" Creates the gfx for all weapons, based on the self.weapons """
		self.weaponsGfx = []    # reset
		for y in range(4):
			weapon = self.weapons[y]
			if weapon:
				_weaponGfx = weapon.picture.copy()
				# render weapon gfx background
				if weapon.ammo:
					# render ammo
					ammoText = font30.render(str(weapon.ammo), True, colors.grey, colors.almostBlack)
					rAmmoText = ammoText.get_rect()
					rAmmoText.topleft = (12, 10)
					pygame.draw.rect(_weaponGfx, colors.almostBlack, (0, 0, 41, 50), 0)
					_weaponGfx.blit(ammoText, rAmmoText)
				# render power
				powerText = font20.render(str(weapon.power), True, colors.grey)
				rPowerText = powerText.get_rect()
				rPowerText.topleft = (312, 30)
				_weaponGfx.blit(powerText, rPowerText)
				# render range
				powerText = font20.render(str(weapon.rangeMin) + ' - ' + str(weapon.rangeMax), True, colors.grey)
				rPowerText = powerText.get_rect()
				rPowerText.topleft = (601, 30)
				_weaponGfx.blit(powerText, rPowerText)
				self.weaponsGfx.append(_weaponGfx)
			else:
				self.weaponsGfx.append(pygame.image.load('gfx/weapons/empty.png'))



class HexSquare():
	""" Representation of one hex """

	def __init__(self, pos, hexType, infrastructure, unit, content = None):     # content = [owner, [unit, unit, ..]]
		self.background = bgTiles[hexType]                                          # The fundamental type of hex, e.g. Forest
		self.bgGrey = greyscale(bgTiles[hexType])                                           # Seen by player, but currently hidden (Grayscaled)
		self.bgHidden = self.bgGrey.copy()
		self.bgHidden.blit(bgTiles['unseen'], (0,0))                            # Never seen by player (mapcolour, with outline)
		self.seen = False                                       # has the square ever been visible?
		self.infra = None                                           # one of 1) Road, 2) Path, 3) Railroad 4) Trenches  (overlay gfx)
		self.unit = Unit(unit) if unit else None                        # any unit occupying the square, e.g. Infantry
		self.fogofwar = None                                    # one of 0) none, completely visible 1) Black, 2) Semi transparent (e.g. seen before, but not currently visible) 3) reddened, ie. marked as not reachable by current unit
		self.position = pos
		self.type = hexType
		self.movementModifier = bgTilesModifiers[hexType][0]
		self.battleModifier = bgTilesModifiers[hexType][1]
		self.sightModifier = bgTilesModifiers[hexType][2]
		self.movementAllowed = [0]
		if hexType == 'hqN' or hexType == 'hqN_w':
			self.name = "Headquarters"
			self.picture = pygame.image.load('gfx/units/pictures/hq.png')
			self.owner = content[0] if content else 0       # 0 for None, 1 for Entente, 2 for CP 
			self.content = Content(50)
			if content and len(content) == 2:
				for unit in content[1]:
					self.content.addUnit(Unit(unit))
			self.updateDepotColours(self.owner)
		elif hexType == 'cmpN' or hexType == 'cmpN_w':
			self.name = "Depot"
			self.picture = pygame.image.load('gfx/units/pictures/storage.png')
			self.owner = content[0] if content else 0       # 0 for None, 1 for Entente, 2 for CP 
			self.content = Content(40)
			if content and len(content) == 2:
				for unit in content[1]:
					self.content.addUnit(Unit(unit))
			self.updateDepotColours(self.owner)
		elif hexType == 'factoryE' or hexType == 'factoryE_w':
			self.name = "Factory"
			self.picture = pygame.image.load('gfx/units/pictures/factory.png')
			self.owner = content[0] if content else 0       # 0 for None, 1 for Entente, 2 for CP 
			self.content = Content(40)
			if content and len(content) == 2:
				for unit in content[1]:
					self.content.addUnit(Unit(unit))
			self.updateDepotColours(self.owner)
		else:
			self.content = False
		if infrastructure:
			self.infra = infraIcons[infrastructure]
			self.bgGrey.blit(greyscale(self.infra), (0,0))  # grayscale and blit any infrastructure on the hidden filed gfx
			if infrastructure.startswith("road"):
				self.movementModifier = 0
				self.battleModifier = 0
			if infrastructure.startswith("path"):
				self.movementModifier = 1
				self.battleModifier = 0
			if infrastructure.startswith("bridge"):
				self.movementModifier = 1
				self.battleModifier = 0
			if infrastructure.startswith("rail") or infrastructure.startswith("cross"):
				self.movementModifier = 0
				self.movementAllowed.append(1)
			if infrastructure.startswith("barbed"):
				self.movementModifier = 10
			if infrastructure.startswith("trench"):
				self.movementModifier = 10
				self.battleModifier = 10
			if infrastructure.startswith('stream') or infrastructure.startswith('lake'):	
				self.movementModifier = None
				self.movementAllowed.append(2)
				self.movementAllowed.remove(0)
		if hexType.startswith('stream') or hexType.startswith('lake'):		# when converted to infrastructure, remove this
			self.movementAllowed.append(2)
			self.movementAllowed.remove(0)



	def updateDepotColours(self, _owner, factory = False):     # 0: None, 1: CentralPowers, 2: Allies
		""" overwrites the colours on the depot/HQ hex """
		colImage = pygame.image.load('gfx/hexTypes/depotOwnership.png')
		cutoutImage = colImage.subsurface((0, _owner * 6, 35, 6))
		_bg = self.background.copy()
		if self.name == "Factory":
			rotImage = pygame.transform.rotate(cutoutImage, -60)
			_bg.blit(rotImage, (61, 9))
		else:
			_bg.blit(cutoutImage, (31, 14))
		self.background = _bg
		# colour units in depot if not owned
		for y in range(9):
			for x in range(2):
				if self.content.units[x][y]:
					self.content.units[x][y].changeColour(_owner)
					self.content.units[x][y].faction = _owner


	def getPixelCooords(self):
		""" Returns the coords where the hex is drawn """
		forskydning = 71 if (self.position[0] % 2) != 0 else 0
		pixelCooords = [self.position[1] * 142 + forskydning + 7, self.position[0] * 40 + 9]
		return pixelCooords



class ContentMenu():
	""" Representation of menu showing content of building or units """

	def __init__(self, parent):
		self.parent = parent
		self.location = (950, 50)
		self.xPos = 36
		self.yPos = 543 
		self.frame = pygame.image.load('gfx/content_frame.png')
		self.cursorGfx = pygame.image.load('gfx/cursor_content.png')
		self.actionMenu = ActionMenu(self.parent)



	def create(self, holdingUnit):
		""" Set picture and text """
		self.content = holdingUnit.content
		self.focused = [RangeIterator(9), RangeIterator(2)]
		nameText = font20.render(str(holdingUnit.name), True, colors.white)
		actualContentText = font20.render(str(holdingUnit.content.storageMax), True, colors.red) 
		maxContentText    = font20.render(str(holdingUnit.content.storageActual()), True, colors.red)
		self._frame = self.frame.copy()
		self._frame.blit(holdingUnit.picture,   (36, 40))
		self._frame.blit(nameText,              (384 - (nameText.get_width() / 2), 55))
		self._frame.blit(actualContentText,     (384 - (actualContentText.get_width() / 2), 132))
		self._frame.blit(maxContentText,        (384 - (maxContentText.get_width() / 2), 201))


	def reset(self):
		""" Move marker to 0,0 """
		self.focused[0].count = 0
		self.focused[1].count = 0


	def checkInput(self):
		if self.actionMenu.active:
			self.actionMenu.checkInput()
		else:
			for event in pygame.event.get():
				mPos = pygame.mouse.get_pos()
				# check mouseover
				if 989 < mPos[0] < 1436 and 596 < mPos[1] < 694:
					squareX = math.floor((mPos[0] - 989) / 50)
					squareY = math.floor((mPos[1] - 596) / 50)
					self.xPos = 36 + (squareX * 50) 
					self.yPos = 543 + (squareY * 50)
					self.focused[0].count = squareX
					self.focused[1].count = squareY
					if event.type == pygame.MOUSEBUTTONDOWN:
						if self.parent.mouseClick.tick() < 500:                     # if doubleclick detected
							self.endMenu()
				# Keyboard
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:    # close menu
						self.parent.mode = "normal"
						self.parent.holdEscape = True
					elif event.key == pygame.K_w:
						self.parent.mode = "normal"
						self.parent.holdEscape = True
					elif event.key == pygame.K_LEFT:
						self.focused[0].dec()
						pygame.time.wait(50)
					elif event.key == pygame.K_RIGHT:
						self.focused[0].inc()
						pygame.time.wait(50)
					elif event.key == pygame.K_UP:
						self.focused[1].dec()
						pygame.time.wait(50)
					elif event.key == pygame.K_DOWN:
						self.focused[1].inc()
						pygame.time.wait(50)
					elif event.key == pygame.K_RETURN:
						self.endMenu()
					self.xPos = 36 + (self.focused[0].get() * 50) 
					self.yPos = 543 + (self.focused[1].get() * 50)
					pygame.mouse.set_pos(self.location[0] + self.xPos + 35, self.location[1] + self.yPos + 35)


	def endMenu(self):
		_unit = self.content.units[self.focused[1].count][self.focused[0].count]
		if _unit and _unit.faction == self.parent.info.player:
			self.parent.interface.fromContent = (self.focused[1].count, self.focused[0].count)  # index of unit to move
			self.actionMenu.createSimple((self.location[0] + self.xPos + 60, self.location[1] + self.yPos - 40))


	def draw(self):
		_frame = self._frame.copy()
		for y in range(9):
			for x in range(2):
				if self.content.units[x][y]:
					_frame.blit(self.content.units[x][y].contentIcon, [38 + (y * 50), 545 + (x * 50)])
		# draw info for highlighted unit, if any
		focusX = self.focused[0].count
		focusY = self.focused[1].count
		# update unit name and info
		if self.content.units[focusY][focusX]:
			_unit = self.content.units[focusY][focusX]
			unitGUI = pygame.Surface((662, 438))
			unitGUI.blit(self.parent.interface.backgroundTextureUnit, (4, 4))
			unitPanel = self.parent.interface.unitPanel.copy()
			unitPanel.blit(self.parent.interface.flags, [3, 3], (flagIndex[_unit.country] * 88, 0, 88, 88))
			unitPanel.blit(_unit.mapIcon, [-1, -1])
			unitPanel.blit(self.parent.interface.ranksGfx, [4, 103], (_unit.experience * 88, 0, 88, 88))
			unitPanel.blit(_unit.picture, [380, 3])
			gfx = font20.render(_unit.name, True, (208, 185, 140));             unitPanel.blit(gfx, [236 - (gfx.get_width() / 2), 9])
			gfx = font20.render(self.parent.info.nameDict[_unit.faction], True, (208, 185, 140));           unitPanel.blit(gfx, [236 - (gfx.get_width() / 2), 50])
			gfx = font20.render(str(_unit.sight), True, (208, 185, 140));       unitPanel.blit(gfx, [175 - (gfx.get_width() / 2), 105])
			gfx = font20.render(str(_unit.speed), True, (208, 185, 140));       unitPanel.blit(gfx, [249 - (gfx.get_width() / 2), 105])
			gfx = font20.render(str(_unit.currentSize), True, (208, 185, 140)); unitPanel.blit(gfx, [323 - (gfx.get_width() / 2), 105])
			gfx = font20.render(str(_unit.armour), True, (208, 185, 140));      unitPanel.blit(gfx, [175 - (gfx.get_width() / 2), 155])
			gfx = font20.render(str(_unit.weight), True, (208, 185, 140));      unitPanel.blit(gfx, [249 - (gfx.get_width() / 2), 155])
			gfx = font20.render(str(_unit.fuel), True, (208, 185, 140));        unitPanel.blit(gfx, [323 - (gfx.get_width() / 2), 155])
			# mark active skills
			unitGUI.blit(self.parent.interface.unitSkills, [618, 11])
			for x in _unit.skills:
				unitGUI.blit(self.parent.interface.skillsMarker, [616, (x * 28) - 19])
			# weapons
			pygame.draw.rect(unitGUI, colors.almostBlack, (0, 218, 662, 58), 4)                         # weapons borders 1
			pygame.draw.rect(unitGUI, colors.almostBlack, (0, 326, 662, 58), 4)                         # weapons borders 2
			unitGUI.blit(_unit.weaponsGfx[0], [4, 222])
			unitGUI.blit(_unit.weaponsGfx[1], [4, 276])
			unitGUI.blit(_unit.weaponsGfx[2], [4, 330])
			unitGUI.blit(_unit.weaponsGfx[3], [4, 384])
			unitGUI.blit(unitPanel, [10, 10])
			_frame.blit(pygame.transform.scale(unitGUI, (452, 285)), [36, 237])
		# draw cursor
		_frame.blit(self.cursorGfx, (self.xPos, self.yPos))
		self.parent.display.blit(_frame, [self.location[0], self.location[1]])
		# show menu, if activated
		if self.actionMenu.active:
			self.actionMenu.draw()
		return



class WeaponMenu():
	""" Representation of the games' weapon menu """

	def __init__(self, parent):
		self.parent = parent
		self.location = (50, 50)
		self.cursorGfx = pygame.image.load('gfx/menuIcons/weaponMenuCursor.png')


	def create(self, attackingSquare):
		""" recreate the menu, calculate which buttons to include, should be called each time cursor is moved """
		self.attackingSquare = attackingSquare
		self.square = self.parent.interface.currentSquare()
		self.location  = self.parent.interface.currentSquare(True)
		self.location[0] += 110
		self.location[1] -= 80
		self.location[1] = 0 if self.location[1] < 0 else self.location[1]
		self.contents = []
		for w in self.attackingSquare.unit.weaponsGfx:
			self.contents.append([pygame.transform.scale(w, (332, 25) ) if w else None, None])
		self.noOfWeapons = 0
		for w in self.attackingSquare.unit.weapons:
			if w != None:
				self.noOfWeapons += 1
		self.focused = RangeIterator(self.noOfWeapons)
		# calculate rect for each weapon
		for weaponNo in range(self.noOfWeapons):
			_butLocation = self.location[1] + 4 + (weaponNo * 25)
			self.contents[weaponNo][1] = pygame.Rect(self.location[0], _butLocation, 332, 25)



	def checkInput(self):
		for event in pygame.event.get():
			mPos = pygame.mouse.get_pos()
			# check mouseover
			for weaponNo in range(self.noOfWeapons):
				if self.contents[weaponNo][1].collidepoint(mPos):
					self.focused.count = weaponNo
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.endMenu(self.focused.get())
			# Keyboard
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:    # close menu
					self.contents = []
					self.parent.mode = "normal"
					self.parent.holdEscape = True
				elif event.key == pygame.K_w:
					self.contents = []
					self.parent.mode = "normal"
					self.parent.holdEscape = True
				elif event.key == pygame.K_UP:
					self.focused.dec()
					pygame.mouse.set_pos(self.location[0] + 325, self.location[1] + 18 + (self.focused.get() * 25))
					pygame.time.wait(50)
				elif event.key == pygame.K_DOWN:
					self.focused.inc()
					pygame.mouse.set_pos(self.location[0] + 325, self.location[1] + 18 + (self.focused.get() * 25))
					pygame.time.wait(50)
				elif event.key == pygame.K_RETURN:
					self.endMenu(self.focused.get())



	def endMenu(self, result):
		self.parent.mode = "normal"
		self.parent.interface.generateMap() # must generate and show clean map before showing battle
		self.parent.interface.drawMap()
		pygame.display.update()
		self.parent.interface.handleBattle(self.attackingSquare, self.parent.interface.currentSquare(), self.attackingSquare.unit.weapons[result])


	def draw(self):
		self.menuBorder = pygame.draw.rect(self.parent.display, colors.almostBlack, (self.location[0] - 2, self.location[1] - 2, 336, 110)) # menu border
		self.parent.display.blit(self.contents[0][0], [self.location[0], self.location[1]])
		self.parent.display.blit(self.contents[1][0], [self.location[0], self.location[1] + 27])
		self.parent.display.blit(self.contents[2][0], [self.location[0], self.location[1] + 54])
		self.parent.display.blit(self.contents[3][0], [self.location[0], self.location[1] + 81])
		self.parent.display.blit(self.cursorGfx,  [self.location[0] - 2 , self.location[1] + (self.focused.get() * 27) - 2])





class ActionMenu():
	""" Representation of the games' action menu """

	def __init__(self, parent):
		self.parent = parent
		self.location = (50, 50)
		self.buttonAttack =     [pygame.image.load('gfx/menuIcons/attack1.png'),        pygame.image.load('gfx/menuIcons/attack2.png'),     None, 1]
		self.buttonMove =       [pygame.image.load('gfx/menuIcons/move1.png'),          pygame.image.load('gfx/menuIcons/move2.png'),       None, 2]
		self.buttonContain =    [pygame.image.load('gfx/menuIcons/containing1.png'),    pygame.image.load('gfx/menuIcons/containing2.png'), None, 3]
		self.buttonExit =       [pygame.image.load('gfx/menuIcons/exit1.png'),          pygame.image.load('gfx/menuIcons/exit2.png'),       None, 4]
		self.active = False


	def createSimple(self, location):
		""" recreate the menu to be used in content """
		self.location  = location
		self.contents = [self.buttonMove, self.buttonExit]
		self.focused = RangeIterator(len(self.contents))
		self.menuWidth = 8 + (len(self.contents) * 62)
		for butNr in range(len(self.contents)):
			_butLocation = self.location[0] + 4 + (butNr * 62)
			self.contents[butNr][2] = pygame.Rect(_butLocation, self.location[1] + 4, 62, 52)
		self.focusedArray = [0 for x in range(len(self.contents))]
		self.active = True          # currently only used in content!


	def create(self):
		""" recreate the menu, calculate which buttons to include, should be called each time cursor is moved """
		self.square = self.parent.interface.currentSquare()
		self.location  = self.parent.interface.currentSquare(True)
		self.location[0] += 110
		self.location[1] -= 30
		self.location[1] = 0 if self.location[1] < 0 else self.location[1]
		self.contents = []
		_focusedUnit = self.parent.interface.currentSquare().unit
		if _focusedUnit.speed:
			self.contents.append(self.buttonMove)
		if _focusedUnit.weapons != [None, None, None, None]:        # DEV: should also check if any ammo in each. Eclude weapons without ammo from list here
			if self.parent.interface.markAttackableSquares(True):
				self.contents.append(self.buttonAttack)
		if _focusedUnit.content:
			self.contents.append(self.buttonContain)
		self.contents.append(self.buttonExit)
		self.focused = RangeIterator(len(self.contents))
		self.menuWidth = 8 + (len(self.contents) * 62)
		for butNr in range(len(self.contents)):
			_butLocation = self.location[0] + 4 + (butNr * 62)
			self.contents[butNr][2] = pygame.Rect(_butLocation, self.location[1] + 4, 62, 52)
		self.focusedArray = [0 for x in range(len(self.contents))]



	def checkInput(self):
		""" Checks and responds to input from keyboard """
		for event in pygame.event.get():
			mPos = pygame.mouse.get_pos()
			# check mouseover
			self.focusedArray = [0 for x in range(len(self.contents))]
			for butNr in range(len(self.contents)):
				if self.contents[butNr][2].collidepoint(mPos):
					self.focused.count = butNr
					self.focusedArray[butNr] = 1
			if not 1 in self.focusedArray:  # reset count, if no button down
				self.focused.count = 0
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.endMenu(self.focused.get())
			# Keyboard
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:    # close menu
					self.parent.holdEscape = True
					self.parent.mode = "normal"
					self.focused.count = 0
				elif event.key == pygame.K_LEFT:
					self.focused.dec()
					self.focusedArray = [0 for x in range(len(self.contents))]
					self.focusedArray[self.focused.get()] = 1
					pygame.mouse.set_pos(self.location[0] + 55 + (self.focused.get() * 62), self.location[1]  + 45)
					pygame.time.wait(50)
				elif event.key == pygame.K_RIGHT:
					self.focused.inc()
					self.focusedArray = [0 for x in range(len(self.contents))]
					self.focusedArray[self.focused.get()] = 1
					pygame.mouse.set_pos(self.location[0] + 55 + (self.focused.get() * 62), self.location[1]  + 45)
					pygame.time.wait(50)
				elif event.key == pygame.K_RETURN:
					self.endMenu(self.focused.get())



	def endMenu(self, result):
		""" execute action selected in the action menu """
		if 1 in self.focusedArray:
			_butID = self.contents[result][3]
			if _butID == 1:                                 # ATTACK
				self.parent.interface.generateMap("attack")
				self.parent.mode = "selectAttack"
				self.parent.interface.fromHex = self.parent.interface.currentSquare()
			elif _butID == 2:                               # MOVE
				self.parent.interface.generateMap("move")
				self.parent.mode = "selectMoveTo"
				self.parent.interface.fromHex = self.parent.interface.currentSquare()
				self.active = False
			elif _butID == 3:                               # CONTENT
				_unit = self.parent.interface.currentSquare().unit
				self.parent.interface.contentMenu.create(_unit)
				self.parent.mode = "showContent"
			elif _butID == 4:                               # RETURN
				if self.active:     # hack!
					self.active = False
				else:
					self.parent.mode = "normal"



	def draw(self):
		self.menuBorder = pygame.draw.rect(self.parent.display, colors.almostBlack, (self.location[0], self.location[1], self.menuWidth, 60), 4)    # menu border
		for butNr in range(len(self.contents)):
			self.parent.display.blit(self.contents[butNr][self.focusedArray[butNr]],  self.contents[butNr][2])



class MapEditor():
	""" Allows editing of Hex, Infrastructur and Units """


	def __init__(self, parent):
		self.parent = parent
		summer = []
		winter = []
		for n in bgTiles.keys():
			if n.endswith("_w"):
				winter.append(n)
			else:
				summer.append(n)
		self.summerTiles = sorted(summer)
		self.winterTiles = sorted(winter)
		self.allHexData = {}
		self.allInfraData = {}
		self.allUnitData = {}
		self.selection = ""
		self.lastMenu = 0
		no = 0
		for n in self.summerTiles:
			self.allHexData[n] = [bgTiles[n], HexSquare((0, 0), n, "", ""), font20.render(str(no) + "  " + self.summerTiles[no], True, colors.black)]
			no += 1
		for n in self.winterTiles:
			self.allHexData[n] = [bgTiles[n], HexSquare((0, 0), n, "", ""), font20.render(str(no) + "  " + self.winterTiles[no - len(self.summerTiles)], True, colors.black)]
			no += 1
		self.displayNames = self.summerTiles + self.winterTiles
		# add infrastructure
		infra = []
		for n in infraIcons.keys():
			infra.append(n)
		self.infraNames = sorted(infra)
		no = 0
		for n in self.infraNames:
			self.allInfraData[n] = [infraIcons[n], font20.render(str(no) + "  " + self.infraNames[no], True, colors.black), n]
			no += 1
		# add units
		ecUnits = []
		cpUnits = []
		winter = []
		for n in unitsParameters.keys():
			if n.startswith("CP_"):
				cpUnits.append(n)
			else:
				ecUnits.append(n)
		self.ecUnitNames = sorted(ecUnits)
		self.cpUnitNames = sorted(cpUnits)
		no = 0
		for n in self.ecUnitNames:
			self.allUnitData[n] = [unitsParameters[n], font20.render(str(no) + "  " + self.ecUnitNames[no], True, colors.black), n]
			no += 1
		for n in self.cpUnitNames:
			self.allUnitData[n] = [unitsParameters[n], font20.render(str(no) + "  " + self.cpUnitNames[no - len(self.ecUnitNames)], True, colors.black), n]
			no += 1
		self.unitNames = self.ecUnitNames + self.cpUnitNames



	def saveData(self, data):
		""" saves data in json in a more readable formatting """
		with open(self.parent.cmdArgs.mapPath, "w") as json_file:
#			json.dump(data, json_file, indent=4)		# simpler, safer, but not formatted
			json_file.write("{\n")
			json_file.write('\t"mapName" :\t"%s",\n' % (data["mapName"]))
			json_file.write('\t"mapNo" :\t%s,\n' % (str(data["mapNo"])))
			json_file.write('\t"player" :\t"%s",\n' % (data["player"]))
			json_file.write('\t"tiles" :\t{\n')
			no = 0
			for line in data["tiles"]:
				_line = str(data["tiles"]["line%s" % str(no + 1)])
				convLine = _line.replace("'", '"')
				if no + 1 != len(data["tiles"]):
					convLine += ","
				json_file.write('\t\t\t\t"line%s" :\t%s\n' % (str(no + 1), convLine))
				no += 1
			json_file.write("\t\t\t\t}\n")
			json_file.write("}\n\n\n\n\n\n\n")
			return 1



	def showTileMenu(self):
		""" display the menu of hex tiles  """
		if self.lastMenu != 1:
			self.selection = ""
		self.lastMenu = 1
		self.menuRunning = True
		self.menu = pygame.Surface((600, 950))	
		pygame.draw.rect(self.menu, colors.red, (0, 0, 600, 950))						# window background
		pygame.draw.rect(self.menu, colors.black, (0, 0, 600, 950), 4)						# window border
		for no in range(len(self.summerTiles)):
			gfx = self.allHexData[self.summerTiles[no]][2]
			self.menu.blit(gfx, [50,  10 + 20 * no])
		for no in range(len(self.winterTiles)):
			gfx = self.allHexData[self.winterTiles[no]][2]
			self.menu.blit(gfx, [350, 10 + 20 * (no)])
		self.parent.display.blit(self.menu, (1124, 15))
		while self.menuRunning:
			selection = font30.render("Selection: " + str(self.selection), True, colors.black)
			pygame.draw.rect(self.parent.display, colors.red, (1400, 900, 300, 50))
			self.parent.display.blit(selection, [1400, 900])
			pygame.display.update()
			self.checkInput()
		# proccess user selection
		if self.selection and int(self.selection) <= len(self.allHexData) - 1:
			selectionName = self.displayNames[int(self.selection)]
			currentSquare = self.parent.interface.currentSquare()
			mapCursor = [self.parent.interface.cursorPos[0] + self.parent.interface.mapView[0], self.parent.interface.cursorPos[1]  + self.parent.interface.mapView[1]]
			# assign new hex object and generate map
			self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].background = bgTiles[selectionName]
			self.parent.interface.generateMap()
			# assign the name of the tile to the .json-file, to preserve the change
			with open(self.parent.cmdArgs.mapPath) as json_file:
				jsonLevelData = json.load(json_file)
				jsonLevelData["tiles"]["line" + str(mapCursor[1] + 1)][mapCursor[0]][0] = selectionName
			self.saveData(jsonLevelData)



	def showInfrastructureMenu(self):
		""" display the menu of hex tiles  """
		if self.lastMenu != 2:
			self.selection = ""
		self.lastMenu = 2
		self.menuRunning = True
		self.menu = pygame.Surface((600, 950))	
		pygame.draw.rect(self.menu, colors.red, (0, 0, 600, 950))						# window background
		pygame.draw.rect(self.menu, colors.black, (0, 0, 600, 950), 4)						# window border
		for no in range(45):
			gfx = self.allInfraData[self.infraNames[no]][1]
			self.menu.blit(gfx, [50,  10 + 20 * no])
		for no in range(45, len(self.infraNames)):
			gfx = self.allInfraData[self.infraNames[no]][1]
			self.menu.blit(gfx, [350, 10 + 20 * (no - 45)])
		self.parent.display.blit(self.menu, (1124, 15))
		while self.menuRunning:
			selection = font30.render("Selection: " + str(self.selection), True, colors.black)
			pygame.draw.rect(self.parent.display, colors.red, (1400, 900, 300, 50))
			self.parent.display.blit(selection, [1400, 900])
			pygame.display.update()
			self.checkInput()
		# proccess user selection
		if self.selection and int(self.selection) <= len(self.allInfraData) - 1:
			selectionName = self.infraNames[int(self.selection)]
			selectedInfraObject = self.allInfraData[selectionName][0]
			selectedInfraName = self.allInfraData[selectionName][2]
			currentSquare = self.parent.interface.currentSquare()
			mapCursor = [self.parent.interface.cursorPos[0] + self.parent.interface.mapView[0], self.parent.interface.cursorPos[1]  + self.parent.interface.mapView[1]]
			# assign and generate map
			self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].infra = selectedInfraObject
			self.parent.interface.generateMap()
			# assign the name of the tile to the .json-file, to preserve the change
			with open(self.parent.cmdArgs.mapPath) as json_file:
				jsonLevelData = json.load(json_file)
				jsonLevelData["tiles"]["line" + str(mapCursor[1] + 1)][mapCursor[0]][1] = selectedInfraName
			self.saveData(jsonLevelData)



	def showUnitMenu(self):
		""" display the menu of hex tiles  """
		if self.lastMenu != 3:
			self.selection = ""
		self.lastMenu = 3
		self.menuRunning = True
		self.menu = pygame.Surface((600, 950))	
		pygame.draw.rect(self.menu, colors.red, (0, 0, 600, 950))						# window background
		pygame.draw.rect(self.menu, colors.black, (0, 0, 600, 950), 4)						# window border
		for no in range(len(self.ecUnitNames)):
			gfx = self.allUnitData[self.ecUnitNames[no]][1]
			self.menu.blit(gfx, [50,  10 + 20 * no])
		for no in range(len(self.cpUnitNames)):
			gfx = self.allUnitData[self.cpUnitNames[no]][1]
			self.menu.blit(gfx, [350, 10 + 20 * no])
		self.parent.display.blit(self.menu, (1124, 15))
		while self.menuRunning:
			selection = font30.render("Selection: " + str(self.selection), True, colors.black)
			pygame.draw.rect(self.parent.display, colors.red, (1400, 900, 300, 50))
			self.parent.display.blit(selection, [1400, 900])
			pygame.display.update()
			self.checkInput()
		# proccess user selection
		if self.selection and int(self.selection) <= len(self.allUnitData) - 1:
			selectionName = self.unitNames[int(self.selection)]
			selectedUnitName = self.allUnitData[selectionName][2]
			currentSquare = self.parent.interface.currentSquare()
			mapCursor = [self.parent.interface.cursorPos[0] + self.parent.interface.mapView[0], self.parent.interface.cursorPos[1]  + self.parent.interface.mapView[1]]
			if selectedUnitName:
				selectedUnitObject = Unit(selectedUnitName)
			else:
				selectedUnitObject = None
			# assign and generate map
			self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].unit = selectedUnitObject
			self.parent.interface.generateMap()
			# assign the name of the tile to the .json-file, to preserve the change
			with open(self.parent.cmdArgs.mapPath) as json_file:
				jsonLevelData = json.load(json_file)
				jsonLevelData["tiles"]["line" + str(mapCursor[1] + 1)][mapCursor[0]][2] = selectedUnitName
			self.saveData(jsonLevelData)



	def checkInput(self):
		""" Checks and responds to input from keyboard and mouse """
		for event in pygame.event.get():
			# Quit
			if event.type == pygame.QUIT:
				pass
		# Keyboard
		keysPressed = pygame.key.get_pressed()
		if keysPressed[pygame.K_LEFT]:
			pass
		elif keysPressed[pygame.K_RIGHT]:
			pass
		elif keysPressed[pygame.K_UP]:
			pass
		elif keysPressed[pygame.K_DOWN]:
			pass
		elif keysPressed[pygame.K_RETURN]:
			self.menuRunning = False
		elif keysPressed[pygame.K_0]:
			self.selection += "0"
			time.sleep(0.2)
		elif keysPressed[pygame.K_1]:
			self.selection += "1"
			time.sleep(0.2)
		elif keysPressed[pygame.K_2]:
			self.selection += "2"
			time.sleep(0.2)
		elif keysPressed[pygame.K_3]:
			self.selection += "3"
			time.sleep(0.2)
		elif keysPressed[pygame.K_4]:
			self.selection += "4"
			time.sleep(0.2)
		elif keysPressed[pygame.K_5]:
			self.selection += "5"
			time.sleep(0.2)
		elif keysPressed[pygame.K_6]:
			self.selection += "6"
			time.sleep(0.2)
		elif keysPressed[pygame.K_7]:
			self.selection += "7"
			time.sleep(0.2)
		elif keysPressed[pygame.K_8]:
			self.selection += "8"
			time.sleep(0.2)
		elif keysPressed[pygame.K_9]:
			self.selection += "9"
			time.sleep(0.2)
		elif keysPressed[pygame.K_BACKSPACE]:
			self.selection = self.selection[:-1]
			time.sleep(0.2)



class FlipSwitch():
	""" Represents a switch with on and off-state """

	def __init__(self, Ind):
		self._value = bool(Ind)

	def flip(self):
		if self._value == True:
			self._value = False
		else:
			self._value = True

	def get(self):
		return self._value

	def getString(self):
		return str(self._value)



class RangeIterator():
	""" Represents a range of INTs from 0 -> X """

	def __init__(self, Ind, loop=True):
		self.count = 0
		self.max = Ind
		self.loop = loop

	def inc(self, count=1, changeMax=False):
		self.count += count
		if changeMax:
			self.max += count
		self._test()

	def dec(self, count=1, changeMax=False):
		self.count -= count
		if changeMax and self.max < 0:
			self.max -= count
		self._test()

	def _test(self):
		if self.count >= self.max:
			if self.loop:
				self.count = 0
			else:
				self.count = self.max
		if self.count < 0:
			if self.loop:
				self.count = self.max + self.count
			else:
				self.count = 0

	def get(self):
		return self.count
