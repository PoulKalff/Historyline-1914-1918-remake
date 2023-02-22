import pygame

pygame.init()
font20 = pygame.font.Font('freesansbold.ttf', 20)
font30 = pygame.font.Font('freesansbold.ttf', 30)
font40 = pygame.font.Font('freesansbold.ttf', 40)
font50 = pygame.font.Font('freesansbold.ttf', 50)
font60 = pygame.font.Font('freesansbold.ttf', 60)


bgTilesModifiers = 	{	'test'	 	 	: 	[10, 20, 10],			# movement penalty (0-10),  battle advantage (0-100), sight hindrance (0-10)
						'forest'	 	:	[6, 43, 8],
						'grass' 		:	[2, 4, 0],
						'hills' 		:	[4, 52, 8],
						'house' 		:	[None, None, 2],
						'mud' 			:	[3, 38, 0],
						'stone'  		: 	[3, 27, 0],
						'mountain'		: 	[10, 63, 10],
						'water'  		: 	[0, 0, 0],
						'waterStones'	: 	[None, None, 0],
						'trenches'		: 	[None, None, 0],	# no map tile yet
						'barbedWire'	: 	[9, 0, 1],			# no map tile yet
						'hqN'	  		: 	[None, None, 7],
						'hqS'  			: 	[None, None, 7],
						'hqC'  			: 	[None, None, 7],
						'hqNE'  		: 	[None, None, 7],
						'hqNW'  		: 	[None, None, 7],
						'hqSE'  		: 	[None, None, 7],
						'hqSW'  		: 	[None, None, 7],
						'cmpN'  		: 	[None, None, 7],
						'cmpS'  		: 	[None, None, 7],
						'cmpE'  		: 	[None, None, 7],
						'cmpW'  		: 	[None, None, 7],
						'mountN'  		: 	[None, None, 10],
						'mountS'  		: 	[None, None, 10],
						'mountE'  		: 	[None, None, 10],
						'mountW'  		: 	[None, None, 10],
						'stream35' 		: 	[None, None, 0],
						'stream46' 		: 	[None, None, 0],
						'stream14' 		: 	[None, None, 0],
						'stream13' 		: 	[None, None, 0],
						'stream15' 		: 	[None, None, 0],
						'stream24' 		: 	[None, None, 0],
						'stream25' 		: 	[None, None, 0],
						'stream26' 		: 	[None, None, 0],
						'stream36'		: 	[None, None, 0],
						'lakeside12'	: 	[None, None, 0],
						'lakeside16'	: 	[None, None, 0],
						'lakeside23'	: 	[None, None, 0],
						'lakeside34'	: 	[None, None, 0],
						'lakeside56'	: 	[None, None, 0],
						'lakeside123'	: 	[None, None, 0],
						'lakeside126'	: 	[None, None, 0],
						'lakeside156'	: 	[None, None, 0],
						'lakeside3456'	: 	[None, None, 0]						

					}

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


unitsParameters = 	{	'' 				:	None,
						'infantryG' 	:	{	'name'		: 'Infantry',
												'armour'	: 25,
												'speed'		: 4,
												'weight'	: 1,
												'armour'	: 250,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['gewehr98', 'lugerp08', 'bayonet' , None],
												'icon' : pygame.image.load('gfx/units/german_infantry.png'), 
											},
						'eliteInfG'		:	{	'name' : 'Elite Infantry',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['maxim', 'trenchKnife', None, None],
												'icon' : pygame.image.load('gfx/units/german_eliteInfantry.png')
											},
						'cavalryG'		:	{	'name' : 'Cavalry',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['gewehr98', 'sabre', None, None],
												'icon' : pygame.image.load('gfx/units/german_cavalry.png') 
											},
						'lArtilleryG'	:	{	'name' : 'Light Artillery',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['feldkanone16', None, None, None],
												'icon' : pygame.image.load('gfx/units/german_lightArtillery.png') 
											},
						'mArtilleryG'	:	{	'name' : 'Medium Artillery',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['lefh', None, None, None],
												'icon' : pygame.image.load('gfx/units/german_mediumArtillery.png') 
											},
						'hArtilleryG'	:	{	'name' : 'Heavy Artillery',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['morser', None, None, None],
												'icon' : pygame.image.load('gfx/units/german_heavyArtillery.png') 
											},
						'supplyCarG' 	:	{	'name' : 'SupplyCar',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: [None, None, None, None],
												'icon' : pygame.image.load('gfx/units/german_supplyCar.png') 
											},
						'bunkerG'	 	:	{	'name' : 'Bunker',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['canon75', None, None, None],
												'icon' : pygame.image.load('gfx/units/german_bunker.png') 
											},
						'infantryF'		:	{	'name' : 'Infantry',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['leeEnfield', 'revolveur', 'bayonet', None],
												'icon' : pygame.image.load('gfx/units/french_infantry.png') 
											},
						'eliteInfF'		:	{	'name' : 'Elite Infantry',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['wickers', 'trenchKnife', None, None],
												'icon' : pygame.image.load('gfx/units/french_eliteInfantry.png') 
											},
						'cavalryF'		:	{	'name' : 'Cavalry',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['leeEnfield', 'sabre', None, None],
												'icon' : pygame.image.load('gfx/units/french_cavalry.png') 
											},
						'lArtilleryF'	:	{	'name' : 'Light Artillery',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['m1902', None, None, None],
												'icon' : pygame.image.load('gfx/units/french_lightArtillery.png') 
											},
						'mArtilleryF'	:	{	'name' : 'Medium Artillery',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['canon75', None, None, None],
												'icon' : pygame.image.load('gfx/units/french_mediumArtillery.png') 
											},
						'hArtilleryF'	:	{	'name' : 'Heavy Artillery',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['canon155', None, None, None],
												'icon' : pygame.image.load('gfx/units/french_heavyArtillery.png') 
											},
						'supplyCarF' 	:	{	'name' : 'SupplyCar',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: [None, None, None, None],
												'icon' : pygame.image.load('gfx/units/french_supplyCar.png')
											},
						'bunkerF'	 	:	{	'name' : 'Bunker',
												'armour'	: 0,
												'speed'		: 0,
												'weight'	: 0,
												'armour'	: 0,
												'fuel'		: 30,
												'movement'	: 3,
												'sight'		: 3,
												'weapons'	: ['lefh', None, None, None],
												'icon' : pygame.image.load('gfx/units/french_bunker.png') 
											}
					}


weaponsParameters = 	{	'bayonet' 	:		{	'name'		: 'Bayonet',
													'air'		: None,
													'ground' 	: [200, 1],
													'water'		: None,
													'ammo'		: 999,
													'picture'	: pygame.image.load('gfx/weapons/bayonet.png'), 
												},
							'sabre'		:		{	'name'		: 'Cavalry Sabre',
													'air'		: None,
													'ground' 	: [200, 1],
													'water'		: None,
													'ammo'		: 999,
													'picture'	: pygame.image.load('gfx/weapons/sabre.png'), 
												},
							'trenchKnife' 	:	{	'name'		: 'TrenchKnife',
													'air'		: None,
													'ground' 	: [200, 1],
													'water'		: None,
													'ammo'		: 999,
													'picture'	: pygame.image.load('gfx/weapons/trenchKnife.png'), 
												},
							'revolveur' :		{	'name'		: 'revolveurM1892',
													'air'		: [100, 1],
													'ground' 	: [250, 1],
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/revolveurM1892.png'), 
												},
							'lugerp08' :		{	'name'		: 'Luger P08',
													'air'		: [100, 1],
													'ground' 	: [250, 1],
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/lugerp08.png'), 
												},
							'gewehr98' :		{	'name'		: 'Gewehr 98',
													'air'		: [150, 1],
													'ground' 	: [430, 1],
													'water'		: [430, 1],
													'ammo'		: 3,
													'picture'	: pygame.image.load('gfx/weapons/gewehr98.png'), 
												},
							'leeEnfield' 	:	{	'name'		: 'Lee-Enfield',
													'air'		: [150, 1],
													'ground' 	: [430, 1],
													'water'		: [430, 1],
													'ammo'		: 3,
													'picture'	: pygame.image.load('gfx/weapons/leeEnfield.png'), 
												},
							'maxim' 	:		{	'name'		: 'Maxim Machinegun',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/maximMachineGun.png'), 
												},
							'wickers' 	:		{	'name'		: 'Wickers Machinegun',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/wickersMachineGun.png'), 
												},
							'morser' 	:		{	'name'		: 'Morser 16',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 8,
													'picture'	: pygame.image.load('gfx/weapons/moerser16.png'), 
												},
							'canon155' 	:		{	'name'		: 'Canon de 155 L',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/canon155.png'), 
												},
							'canon75' 	:		{	'name'		: 'Wickers Machinegun',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/canon75.png'), 
												},
							'm1902' 	:		{	'name'		: '3-inch M1902',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/m1902.png'), 
												},
							'feldkanone16' 	:	{	'name'		: '7.7 cm Feldkanone 16',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/feldkanone16.png'), 
												},
							'lefh' 	:			{	'name'		: '10.5 cm leichte Feldhaubitze 16',
													'air'		: None,
													'ground' 	: None,
													'water'		: None,
													'ammo'		: 5,
													'picture'	: pygame.image.load('gfx/weapons/lefh.png'), 
												}
						}


class colorList:
	black =				(0, 0, 0)
	white =				(255, 255, 255)
	red =				(255, 0, 0)
	darkRed =			(165, 32, 32)
	cyan =				(0, 255, 255)
	green =				(0, 255, 0)
	grey =				(150, 150, 150)
	darkGrey =			(50, 50, 50)
	almostBlack =		(20, 20, 20)
	orange =			(220, 162, 57)
	green =				(70, 180, 50)
	blue =				(80, 120, 250)
	background =		(55, 55, 55)
	yellow = 			(255, 255, 0)
	bi3 =				(68, 136, 77)
	historylineDark =	(49, 48, 33)
	historylineLight =	(107, 105, 90)


class renderObject():
	""" An object to be rendered """

	def __init__(self, frame, coord, pri, descr='None'):
		self.frame = frame
		self.coordinate = coord
		self.priority = pri
		self.description = descr



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
	# (v3) Represents a range of INTs from 0 -> X

	def __init__(self, Ind, loop=True):
		self.current = 0
		self.max = Ind
		self.loop = loop

	def inc(self, count=1):
		self.current += count
		self._test()

	def dec(self, count=1):
		self.current -= count
		self._test()

	def incMax(self, incCurrent = True):
		""" Increase both value and max valuse """
		self.max += 1
		if incCurrent:
			self.current += 1
		self._test()

	def decMax(self, count=1):
		""" Increase both value and max valuse """
		self.max -= count
		self.current -= count
		self._test()

	def _test(self):
		""" Tests that all is well, should be called after any change in values"""
		self.max = 0 if self.max < 0 else self.max
		if self.loop:
			if self.current > self.max:
				self.current -= self.max + 1
			elif self.current < 0:
				self.current += self.max + 1
		elif not self.loop:
			if self.current >= self.max:
				self.current = self.max
			elif self.current < 0:
				self.current = 0

	def get(self):
		return self.current



class PlayerMovement():
	""" Representation of the current movement of the player. (Is it necessarry? Could it be simplified?) """

	def __init__(self):
		self.left = False
		self.right = False
		self.up = False
		self.down = False

	def verticalMove(self, direction):
		self.down = False
		if direction:
			self.left = False
			self.right = True
		else:
			self.left = True
			self.right = False

	def goUp(self):
		self.up = True
		self.down = False

	def goDown(self):
		self.up = False
		self.down = True

	def stop(self):
		self.left = False
		self.right = False
		self.up = False
		self.down = False

	def isMoving(self):
		if self.left or self.right or self.up or self.down:
			return True
		else:
			return False

	def show(self):
		print(int(self.left), int(self.right), int(self.up), int(self.down))