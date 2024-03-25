import sys
import json
import time
import copy
import pygame
import random
import numpy as np
import pygame.surfarray as surfarray
from hlrData import *

# --- Variables / Ressources ----------------------------------------------------------------------

colors = colorList

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
			self.storageMax = data['storageMax']
			self.storageActual = 0
			self.sight = data['sight']
			self.fuel = data['fuel']
			self.experience = 0
			self.skills = data['skills']
			self.weapons = []
			self.weaponsGfx = []
			self.maxSize = 10		# all units size 10?
			self.currentSize = 10
			self.faction = 'Central Powers' if self.country in ['Germany', 'Austria', 'Bulgaria', 'Ottoman'] else 'Entente Cordial'
			if self.storageMax > 0:
				self.content = []
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
			self.allIcons = [	rawIcon,
								rot_center(rawIcon, 60),
								rot_center(rawIcon, 120),
								rot_center(rawIcon, 180),
								rot_center(rawIcon, 240),
								rot_center(rawIcon, 300),
							 ]
			self.mapIcon = self.allIcons[3] if self.faction == 'Central Powers' else self.allIcons[0]
			self.updateWeaponsGfx()


	def updateWeaponsGfx(self):
		""" Creates the gfx for all weapons, based on the self.weapons """
		self.weaponsGfx = []	# reset
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
		if hexType == 'hqN':
			self.name = "Headquarters"
			self.content = []
			self.storageMax = 50
			self.storageActual = 0
			self.picture = pygame.image.load('gfx/units/pictures/hq.png')
		elif hexType == 'cmpN':
			self.name = "Depot"
			self.content = []
			self.storageMax = 40
			self.storageActual = 0
			self.picture = pygame.image.load('gfx/units/pictures/storage.png')
		else:
			self.content = False
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
		self.contents = []
		self.xPos = 36
		self.yPos = 543 
		self.frame = pygame.image.load('gfx/content_frame.png')
		self.cursorGfx = pygame.image.load('gfx/cursor_content.png')



	def create(self, holdingUnit):
		""" Set picture and text """
		self.focused = [RangeIterator(9), RangeIterator(2)]
		nameText = font20.render(str(holdingUnit.name), True, colors.white)
		actualContentText = font20.render(str(holdingUnit.storageMax), True, colors.red) 
		maxContentText    = font20.render(str(holdingUnit.storageActual), True, colors.red)
		self._frame = self.frame.copy()
		self._frame.blit(holdingUnit.picture,	(36, 40))
		self._frame.blit(nameText, 				(384 - (nameText.get_width() / 2), 55))
		self._frame.blit(actualContentText,		(384 - (actualContentText.get_width() / 2), 132))
		self._frame.blit(maxContentText,		(384 - (maxContentText.get_width() / 2), 201))



	def checkInput(self):
		for event in pygame.event.get():
			mPos = pygame.mouse.get_pos()
			# check mouseover
#			for weaponNo in range(self.noOfWeapons):
#				if self.contents[weaponNo][1].collidepoint(mPos):
#					self.focused.count = weaponNo


# Must be able to select with mouse. Get grid coord






			if event.type == pygame.MOUSEBUTTONDOWN:
				self.endMenu(self.focused.get())
			# Keyboard
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:	# close menu
					self.contents = []
					self.parent.mode = "normal"
					self.parent.holdEscape = True
				elif event.key == pygame.K_w:
					self.contents = []
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
					self.endMenu(self.focused.get())
				self.xPos = 36 + (self.focused[0].get() * 50) 
				self.yPos = 543 + (self.focused[1].get() * 50)
				pygame.mouse.set_pos(self.location[0] + self.xPos + 35, self.location[1] + self.yPos + 35)



	def endMenu(self, result):
		self.parent.mode = "normal"
		self.parent.interface.drawMap()
		pygame.display.update()



	def draw(self):
		_frame = self._frame.copy()
		_frame.blit(self.cursorGfx, (self.xPos, self.yPos))
		self.parent.display.blit(_frame, [self.location[0], self.location[1]])

























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
				if event.key == pygame.K_ESCAPE:	# close menu
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
		self.parent.interface.generateMap()	# must generate and show clean map before showing battle
		self.parent.interface.drawMap()
		pygame.display.update()
		self.parent.interface.handleBattle(self.attackingSquare, self.parent.interface.currentSquare(), self.attackingSquare.unit.weapons[result])


	def draw(self):
		self.menuBorder = pygame.draw.rect(self.parent.display, colors.almostBlack, (self.location[0] - 2, self.location[1] - 2, 336, 110))	# menu border
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
		self.buttonAttack =		[pygame.image.load('gfx/menuIcons/attack1.png'), 		pygame.image.load('gfx/menuIcons/attack2.png'),		None, 0]
		self.buttonMove =		[pygame.image.load('gfx/menuIcons/move1.png'), 			pygame.image.load('gfx/menuIcons/move2.png'),		None, 1]
		self.buttonContain =	[pygame.image.load('gfx/menuIcons/containing1.png'),	pygame.image.load('gfx/menuIcons/containing2.png'),	None, 2]
		self.buttonExit =		[pygame.image.load('gfx/menuIcons/exit1.png'), 			pygame.image.load('gfx/menuIcons/exit2.png'),		None, 3]



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
		if _focusedUnit.weapons != [None, None, None, None]:		# DEV: should also check if any ammo in each. Eclude weapons without ammo from list here
			if self.parent.interface.markAttackableSquares(True):
				self.contents.append(self.buttonAttack)
		if _focusedUnit.storageMax:
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
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.endMenu(self.focused.get())
			# Keyboard
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:	# close menu
					self.parent.holdEscape = True
					self.parent.mode = "normal"
					self.focused.count = 0
					self.focusedArray = [1, 0, 0, 0]
				elif event.key == pygame.K_LEFT:
					self.focused.dec()
					self.focusedArray = [0, 0, 0, 0]
					self.focusedArray[self.focused.get()] = 1
					pygame.mouse.set_pos(self.location[0] + 55 + (self.focused.get() * 62), self.location[1]  + 45)
					pygame.time.wait(50)
				elif event.key == pygame.K_RIGHT:
					self.focused.inc()
					self.focusedArray = [0, 0, 0, 0]
					self.focusedArray[self.focused.get()] = 1
					pygame.mouse.set_pos(self.location[0] + 55 + (self.focused.get() * 62), self.location[1]  + 45)
					pygame.time.wait(50)
				elif event.key == pygame.K_RETURN:
					self.endMenu(self.focused.get())





	def endMenu(self, result):
		""" execute action selected in the action menu """
		_butID = self.contents[result][3]
		if _butID == 0:									# ATTACK
			self.parent.interface.generateMap("attack")
			self.parent.mode = "selectAttack"
			self.parent.interface.fromHex = self.parent.interface.currentSquare()
		elif _butID == 1:								# MOVE
			self.parent.interface.generateMap("move")
			self.parent.mode = "selectMoveTo"
			self.parent.interface.fromHex = self.parent.interface.currentSquare()
		elif _butID == 2:								# CONTENT
			_unit = self.parent.interface.currentSquare().unit
			self.parent.interface.contentMenu.create(_unit)
			self.parent.mode = "showContent"
			print(_unit)




	#		sys.exit('notImplemented Exception: Content')
		elif _butID == 3:								# RETURN
			self.parent.mode = "normal"



	def draw(self):
		self.menuBorder = pygame.draw.rect(self.parent.display, colors.almostBlack, (self.location[0], self.location[1], self.menuWidth, 60), 4)	# menu border
		for butNr in range(len(self.contents)):
			self.parent.display.blit(self.contents[butNr][self.focusedArray[butNr]],  self.contents[butNr][2])




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
		self.cursorFromGfx = pygame.image.load('gfx/cursor_from.png')
		self.cursorAttackGfx = pygame.image.load('gfx/cursor_attacking.png')
		self.hexBorder = pygame.image.load('gfx/hexBorder.png')
		self.skillsMarker = pygame.image.load('gfx/skills_marker.png')
		self.iProgressBar = pygame.image.load('gfx/progressBarI.png')
		self.progressSquare = pygame.image.load('gfx/progress.png')
		self.battleMenu = pygame.image.load('gfx/battleMenu.png')
		self.flags = pygame.image.load('gfx/flags.png')
		self.unitDeath= pygame.image.load('gfx/explosion.png')
		self.unitHurt= pygame.image.load('gfx/skull_blood.png')
		self.ranksGfx = pygame.image.load('gfx/ranksBig.png')
		self.unitPanel = pygame.image.load('gfx/unit_panel.png')
		self.unitSkills = pygame.image.load('gfx/skills.png')
		self.backgroundTexture = pygame.image.load('gfx/steelTexture.png')
		self.backgroundTextureUnit = pygame.image.load('gfx/steelTextureUnit.png')
		self.backgroundTextureTerrain = pygame.image.load('gfx/steelTextureTerrain.png')
		self.semiTransparent = pygame.image.load('gfx/hexTypes/hex_semiTransparent.png')
		self.actionMenu = ActionMenu(self.parent)
		self.weaponMenu = WeaponMenu(self.parent)
		self.contentMenu = ContentMenu(self.parent)
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




	def handleBattle(self, attackFromSquare, attackToSquare, weapon):
		""" Handles and shows the battle between to units """
		# retrieve all data for calculation
		_showBattleLoop = True
		distance = self.calculateDistance(attackFromSquare.position, attackToSquare.position, weapon.rangeMax) - 1
		_enemyWeapons = [x for x in attackToSquare.unit.weapons if x]
		_enemyWeaponsInRange = [x for x in _enemyWeapons if x.rangeMax >= distance]
		_enemyWeaponWithAmmo = [x for x in _enemyWeaponsInRange if x.ammo != 0] if _enemyWeaponsInRange else []
		enemyWeapon = sorted(_enemyWeaponWithAmmo, key=lambda x: x.power, reverse=True)[0] if _enemyWeaponWithAmmo else None
		# Calculate battle
		fBaseAttack = (weapon.power - attackToSquare.unit.armour)
		fDistanceModified = fBaseAttack - (distance * 3)																	# (0 - 6 (theoretically infinitely))
		fTerrainModified = fDistanceModified + ((attackFromSquare.battleModifier - attackToSquare.battleModifier) / 3)		# (0 - 100)
		fExperienceModified = fTerrainModified + ((attackFromSquare.unit.experience - attackToSquare.unit.experience) * 3)	# 
		fSizeModified = fExperienceModified + ((attackFromSquare.unit.currentSize - attackToSquare.unit.currentSize) * 3)	# 
		fRndModified = fSizeModified + random.randint(-5, 5)
		fFinal = int(fRndModified / 10) if fRndModified > 0 else 0
		eBaseAttack = (enemyWeapon.power - attackFromSquare.unit.armour) if enemyWeapon else 0
		eDistanceModified = eBaseAttack - (distance * 3)																	# (0 - 6 (theoretically infinitely))
		eTerrainModified = eDistanceModified + ((attackToSquare.battleModifier - attackFromSquare.battleModifier) / 3)		# (0 - 100)
		eExperienceModified = eTerrainModified + ((attackToSquare.unit.experience - attackFromSquare.unit.experience) * 3)	# 
		eSizeModified = eExperienceModified + ((attackToSquare.unit.currentSize - attackFromSquare.unit.currentSize) * 3)	# 
		eRndModified = eSizeModified + random.randint(-5, 5)
		eFinal = int(eRndModified / 10) if eRndModified > 0 else 0
		# # Show data, for DEV
		# print()
		# print("Non-usable data:")
		# print("   Attack FROM: ", attackFromSquare.position)
		# print("   Attack TO:   ", attackToSquare.position)
		# print("   Attacker: ", str( attackFromSquare.unit.name ))
		# print("   Attacked: ", str( attackToSquare.unit.name ))
		# print("   Weapon:   ", str( weapon.name ))
		# print("Usable data:")
		# print("   Distance: ", str( distance ))
		# print("Friend:")
		# print("   Weapon power: ", str(weapon.power))
		# print("   Armor power:  ", str(attackFromSquare.unit.armour))
		# print("   Experience:   ", str(attackFromSquare.unit.experience))
		# print("   Terrain:      ", str(attackFromSquare.battleModifier))
		# print("   Size:         ", str(attackFromSquare.unit.currentSize))
		# print("Enemy:")
		# print("   Weapon power: ", str(enemyWeapon.power))
		# print("   Armor power:  ", str(attackToSquare.unit.armour))
		# print("   Experience:   ", str(attackToSquare.unit.experience))
		# print("   Terrain:      ", str(attackToSquare.battleModifier))
		# print("   Size:         ", str(attackToSquare.unit.currentSize))
		# print()
		# print("Calculation (Friend): ")
		# print("   Base:         ", fBaseAttack)
		# print("   Distance:     ", fDistanceModified)
		# print("   Terrain:      ", fTerrainModified)
		# print("   Experience:   ", fExperienceModified)
		# print("   Size:         ", fSizeModified)
		# print("   Random:       ", fRndModified)
		# print("   Kills:        ", fFinal)
		# print("Calculation (Enemy): ")
		# print("   Base:         ", eBaseAttack)
		# print("   Distance:     ", eDistanceModified)
		# print("   Terrain:      ", eTerrainModified)
		# print("   Experience:   ", eExperienceModified)
		# print("   Size:         ", eSizeModified)
		# print("   Random:       ", eRndModified)
		# print("   Kills:        ", eFinal)
		# show battle : make calculations needed inside loop		
		fromSize = font40.render(str(attackFromSquare.unit.currentSize), True, (208, 185, 140));
		toSize = font40.render(str(attackToSquare.unit.currentSize), True, (208, 185, 140));
		subFromWeapon = weapon.picture.subsurface((42, 0, 248, 49))
		subToWeapon = enemyWeapon.picture.subsurface((42, 0, 248, 49)) if enemyWeapon else pygame.Surface((290, 49), pygame.SRCALPHA, 32)
		fromWeapon = pygame.transform.scale(subFromWeapon, (146, 30))
		toWeapon = pygame.transform.scale(subToWeapon, (146, 30))
		_leftBarWidth = (40 + (fFinal - eFinal)) * 10
		_rightBarWidth = 810 - _leftBarWidth
		_deaths = [False, False]						# raise flag if any of the units die
		# create loop to show battle
		for frame in range(300):
			if frame < 100:
				barFrame = frame
			elif frame == 100:
				barFrame = 100
				# update game data when bars are fully drawn
				attackToSquare.unit.currentSize -= fFinal
				if fFinal > 0 and attackFromSquare.unit.experience < 10:	# if attacked was hit
					attackFromSquare.unit.experience += 1
				if attackToSquare.unit.currentSize < 1:						# if attacked was killed
					attackToSquare.unit.currentSize = 0
					if attackFromSquare.unit.experience < 10:
						attackFromSquare.unit.experience += 1
					_deaths[0] = True																				# SHOW DEATH!!!!!
				attackFromSquare.unit.currentSize -= eFinal
				if eFinal > 0 and attackToSquare.unit.experience < 10:		# if attacker was hit
					attackToSquare.unit.experience += 1
				if attackFromSquare.unit.currentSize < 1:					# if attacker was killed
					attackFromSquare.unit.currentSize = 0
					if attackToSquare.unit.experience < 10:
						attackToSquare.unit.experience += 1
					_deaths[1] = True	
				fromSize = font40.render(str(attackFromSquare.unit.currentSize), True, (208, 185, 140));
				toSize = font40.render(str(attackToSquare.unit.currentSize), True, (208, 185, 140));
			else:
				barFrame = 100
			battleMenu = self.battleMenu.copy()
			battleMenu.blit(self.flags, [286, 48], (0, 0, 88, 88))	# flags
			battleMenu.blit(self.flags, [466, 48], (88, 0, 88, 88))
			battleMenu.blit(attackFromSquare.unit.mapIcon, [282, 44])	# units
			battleMenu.blit(attackToSquare.unit.mapIcon, [462, 44])
			battleMenu.blit(self.ranksGfx, [20, 48], (attackFromSquare.unit.experience * 88, 0, 88, 88))	# exp
			battleMenu.blit(self.ranksGfx, [732, 48], (attackToSquare.unit.experience * 88, 0, 88, 88))
			battleMenu.blit(fromSize, [197 - (fromSize.get_width() / 2), 53])	# size
			battleMenu.blit(toSize, [643 - (toSize.get_width() / 2), 53])
			battleMenu.blit(fromWeapon, [124, 106])	# weapons
			battleMenu.blit(toWeapon, [570, 106])
			# Progress bars. Base length of each bar is 380, (+/- battle outcome * 10)
			_progressbarLeft = pygame.Surface(((_leftBarWidth / 100) * barFrame, 14))
			_progressbarRight = pygame.Surface(((_rightBarWidth / 100) * barFrame, 14))
			_progressbarLeft.fill(colors.green)
			_progressbarRight.fill(colors.red)
			battleMenu.blit(_progressbarLeft, [20, 14])
			battleMenu.blit(_progressbarRight, [820 - (_rightBarWidth / 100) * barFrame, 14])
			self.parent.display.blit(battleMenu, [144, 800])			# menu background
			pygame.display.update()
			time.sleep(0.005)
		self.drawMap()
		pygame.display.update()
		tCoords = attackToSquare.getPixelCooords()
		fCoords = attackFromSquare.getPixelCooords()
		# show players hurt
		if fFinal:
			self.parent.display.blit(self.unitHurt, [tCoords[0] + 24, tCoords[1] + 12], (fFinal * 72, 0, 72, 72))
			pygame.display.update()
			time.sleep(1)		
		if eFinal:
			self.parent.display.blit(self.unitHurt, [fCoords[0] + 24, fCoords[1] + 12], (eFinal * 72, 0, 72, 72))
			pygame.display.update()
			time.sleep(1)
		self.generateMap()
		self.drawMap()
		pygame.display.update()
		# handle any player death
		if _deaths[0]:
			for d in range(9):
				self.parent.display.blit(self.unitDeath, [tCoords[0] + 12, tCoords[1] + 4], (d * 96, 0, 96, 96))
				pygame.display.update()
				time.sleep(0.1)
			attackToSquare.unit = None
			self.generateMap()
			self.drawMap()
			pygame.display.update()
		if _deaths[1]:
			for d in range(9):
				self.parent.display.blit(self.unitDeath, [fCoords[0] + 12, fCoords[1] + 4], (d * 96, 0, 96, 96))
				pygame.display.update()
				time.sleep(0.1)
			attackFromSquare.unit = None
			self.generateMap()
			self.drawMap()
			pygame.display.update()
		return True



	def markMovableSquares(self):
		""" prints an overlay on each hexSquare on the map that the current unit cannot move to.
			Must be called each time player selects move """
		unitSpeed = self.currentSquare().unit.speed
		self.movingFrom = self.currentSquare()
		x, y = self.movingFrom.position
		withinRange = [(x,y)]	# coord of self
		for iteration in range(unitSpeed):
			for coord in set(withinRange):
				neighbors = adjacentHexes(*coord, self.mapWidth, self.mapHeight)
				withinRange += neighbors
		movableSquares = list(set(withinRange))
		movableSquares.remove(self.movingFrom.position)
		obstructed = []
		for x, y in movableSquares:
			if self.mainMap[x][y].fogofwar != 0:
				obstructed.append((x,y))
			elif self.mainMap[x][y].unit:
				if self.mainMap[x][y].unit.storageMax == 0:		# do not remove units that has storage
					obstructed.append((x,y))
				elif self.currentSquare().unit.weight + self.mainMap[x][y].unit.storageActual > self.mainMap[x][y].unit.storageMax:			# if not enough room 
					obstructed.append((x,y))
			elif self.mainMap[x][y].movementModifier == None:
				if type(self.mainMap[x][y].content) != list:			# if hex has a storage
					obstructed.append((x,y))
		# remove obstacaled squares
		for pos in obstructed:
			movableSquares.remove(pos)
		# mark squares not possible to target 
		for x in range(self.mapHeight):
			for y in range(len(self.mainMap[x])):
				if self.mainMap[x][y].fogofwar == 0 and (x,y) not in movableSquares:
					self.mainMap[x][y].fogofwar = 3



	def markAttackableSquares(self, check = False):
		""" prints an overlay on each hexSquare on the map that the current unit cannot attack.
			Must be called each time player selects attack
			If check is True, returns True or False, indicating whether any units are in range """
		attackingFrom = self.currentSquare()
		x, y = attackingFrom.position
		withinRange = [(x,y)]	# coord of self
		_allMin = []
		_allMax = []
		for c in attackingFrom.unit.weapons:
			if c:
				_allMin.append(c.rangeMin)
				_allMax.append(c.rangeMax)
		rangeMin = min(_allMin)
		rangeMax = max(_allMax)
		for iteration in range(rangeMax):
			for coord in set(withinRange):
				neighbors = adjacentHexes(*coord, self.mapWidth, self.mapHeight)
				withinRange += neighbors
		attackableSquares = list(set(withinRange))
		attackableSquares.remove(attackingFrom.position)
		if rangeMin > 1:
			belowMinRange = [(x,y)]
			for iteration in range(rangeMin - 1):
				for coord in set(belowMinRange):
					neighbors = adjacentHexes(*coord, self.mapWidth, self.mapHeight)
					belowMinRange += neighbors
			# remove any field below min range
			for coord in belowMinRange:
				if coord in attackableSquares:
					attackableSquares.remove(coord)
		attackableEnemySquares = []
		for x, y in attackableSquares:
			if self.mainMap[x][y].fogofwar == 0:
				if self.mainMap[x][y].unit:
					if self.mainMap[x][y].unit.faction != self.parent.playerSide:
						attackableEnemySquares.append((x,y))
		if check:
			return bool(attackableEnemySquares)
		else:
			# mark squares possible to attack 
			for x in range(self.mapHeight):
				for y in range(len(self.mainMap[x])):
					if self.mainMap[x][y].fogofwar == 0 and (x,y) not in attackableEnemySquares:
						self.mainMap[x][y].fogofwar = 3



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


	def getSquare(self, coord):
		""" returns the hexSquare with the given coordinates"""
		return self.mainMap[coord[0]][coord[1]]


	def currentSquare(self, coords = False):
		""" returns the currently hightlighted hexSquare """
		mapCursor = [self.cursorPos[0] + self.mapView[0], self.cursorPos[1]  + self.mapView[1]]
		# prevent cursor exiting map
		if mapCursor[0] < 0: mapCursor[0] = 0
		if mapCursor[0] > 7: mapCursor[0] = 7
		if mapCursor[1] < 0: mapCursor[1] = 0
		if mapCursor[1] > 22: mapCursor[1] = 21
		# return result
		if coords:
			# get the pixel coordinates from the hex coordinates
			forskydning = 71 if (self.cursorPos[1] % 2) != 0 else 0
			pixelCooords = [self.cursorPos[0] * 142 + forskydning + 7, self.cursorPos[1] * 40 + 9]
			return pixelCooords
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
		if self.parent.mode == "actionMenu":
			self.actionMenu.draw()
		elif self.parent.mode == "weaponMenu":
			self.weaponMenu.draw()
		elif self.parent.mode == "showContent":
			self.contentMenu.draw()




	def generateMap(self, action = None):
		""" generate the basic map to be used to draw main map and minimap """	
		self.calculateFOW()
		if action == 'move':
			self.markMovableSquares()
		elif action == 'attack':
			self.markAttackableSquares()
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
				if self.parent.cmdArgs.hexnumbers:	# put as number on square
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
		self.rectMap = pygame.draw.rect(self.parent.display, colors.almostBlack, (15, 15, 1098, 968), 4)								# map border (main map = 1098 / 968)
		self.parent.display.blit(self.map, [19, 19], (self.mapView[0], self.mapView[1] * 40, 1098 + self.mapView[0], 960))		# blit visible area of map
		forskydning = 71 if (self.cursorPos[1] % 2) != 0 else 0
		if self.parent.mode == "selectMoveTo":
			forskydning2 = 71 if (self.fromHex.position[0] % 2) != 0 else 0
			self.parent.display.blit(self.cursorFromGfx, [self.fromHex.position[1] * 142 + forskydning2 + 7, self.fromHex.position[0] * 40 + 9])
		elif self.parent.mode == "selectAttack":
			forskydning2 = 71 if (self.fromHex.position[0] % 2) != 0 else 0
			self.parent.display.blit(self.cursorAttackGfx, [self.fromHex.position[1] * 142 + forskydning2 + 7, self.fromHex.position[0] * 40 + 9])
		self.parent.display.blit(self.cursorGfx, [self.cursorPos[0] * 142 + forskydning + 7, self.cursorPos[1] * 40 + 9])
		return 1



	def drawMiniMap(self):
		pygame.draw.rect(self.parent.display, colors.darkGrey , (1124, 15,  662, 400), 0)			# minimap area background
		pygame.draw.rect(self.parent.display, colors.almostBlack, (1124, 15,  662, 400), 4)					# minimap area border
		miniMapXCoord =	1459 - int(self.miniMap.get_width() / 2)
		w, h = self.miniMap.get_size()
		self.parent.display.blit(self.miniMap, [miniMapXCoord, 19])
		self.rectMini = pygame.draw.rect(self.parent.display, colors.almostBlack, (miniMapXCoord - 4, 15,  w + 8, h + 8), 4)					# minimap border
		# calculate percentage of area displayed
		widthPercentageDisplayed = 8 / self.mapWidth
		heightPercentageDisplayed = 12 / int((self.mapHeight + 1) / 2)
		# draw a rectangle to show the field of view on the miniMap
		markerOffsetX = self.mapView[0] / self.mapWidth				# calculate marker offset
		markerOffsetY = self.mapView[1] / self.mapHeight
		pygame.draw.rect(self.parent.display, colors.red, (miniMapXCoord -2 + int(w * markerOffsetX), 17 + int(h * markerOffsetY), int((w + 4) * widthPercentageDisplayed), int((h) * heightPercentageDisplayed)), 2)



	def drawTerrainGUI(self):
		""" fetches cursor position and fills out info on unit and terrain """
		TerrainGUI = pygame.Surface((662, 118))
		TerrainGUI.blit(self.backgroundTextureTerrain, (4, 4))
		pygame.draw.rect(TerrainGUI, colors.almostBlack, (0, 0, 662, 118), 4)		# window border
		square = self.currentSquare()
		if not square.fogofwar:
			TerrainGUI.blit(self.movementModifierText, (176, 20))
			TerrainGUI.blit(self.battleModifierText, (176, 50))
			TerrainGUI.blit(self.sightModifierText, (176, 80))
			TerrainGUI.blit(square.background, [49, 19])
			if square.infra:	TerrainGUI.blit(square.infra, [49, 19])
			TerrainGUI.blit(self.hexBorder, [47, 17])
			if square.movementModifier != None:
				for x in range(square.movementModifier):
					TerrainGUI.blit(self.progressSquare, (392 + (x * 20), 18))
			else:
				TerrainGUI.blit(self.iProgressBar, [392, 18])
			if square.battleModifier != None:
				for x in range(int(square.battleModifier / 10)):
					TerrainGUI.blit(self.progressSquare, (392 + (x * 20), 48))
			else:
				TerrainGUI.blit(self.iProgressBar, [392, 48])
			for x in range(square.sightModifier):
				TerrainGUI.blit(self.progressSquare, (392 + (x * 20), 78))
		self.parent.display.blit(TerrainGUI, [1124, 421])
		return 1



	def drawUnitGUI(self):
		unitGUI = pygame.Surface((662, 438))
		unitGUI.blit(self.backgroundTextureUnit, (4, 4))
		pygame.draw.rect(unitGUI, colors.almostBlack, (0, 0, 662, 438), 4)						# window border
		square = self.currentSquare()
		if not square.fogofwar and square.unit:
			unitPanel = self.unitPanel.copy()
			unitPanel.blit(self.flags, [3, 3], (self.flagIndex[square.unit.country] * 88, 0, 88, 88))
			unitPanel.blit(square.unit.mapIcon, [-1, -1])
			unitPanel.blit(self.ranksGfx, [4, 103], (square.unit.experience * 88, 0, 88, 88))
			unitPanel.blit(square.unit.picture, [380, 3])
			gfx = font20.render(square.unit.name, True, (208, 185, 140)); 				unitPanel.blit(gfx, [236 - (gfx.get_width() / 2), 9])
			gfx = font20.render(square.unit.faction, True, (208, 185, 140)); 			unitPanel.blit(gfx, [236 - (gfx.get_width() / 2), 50])
			gfx = font20.render(str(square.unit.sight), True, (208, 185, 140)); 		unitPanel.blit(gfx, [175 - (gfx.get_width() / 2), 105])
			gfx = font20.render(str(square.unit.speed), True, (208, 185, 140)); 		unitPanel.blit(gfx, [249 - (gfx.get_width() / 2), 105])
			gfx = font20.render(str(square.unit.currentSize), True, (208, 185, 140)); 	unitPanel.blit(gfx, [323 - (gfx.get_width() / 2), 105])
			gfx = font20.render(str(square.unit.armour), True, (208, 185, 140)); 		unitPanel.blit(gfx, [175 - (gfx.get_width() / 2), 155])
			gfx = font20.render(str(square.unit.weight), True, (208, 185, 140)); 		unitPanel.blit(gfx, [249 - (gfx.get_width() / 2), 155])
			gfx = font20.render(str(square.unit.fuel), True, (208, 185, 140)); 			unitPanel.blit(gfx, [323 - (gfx.get_width() / 2), 155])
			# mark active skills
			unitGUI.blit(self.unitSkills, [618, 11])
			for x in square.unit.skills:
				unitGUI.blit(self.skillsMarker, [616, (x * 28) - 19])
			# weapons
			pygame.draw.rect(unitGUI, colors.almostBlack, (0, 218, 662, 58), 4)							# weapons borders 1
			pygame.draw.rect(unitGUI, colors.almostBlack, (0, 326, 662, 58), 4)							# weapons borders 2
			unitGUI.blit(square.unit.weaponsGfx[0], [4, 222])
			unitGUI.blit(square.unit.weaponsGfx[1], [4, 276])
			unitGUI.blit(square.unit.weaponsGfx[2], [4, 330])
			unitGUI.blit(square.unit.weaponsGfx[3], [4, 384])
			unitGUI.blit(unitPanel, [10, 10])
		self.parent.display.blit(unitGUI, [1124, 545])
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




	def calculateDistance(self, _from, _to, _range):
		""" calculates the distance from one hex to another """
		paths = [[_from]]					# adding first step to matrix of all possible paths
		visited = [_from] 			# all fields prev visted
		validPaths = []
		for x in range(_range):					# calculate 1 iteration per range
			paths.sort(key=len)
			newPaths = []
			for p in reversed(paths):
				lastField = p[-1]
				neighbors = adjacentHexes(*lastField, self.mapWidth, self.mapHeight)
				for n in reversed(neighbors):
					square = self.getSquare(n)
					if n in visited:				# We don't want paths to visit previously visited fields
						neighbors.remove(n)
				for n in neighbors:
					new = copy.copy(p)
					new.append(n)
					newPaths.append(new)
					visited.append(n)
				paths.remove(p)			# remove currently processed path, as it is obsolete
				for np in newPaths:				# searching for a match with target field
					if np[-1] == _to and np not in validPaths:
						validPaths.append(np)
			paths += newPaths
			paths.sort(key=len)
		validPaths.sort(key=len)
		return len(validPaths[0]) - 1



	def findPath(self, _moveFrom, _moveTo):
		""" calculates the path that a unit must take to get from one filed to the next """
#		print("Unit must move from (%s) to (%s) :" % (_moveFrom, _moveTo))
		paths = [[_moveFrom]]					# adding first step to matrix of all possible paths
		visited = [_moveFrom] 			# all fields prev visted
		while True:					# calculate paths until path is found
			paths.sort(key=len)
			newPaths = []
			for p in reversed(paths):
				lastField = p[-1]
				neighbors = adjacentHexes(*lastField, self.mapWidth, self.mapHeight)
				for n in reversed(neighbors):
					square = self.getSquare(n)
					if square.unit:
						if square.unit.faction != "Central Powers":		# if they are not ours
							neighbors.remove(n)
					elif square.fogofwar:			# if field not clear
						neighbors.remove(n)
					if n in visited and n in neighbors:				# We don't want paths to visit previously visited fields
						neighbors.remove(n)
				for n in neighbors:
					new = copy.copy(p)
					new.append(n)
					newPaths.append(new)
					visited.append(n)
				paths.remove(p)			# remove currently processed path, as it is obsolete
				for np in newPaths:				# searching for a match with target field
					if np[-1] == _moveTo:
#						print("Calculated path is", np)
						return np
			paths += newPaths
			paths.sort(key=len)



	def executeMove(self, movePath):
		""" Shows the movement of a unit along the path given by the points in the path, then updates map data """
		self.parent.mode = "normal"
		xFrom, yFrom = movePath[0]
		_fromCoord = movePath[0]
		xTo, yTo = movePath[-1]
		fromHex = self.mainMap[xFrom][yFrom]
		toHex = self.mainMap[xTo][yTo]
		# remove unit from matrix and save it, display map without unit
		_unitMoved = fromHex.unit
		fromHex.unit = None
		self.generateMap()
		for coord in movePath:
			x, y = coord
			forskydning = 71 if (x % 2) != 0 else 0
			pixelCoordXto = x * 40 + 10
			pixelCoordYto = y * 142 + forskydning + 19
			if coord != _fromCoord:
#				print("Moving pixel coordinates: (%s, %s) ---> (%s, %s)" % (pixelCoordXfrom, pixelCoordYfrom, pixelCoordXto, pixelCoordYto))
				# calculate rotation
				if pixelCoordYfrom > pixelCoordYto:
					if pixelCoordXfrom < pixelCoordXto:
						rotation = 2	# left down
					else:
						rotation = 1	# left up
				elif pixelCoordYfrom < pixelCoordYto:
					if pixelCoordXfrom < pixelCoordXto:
						rotation = 4	# right down
					else:
						rotation = 5	# right up
				else:
					if pixelCoordXfrom < pixelCoordXto:
						rotation = 3	# down
					else:
						rotation = 0	# up
				_unitMoved.mapIcon = _unitMoved.allIcons[rotation]
				frameCoord = [pixelCoordYfrom, pixelCoordXfrom]
				for x in range(8):
					# show frame
					self.drawMap()
					self.parent.display.blit(_unitMoved.allIcons[rotation], [frameCoord[0], frameCoord[1]])		# must blit unit.allIcons[0-5]
					pygame.display.update()
					pygame.time.wait(20)
					# use rotation to calculatenext frame
					if rotation == 0:			# up
						frameCoord[1] -= 10
					elif rotation == 1:			# left up
						frameCoord[0] = int(frameCoord[0] - 8.875)
						frameCoord[1] -= 5
					elif rotation == 2:			# left down
						frameCoord[0] = int(frameCoord[0] - 8.875)
						frameCoord[1] += 5
					elif rotation == 3:			# down
						frameCoord[1] += 10
					elif rotation == 4:			# right down
						frameCoord[0] = int(frameCoord[0] + 8.875)
						frameCoord[1] += 5
					elif rotation == 5:			# right up
						frameCoord[0] = int(frameCoord[0] + 8.875)
						frameCoord[1] -= 5
			pixelCoordXfrom = pixelCoordXto
			pixelCoordYfrom = pixelCoordYto
		# check if target has content
		if toHex.content != False:
			toHex.content.append(_unitMoved)
			toHex.storageActual += _unitMoved.weight


			print("HEX", toHex.content, toHex.storageActual)
#			print(dir(toHex))
#			print(toHex.storageMax)


		elif toHex.unit and _unitMoved.weight + toHex.unit.storageActual <= toHex.unit.storageMax:			# if enough room 
			toHex.unit.content.append(_unitMoved)
			toHex.unit.storageActual += _unitMoved.weight


			print(toHex.unit.content, toHex.unit.storageActual)




		else:
			toHex.unit = _unitMoved
		# generate and display new map with unit
		self.generateMap()
		self.drawMap()
		pygame.display.update()
		return 1


