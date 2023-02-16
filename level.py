import sys
import json
import time
import pygame
from helperFunctions import *

# --- Variables / Ressources ----------------------------------------------------------------------

colors = colorList
developerMode = False
# texts used on map
movementModifierText = font20.render('Movement Penalty', True, colors.black)
rMovementModifierText = movementModifierText.get_rect()
rMovementModifierText.topleft = (1250, 435)
battleModifierText = font20.render('Battle Advantage', True, colors.black)
rBattleModifierText = battleModifierText.get_rect()
rBattleModifierText.topleft = (1250, 465)
sightModifierText = font20.render('Sight Hindrance', True, colors.black)
rSightModifierText = sightModifierText.get_rect()
rSightModifierText.topleft = (1250, 495)


# --- Classes -------------------------------------------------------------------------------------


class Weapon():
	""" Representation of one weapon """

	def __init__(self, key):
		if key:
			data = weaponsParameters[key]
			self.name = data['name']
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
			self.maxSize = 10		# all units size 10?
			self.currentSize = 10
			self.fuel = data['fuel']
			self.movement = data['movement']
			self.sight = data['sight']
			self.weapons = []
			for w in data['weapons']:
				if w: self.weapons.append(Weapon(w))
			self.mapIcon = data['icon']




class HexSquare():
	""" Representation of one hex """

	def __init__(self, hexType, infrastructure, unit):
		self.background = bgTiles[hexType]	 										# The fundamental type of hex, e.g. Forest
		self.infra = None											# one of 1) Road, 2) Path, 3) Railroad 4) Trenches 	(overlay gfx)
		self.unit = Unit(unit) if unit else None						# any unit occupying the square, e.g. Infantry
		self.fogofwar = None									# one of 1) Black, 2) Semi transparent (e.g. seen before, but not currently)
		self.movementModifier = bgTilesModifiers[hexType][0]
		self.battleModifier = bgTilesModifiers[hexType][1]
		self.sightModifier = bgTilesModifiers[hexType][2]
		if infrastructure:
			self.infra = infraIcons[infrastructure]
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


class Map(list):
	""" Representation of the background """

	def __init__(self, parent, levelNo):
		self.parent = parent
		# read data
		with open('levels/level' + str(levelNo) + '.json') as json_file:
			jsonLevelData = json.load(json_file)
		self.squareWidth = len(jsonLevelData["tiles"]["line1"])			# 8 for level 1
		self.squareHeight = len(jsonLevelData["tiles"])					# 47 for level 1
		self.pixelWidth = self.squareWidth * 142
		self.pixelHeight = self.squareHeight * 40
		self.cursorGfx = pygame.image.load('gfx/cursor.png')
		self.infinityGfx = pygame.image.load('gfx/infinity.png')
		self.progressBar = pygame.image.load('gfx/progressBar.png')
		self.iProgressBar = pygame.image.load('gfx/progressBarI.png')
		self.cursorPos = [0,0]									# x,y index of cursor position on SCREEN, not on map!
		self.mapView = [0, 0]										# the starting coordinates of the map
		# texts
		self.movementModifierText = [movementModifierText, rMovementModifierText]
		self.battleModifierText = [battleModifierText, rBattleModifierText]
		self.sightModifierText =  [sightModifierText, rSightModifierText]
		for value in jsonLevelData['tiles'].values():
			line = []
			for square in value:
				line.append(HexSquare(*square))
			self.append(line)



	def draw(self):
		self.parent.display.fill([49, 48, 33])
		pygame.draw.rect(self.parent.display, (107, 105, 90), (19, 19, 1090, 960), 0)							# map background
		for x in range(23):
			for y in range(len(self[x])):
				square = self[x + self.mapView[1]][y]
				forskydning = 71 if (x % 2) != 0 else 0
				self.parent.display.blit(square.background, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
				if square.infra:	self.parent.display.blit(square.infra, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
				if square.unit:		self.parent.display.blit(square.unit.mapIcon, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
				if developerMode:
					text = self.parent.devModeFont.render(str(x + 1) + '/' + str(y + 1), True, (255,0,0))
					image = pygame.Surface((96, 80), pygame.SRCALPHA)
					textRect = text.get_rect()
					textRect.topleft = (20, 20)
					image.blit(text, textRect)
					self.parent.display.blit(image, [self.parent.viewDsp[0] + (y * 142 + forskydning), self.parent.viewDsp[1] + (x * 40)])
		forskydning = 71 if (self.cursorPos[1] % 2) != 0 else 0
		self.parent.display.blit(self.cursorGfx, [self.parent.viewDsp[0] + (self.cursorPos[0] * 142 + forskydning), self.parent.viewDsp[1] + (self.cursorPos[1] * 40)])
		# window borders
		pygame.draw.rect(self.parent.display, colors.almostBlack, (0, 0, 1800, 1000), 4)							# window border
		pygame.draw.rect(self.parent.display, colors.almostBlack, (15, 15, 1098, 968), 4)								# map border (main map = 1098 / 968)
		pygame.draw.rect(self.parent.display, colors.historylineLight , (1124, 15,  662, 400), 0)					# minimap background
		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 15,  662, 400), 4)							# minimap border


		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 426, 662, 100), 4)							# middle window border
		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 537, 662, 446), 4)						# lower window border
		self.parent.display.blit(*self.movementModifierText)
		self.parent.display.blit(*self.battleModifierText)
		self.parent.display.blit(*self.sightModifierText)
		return 1



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




