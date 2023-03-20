import sys
import json
import time
import pygame
import numpy as np
import pygame.surfarray as surfarray
from hlrData import *

# --- Variables / Ressources ----------------------------------------------------------------------

colors = colorList
developerMode = True

# --- Classes -------------------------------------------------------------------------------------


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
	""" Representation of one unit	"""

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
			self.weapons = []
			self.maxSize = 10		# all units size 10?
			self.currentSize = 10
			self.faction = 'Central Powers' if self.country in ['Germany', 'Austria', 'Bulgaria', 'Ottoman'] else 'Entente Cordial'
			for w in data['weapons']:
				if w:
					self.weapons.append(Weapon(w))
				else:
					self.weapons.append(None)
			self.picture = data['picture']
			rawIcon = data['icon']
			# if central powers, rotate and colourize icon
			if self.faction == 'Central Powers':
				arr = pygame.surfarray.pixels3d(rawIcon)
				for i in range(48):
					for j in range(48): # loop over the 2d array
						if np.array_equal(arr[i, j], [164, 132, 112]):
							arr[i, j] = [72, 88, 52]
						elif np.array_equal(arr[i, j], [80, 68, 52]):
							arr[i, j] = [24, 40, 20]
						elif np.array_equal(arr[i, j], [216, 188, 160]):
							arr[i, j] = [148, 168, 100]
						elif np.array_equal(arr[i, j], [144, 112,  88]):
							arr[i, j] = [56, 72, 36]
						elif np.array_equal(arr[i, j], [180, 148, 124]):
							arr[i, j] = [88, 104, 36]
			rawIcon = pygame.transform.scale2x(rawIcon)
			self.allIcons = [	rot_center(rawIcon, 60),
								rot_center(rawIcon, 120), 
								rot_center(rawIcon, 180), 			
								rot_center(rawIcon, 240), 
								rot_center(rawIcon, 300), 
								rawIcon
							 ]
			self.mapIcon = self.allIcons[2] if self.faction == 'Central Powers' else self.allIcons[5]




class HexSquare():
	""" Representation of one hex """

	def __init__(self, pos, hexType, infrastructure, unit):
		self.background = bgTiles[hexType]	 										# The fundamental type of hex, e.g. Forest
		self.bgGrey = greyscale(bgTiles[hexType])	 										# Seen by player, but currently hidden (Grayscaled)
		self.bgHidden = self.bgGrey.copy()
		self.bgHidden.blit(bgTiles['unseen'], (0,0))							# Never seen by player (mapcolour, with outline)
		self.seen = False										# has the square ever been visible?
		self.infra = None											# one of 1) Road, 2) Path, 3) Railroad 4) Trenches 	(overlay gfx)
		self.unit = Unit(unit) if unit else None						# any unit occupying the square, e.g. Infantry
		self.fogofwar = None									# one of 0) none, completely visible 1) Black, 2) Semi transparent (e.g. seen before, but not currently visible) 3) reddened, ie. marked as not reachable by current unit
		self.position = pos
		self.movementModifier = bgTilesModifiers[hexType][0]
		self.battleModifier = bgTilesModifiers[hexType][1]
		self.sightModifier = bgTilesModifiers[hexType][2]
		if infrastructure:
			self.infra = infraIcons[infrastructure]
			self.bgGrey.blit(greyscale(self.infra), (0,0))	# grayscale and blit any infrastructure on the hidden filed gfx
			if infrastructure.startswith("road"):
				self.movementModifier = 0
				self.battleModifier = 0
			elif infrastructure.startswith("path"):
				self.movementModifier = 1
				self.battleModifier = 0
			elif infrastructure.startswith("bridge"):
				self.movementModifier = 1
				self.battleModifier = 0
			elif infrastructure.startswith("rail"):
				self.movementModifier = 0
			elif infrastructure.startswith("barbed"):
				self.movementModifier = 10
			elif infrastructure.startswith("trench"):
				self.movementModifier = 10
				self.battleModifier = 10





class ActionMenu():
	""" Representation of the games' action menu """

	def __init__(self, display):
		self.display = display
		self.active = False
		self.location = (50, 50)
		self.focused = RangeIterator(4)
		self.focusedArray = [1,0,0,0]
		self.buttonAttack =		[pygame.image.load('gfx/menuIcons/attack1.png'), 		pygame.image.load('gfx/menuIcons/attack2.png')]
		self.buttonMove =		[pygame.image.load('gfx/menuIcons/move1.png'), 			pygame.image.load('gfx/menuIcons/move2.png')]
		self.buttonContain =	[pygame.image.load('gfx/menuIcons/containing1.png'),	pygame.image.load('gfx/menuIcons/containing2.png')]
		self.buttonExit =		[pygame.image.load('gfx/menuIcons/exit1.png'), 			pygame.image.load('gfx/menuIcons/exit2.png')]


	def show(self, activeSquare):
		self.square = activeSquare
		if not self.square.fogofwar and self.square.unit:
			self.active = True


	def hide(self):
		self.active = False



	def checkInput(self):
		""" Checks and responds to input from keyboard """
		for event in pygame.event.get():
			keysPressed = pygame.key.get_pressed()
			if keysPressed[pygame.K_LEFT]:
				self.focused.dec()
			elif keysPressed[pygame.K_RIGHT]:
				self.focused.inc()
			elif keysPressed[pygame.K_RETURN]:
				result = self.focused.get()
				self.active = False
				self.focused.count = 0
				self.focusedArray = [0, 0, 0, 0]
				self.focusedArray[self.focused.get()] = 1
				return result
			self.focusedArray = [0, 0, 0, 0]
			self.focusedArray[self.focused.get()] = 1



	def draw(self):
		if self.active:
			pygame.draw.rect(self.display, colors.almostBlack, (self.location[0], self.location[1], 256, 60), 4)			# menu border
			self.display.blit(self.buttonAttack[self.focusedArray[0]],  [self.location[0] + 4,   self.location[1] + 4])
			self.display.blit(self.buttonMove[self.focusedArray[1]],    [self.location[0] + 66,  self.location[1] + 4])
			self.display.blit(self.buttonContain[self.focusedArray[2]], [self.location[0] + 128, self.location[1] + 4])
			self.display.blit(self.buttonExit[self.focusedArray[3]],    [self.location[0] + 190, self.location[1] + 4])





class GUI():
	""" Representation of the background """

	def __init__(self, parent, levelNo):
		self.parent = parent
		self.mainMap = []
		# read data
		with open('levels/level' + str(levelNo) + '.json') as json_file:
			jsonLevelData = json.load(json_file)
		self.squareWidth = len(jsonLevelData["tiles"]["line1"])			# 8 for level 1
		self.squareHeight = len(jsonLevelData["tiles"])					# 47 for level 1
		self.pixelWidth = self.squareWidth * 142
		self.pixelHeight = self.squareHeight * 40
		self.flagIndex = {'Germany' : 0, 'France' : 1}
		self.cursorGfx = pygame.image.load('gfx/cursor.png')
		self.hexBorder = pygame.image.load('gfx/hexBorder.png')
		self.skillsMarker = pygame.image.load('gfx/skills_marker.png')
		self.progressBar = pygame.image.load('gfx/progressBar.png')
		self.iProgressBar = pygame.image.load('gfx/progressBarI.png')
		self.flags = pygame.image.load('gfx/flags.png')
		self.noWeapon = pygame.image.load('gfx/weapons/empty.png')
		self.ranksGfx = pygame.image.load('gfx/ranks.png')
		self.unitPanel = pygame.image.load('gfx/unit_panel.png')
		self.unitSkills = pygame.image.load('gfx/skills.png')
		self.backgroundTexture = pygame.image.load('gfx/steelTexture.png')
		self.backgroundTextureUnit = pygame.image.load('gfx/steelTextureUnit.png')
		self.backgroundTextureTerrain = pygame.image.load('gfx/steelTextureTerrain.png')
		self.semiTransparent = pygame.image.load('gfx/hexTypes/hex_semiTransparent.png')
		self.actionMenu = ActionMenu(self.parent.display)
		self.cursorPos = [0,0]									# x,y index of cursor position on SCREEN, not on map!
		self.mapView = [0, 0]										# the starting coordinates of the map
		# texts
		self.movementModifierText = font20.render('Movement Penalty', True, colors.black) 	# [movementModifierText, rMovementModifierText]
		self.battleModifierText = font20.render('Battle Advantage', True, colors.black)		#[battleModifierText, rBattleModifierText]
		self.sightModifierText = font20.render('Sight Hindrance', True, colors.black)				# [sightModifierText, rSightModifierText]
		for nrX, value in enumerate(jsonLevelData['tiles'].values()):
			line = []
			for nrY, square in enumerate(value):
				line.append(HexSquare((nrX, nrY), *square))
			self.mainMap.append(line)
		self.mapWidth = len(self.mainMap[0])
		self.mapHeight = len(self.mainMap)
		self.generateMap()



	def moveUnit(self):
		""" prints an overlay on each hexSquare on the map that the current unit cannot move to
			must be called each time player selects move """
		unitSpeed = self.currentSquare().unit.speed
		movingFrom = self.currentSquare().position
		x, y = movingFrom
		withinRange = [(x,y)]	# coord of self
		for iteration in range(unitSpeed):
			for coord in set(withinRange):
				neighbors = adjacentHexes(*coord, self.mapWidth, self.mapHeight)
				withinRange += neighbors
		movableSquares = list(set(withinRange))
		movableSquares.remove(movingFrom)
		obstructed = []
		for x, y in movableSquares:
			if self.mainMap[x][y].fogofwar != 0:
				obstructed.append((x,y))
			elif self.mainMap[x][y].unit:
				obstructed.append((x,y))
			elif self.mainMap[x][y].movementModifier == None:
				obstructed.append((x,y))
		# remove obstacaled squares
		for pos in obstructed:
			movableSquares.remove(pos)
		# mark squares not possible to target 
		for x in range(self.mapHeight):
			for y in range(len(self.mainMap[x])):
				if self.mainMap[x][y].fogofwar == 0 and (x,y) not in movableSquares:
					self.mainMap[x][y].fogofwar = 3
		# move unit

		# regenerate map







	def calculateFOW(self):
		""" checks each hexSquare on the map and marks it as visible if it can be seen by any friendly unit 
			must be called each time player moves a piece"""
		for x in range(self.mapHeight):
			for y in range(len(self.mainMap[x])):
				self.mainMap[x][y].fogofwar = 2 if self.mainMap[x][y].seen else 1
		for x in range(self.mapHeight):
			for y in range(len(self.mainMap[x])):
				if self.mainMap[x][y].unit:
					if self.mainMap[x][y].unit.faction == self.parent.playerSide:			# only mark visible if it is our own unit
						withinSight = [(x,y)]	# coord of self
						for iteration in range(self.mainMap[x][y].unit.sight):
							for coord in set(withinSight):
								neighbors = adjacentHexes(*coord, self.mapWidth, self.mapHeight)
								withinSight += neighbors
						for c in set(withinSight):
							try:
								self.mainMap[c[0]][c[1]].fogofwar = 0
								self.mainMap[c[0]][c[1]].seen = True
							except:
								print("Coordinate exceed map size in calculateFOW():", c)


	def currentSquare(self, coords = False):
		""" returns the currently hightlighted hexSquare """
		mapCursor = [self.cursorPos[0] + self.mapView[0], self.cursorPos[1]  + self.mapView[1]]
		if coords:
			return mapCursor
		else:
			return self.mainMap[mapCursor[1]][mapCursor[0]]



	def draw(self):
		""" draws all parts of the interface """
		self.parent.display.blit(self.backgroundTexture, (0,0))
		pygame.draw.rect(self.parent.display, colors.almostBlack, (0, 0, 1800, 1000), 4)							# window border
		self.drawMap()
		self.drawMiniMap()
		self.drawTerrainGUI()
		self.drawUnitGUI()
		self.actionMenu.draw()



	def generateMap(self, movingUnit = False):
		""" generate the basic map to be used to draw main map and minimap """	
		self.calculateFOW()
		if movingUnit:
			self.markMovableSquares()





		width = (self.mapWidth * 142) - 46  # dunno why 46 must be subtracted?
		height = (self.mapHeight + 1) * 40
		self.map = pygame.Surface((width, height))
		self.map.fill(colors.historylineDark)
		for x in range(self.mapHeight):
			for y in range(len(self.mainMap[x])):
				square = self.mainMap[x][y]
				forskydning = 71 if (x % 2) != 0 else 0
		 		# one of 0) none, completely visible 1) Black, 2) Semi transparent (e.g. seen before, but not currently visible) 3) reddened, ie. marked as not reachable by current unit
				if square.fogofwar == 0:	# fully visible
					self.map.blit(square.background, [y * 142 + forskydning, x * 40])
					if square.infra:	self.map.blit(square.infra, [y * 142 + forskydning, x * 40])
					if square.unit:		self.map.blit(square.unit.mapIcon, [y * 142 + forskydning, x * 40 - 9])
				elif square.fogofwar == 1:	# fully hidden, black
					self.map.blit(square.bgHidden, [y * 142 + forskydning, x * 40])
				elif square.fogofwar == 2:	# hidden, but seen before, grey
					self.map.blit(square.bgGrey, [y * 142 + forskydning, x * 40])
				elif square.fogofwar == 3:	# unreachable to move to, normal but overlayed
					self.map.blit(square.background, [y * 142 + forskydning, x * 40])
					if square.infra:	self.map.blit(square.infra, [y * 142 + forskydning, x * 40])
					if square.unit:		self.map.blit(square.unit.mapIcon, [y * 142 + forskydning, x * 40 - 9])
					self.map.blit(self.semiTransparent, [y * 142 + forskydning, x * 40])
				if developerMode:	# put as number on square
					text = self.parent.devModeFont.render(str(x) + '/' + str(y), True, (255,0,0))
					image = pygame.Surface((96, 80), pygame.SRCALPHA)
					textRect = text.get_rect()
					textRect.topleft = (20, 20)
					image.blit(text, textRect)
					self.map.blit(image, [y * 142 + forskydning, x * 40])
		# generate minimap
		width = (self.mapWidth * 142) - 46			# dunno why 46 must be subtracted?
		height = (self.mapHeight + 1) * 40
		tempMiniMap = self.map.copy()
		# scale minimap to max height of minimap area (392)
		scaleFactor = 392 / height
		self.miniMap = pygame.transform.scale(tempMiniMap, (width * scaleFactor, height * scaleFactor))
#		pygame.image.save(self.map, 'generatedMap.png')



	def drawMap(self):
		pygame.draw.rect(self.parent.display, colors.almostBlack, (15, 15, 1098, 968), 4)								# map border (main map = 1098 / 968)
		self.parent.display.blit(self.map, [19, 19], (self.mapView[0], self.mapView[1] * 40, 1098 + self.mapView[0], 960))		# blit visible area of map
		forskydning = 71 if (self.cursorPos[1] % 2) != 0 else 0
		self.parent.display.blit(self.cursorGfx, [self.cursorPos[0] * 142 + forskydning + 7, self.cursorPos[1] * 40 + 9])
		return 1



	def drawMiniMap(self):
		pygame.draw.rect(self.parent.display, colors.darkGrey , (1124, 15,  662, 400), 0)			# minimap area background
		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 15,  662, 400), 4)					# minimap area border
		miniMapXCoord =	1459 - int(self.miniMap.get_width() / 2)
		w, h = self.miniMap.get_size()
		self.parent.display.blit(self.miniMap, [miniMapXCoord, 19])
		pygame.draw.rect(self.parent.display, colors.almostBlack, (miniMapXCoord - 4, 15,  w + 8, h + 8), 4)					# minimap border
		# calculate percentage of area displayed
		widthPercentageDisplayed = 8 / self.mapWidth
		heightPercentageDisplayed = 12 / int((self.mapHeight + 1) / 2)
		# draw a rectangle to show the field of view on the miniMap
		markerOffsetX = self.mapView[0] / self.mapWidth				# calculate marker offset
		markerOffsetY = self.mapView[1] / self.mapHeight
		pygame.draw.rect(self.parent.display, colors.red, (	miniMapXCoord -2 + int(w * markerOffsetX), 17 + int(h * markerOffsetY), (w + 4) * widthPercentageDisplayed, (h) * heightPercentageDisplayed), 2)



	def drawTerrainGUI(self):
		""" fetches cursor position and fills out info on unit and terrain """
		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 426, 662, 118), 4)		# middle window border
		self.parent.display.blit(self.backgroundTextureTerrain, (1128, 430))
		square = self.currentSquare()
		if not square.fogofwar:
			pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 426, 662, 118), 4)		# middle window border
			self.parent.display.blit(self.backgroundTextureTerrain, (1128, 430))
			self.parent.display.blit(self.movementModifierText, (1270, 445))
			self.parent.display.blit(self.battleModifierText, (1270, 475))
			self.parent.display.blit(self.sightModifierText, (1270, 505))
			self.parent.display.blit(square.background, [1144, 446])
			if square.infra:	self.parent.display.blit(square.infra, [1144, 446])
			self.parent.display.blit(self.hexBorder, [1142, 444])
			if square.movementModifier != None:
				self.parent.display.blit(self.progressBar, [1460, 444], (0, 0, square.movementModifier * 30, 20))
			else:
				self.parent.display.blit(self.iProgressBar, [1460, 444])
			if square.battleModifier != None:
				self.parent.display.blit(self.progressBar, [1460, 474], (0, 0, square.battleModifier * 3, 20))	
			else:
				self.parent.display.blit(self.iProgressBar, [1460, 474])
			self.parent.display.blit(self.progressBar, [1460, 504], (0, 0, square.sightModifier * 30, 20))



	def drawUnitGUI(self):
		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 555, 662, 428), 4)						# lower window border
		self.parent.display.blit(self.backgroundTextureUnit, (1128, 559))
		square = self.currentSquare()
		if not square.fogofwar and square.unit:
			self.parent.display.blit(self.unitPanel, [1135, 570])
			self.parent.display.blit(self.flags, [1145, 573], (self.flagIndex[square.unit.country] * 88, 0, 88, 88))
			self.parent.display.blit(square.unit.mapIcon, [1141, 569])
			pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 763, 662, 58), 4)							# weapons borders 1
			pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 871, 662, 58), 4)							# weapons borders 2
			self.parent.display.blit(self.unitSkills, [1750, 565])
			self.parent.display.blit(self.ranksGfx, [1156, 676], (square.unit.experience * 66, 0, 66, 66))
			self.parent.display.blit(square.unit.picture, [1522, 573])
			gfx = font20.render(square.unit.name, True, (208, 185, 140)); self.parent.display.blit(gfx, [1380 - (gfx.get_width() / 2), 575])
			gfx = font20.render(square.unit.faction, True, (208, 185, 140)); self.parent.display.blit(gfx, [1380 - (gfx.get_width() / 2), 610])
			gfx = font20.render(str(square.unit.sight), True, (208, 185, 140)); self.parent.display.blit(gfx, [1318 - (gfx.get_width() / 2), 662])
			gfx = font20.render(str(square.unit.speed), True, (208, 185, 140)); self.parent.display.blit(gfx, [1392 - (gfx.get_width() / 2), 662])
			gfx = font20.render(str(square.unit.currentSize), True, (208, 185, 140)); self.parent.display.blit(gfx, [1462 - (gfx.get_width() / 2), 662])
			gfx = font20.render(str(square.unit.armour), True, (208, 185, 140)); self.parent.display.blit(gfx, [1318 - (gfx.get_width() / 2), 712])
			gfx = font20.render(str(square.unit.weight), True, (208, 185, 140)); self.parent.display.blit(gfx, [1392 - (gfx.get_width() / 2), 712])
			gfx = font20.render(str(square.unit.fuel), True, (208, 185, 140)); self.parent.display.blit(gfx, [1462 - (gfx.get_width() / 2), 712])
			# mark active skills
			for x in square.unit.skills:
				self.parent.display.blit(self.skillsMarker, [1748, 535 + (x * 28)])
			# weapons
			yCoords = [767, 821, 875, 929]			
			for y in range(4):
				weapon = square.unit.weapons[y]
				if weapon:
					# render weapon gfx background
					self.parent.display.blit(weapon.picture, [1128, yCoords[y]])
					if weapon.ammo:
						# render ammo
						ammoText = font30.render(str(weapon.ammo), True, colors.grey, colors.almostBlack)
						rAmmoText = ammoText.get_rect()
						rAmmoText.topleft = (1140, yCoords[y] + 10)
						pygame.draw.rect(self.parent.display, colors.almostBlack, (1128, yCoords[y], 41, 50), 0)
						self.parent.display.blit(ammoText, rAmmoText)
					# render power
					powerText = font20.render(str(weapon.power), True, colors.grey)
					rPowerText = powerText.get_rect()
					rPowerText.topleft = (1441, yCoords[y] + 30)
					self.parent.display.blit(powerText, rPowerText)
					# render range
					powerText = font20.render(str(weapon.rangeMin) + ' - ' + str(weapon.rangeMax), True, colors.grey)
					rPowerText = powerText.get_rect()
					rPowerText.topleft = (1728, yCoords[y] + 30)
					self.parent.display.blit(powerText, rPowerText)
				else:
					self.parent.display.blit(self.noWeapon, [1128, yCoords[y]])



	def cursorMove(self, direction):
		""" Values are left, right, up, down """
		verticalOdd = self.cursorPos[1] % 2 == 0
		if direction == 'Up':
				if self.cursorPos[1] > 1:
					self.cursorPos[1] -= 2
				else:
					if self.mapView[1] > 1:
						self.mapView[1] -= 2		# NB : ONLY even numbers, as two lines must be drawn as one!
		elif direction == 'Down':
			if self.cursorPos[1] < 21:
				self.cursorPos[1] += 2
			else:
				if self.mapView[1] + 24 < self.squareHeight:
					self.mapView[1] += 2		# NB : ONLY even numbers, as two lines must be drawn as one!
		elif direction == 'Left':
			if self.cursorPos[0] > 0:
				if verticalOdd:
					self.cursorPos[1] += 1
					self.cursorPos[0] -= 1
				else:
					self.cursorPos[1] -= 1
			else:
				if self.cursorPos[1] % 2 != 0:
					self.cursorPos[1] -= 1
		elif direction == 'Right':
			if self.cursorPos[0] < 7:
				if verticalOdd:
					self.cursorPos[1] += 1
				else:
					self.cursorPos[0] += 1
					self.cursorPos[1] -= 1
		# prevent cursor exiting map
		if self.cursorPos[0] < 0: self.cursorPos[0] = 0
		if self.cursorPos[1] < 0: self.cursorPos[1] = 0
		if self.cursorPos[1] > 22: self.cursorPos[1] = 21




