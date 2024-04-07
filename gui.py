import sys
import json
import time
import copy
import math
import pygame
import random
import pygame.surfarray as surfarray
from hlrData import *

# --- Classes -------------------------------------------------------------------------------------

class GUI():
	""" Representation of the background """

	def __init__(self, parent):
		self.parent = parent
		# load constants
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
		self.mainMap = []
		self.fromContent = False 	# flag, shows moveUnit to not move the unit of current hex
		# gfxTexts
		self.movementModifierText = font20.render('Movement Penalty', True, colors.black) 	# [movementModifierText, rMovementModifierText]
		self.battleModifierText = font20.render('Battle Advantage', True, colors.black)		#[battleModifierText, rBattleModifierText]
		self.sightModifierText = font20.render('Sight Hindrance', True, colors.black)				# [sightModifierText, rSightModifierText]
		# load map data
		with open(parent.cmdArgs.mapPath) as json_file:
			jsonLevelData = json.load(json_file)
		self.parent.info = Info(jsonLevelData["mapName"], jsonLevelData["mapNo"], jsonLevelData["player"], jsonLevelData["tiles"])
		for nrX, value in enumerate(jsonLevelData['tiles'].values()):
			line = []
			for nrY, square in enumerate(value):
				line.append(HexSquare((nrX, nrY), *square))
			self.mainMap.append(line)
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
		if self.fromContent:
			movingUnit = self.parent.interface.contentMenu.content.units[self.fromContent[0]][self.fromContent[1]]
		else:
			movingUnit = self.currentSquare().unit
		self.movingFrom = self.currentSquare()
		xFrom, yFrom = self.movingFrom.position
		withinRange = [(xFrom, yFrom)]	# coord of self
		for iteration in range(movingUnit.speed):
			for coord in set(withinRange):
				neighbors = adjacentHexes(*coord, self.parent.info.mapWidth, self.parent.info.mapHeight)
				withinRange += neighbors
		movableSquares = list(set(withinRange))
		movableSquares.remove(self.movingFrom.position)
		obstructed = []
		for x, y in movableSquares:
			if self.mainMap[x][y].fogofwar != 0 and self.mainMap[x][y].fogofwar != 2:
				obstructed.append((x,y))
			elif self.mainMap[x][y].unit:
				if movingUnit.faction != self.parent.info.player:
					obstructed.append((x,y))		# remove if opposing units
				else:
					if self.mainMap[x][y].unit.content:		# if unit has storage, check if enough room
						if movingUnit.weight + self.mainMap[x][y].unit.content.storageActual() > self.mainMap[x][y].unit.content.storageMax: 
							obstructed.append((x,y))
						elif self.mainMap[x][y].unit.faction != self.parent.info.player:	# If not our unit
							obstructed.append((x,y))
					else:
						obstructed.append((x,y))
			# handle depot access
			if self.mainMap[x][y].movementModifier == None:
				if self.mainMap[x][y].content == False:			# if hex does not have a storage
					obstructed.append((x,y))
				elif self.mainMap[x][y].owner != 0 and self.mainMap[x][y].owner != self.parent.info.player:		# if hex does have a storage, is it the enemys
					if not 1 in movingUnit.skills:	# mark hex only if moving unit can capture
						obstructed.append((x,y))
		# remove obstacaled squares
		for pos in obstructed:
			if pos in movableSquares:
				movableSquares.remove(pos)
		# mark squares not possible to target 
		for x in range(self.parent.info.mapHeight):
			for y in range(len(self.mainMap[x])):
				if self.mainMap[x][y].fogofwar != 1 and (x,y) not in movableSquares:
					self.mainMap[x][y].fogofwar = 3
		# mark inacessible and too far paths
		for square in movableSquares:
			result = self.findPath((xFrom, yFrom), square)
			if not result:
				self.mainMap[square[0]][square[1]].fogofwar = 3
			elif len(result) - 1 > movingUnit.speed :
				self.mainMap[square[0]][square[1]].fogofwar = 3



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
				neighbors = adjacentHexes(*coord, self.parent.info.mapWidth, self.parent.info.mapHeight)
				withinRange += neighbors
		attackableSquares = list(set(withinRange))
		attackableSquares.remove(attackingFrom.position)
		if rangeMin > 1:
			belowMinRange = [(x,y)]
			for iteration in range(rangeMin - 1):
				for coord in set(belowMinRange):
					neighbors = adjacentHexes(*coord, self.parent.info.mapWidth, self.parent.info.mapHeight)
					belowMinRange += neighbors
			# remove any field below min range
			for coord in belowMinRange:
				if coord in attackableSquares:
					attackableSquares.remove(coord)
		attackableEnemySquares = []
		for x, y in attackableSquares:
			if self.mainMap[x][y].fogofwar == 0:
				if self.mainMap[x][y].unit:
					if self.mainMap[x][y].unit.faction != self.parent.info.player:
						attackableEnemySquares.append((x,y))
		if check:
			return bool(attackableEnemySquares)
		else:
			# mark squares possible to attack 
			for x in range(self.parent.info.mapHeight):
				for y in range(len(self.mainMap[x])):
					if self.mainMap[x][y].fogofwar == 0 and (x,y) not in attackableEnemySquares:
						self.mainMap[x][y].fogofwar = 3



	def calculateFOW(self):
		""" checks each hexSquare on the map and marks it as visible if it can be seen by any friendly unit 
			must be called each time player moves a piece"""
		depotSquares = []
		for x in range(self.parent.info.mapHeight):
			for y in range(len(self.mainMap[x])):
				self.mainMap[x][y].fogofwar = 2 if self.mainMap[x][y].seen else 1
		for x in range(self.parent.info.mapHeight):
			for y in range(len(self.mainMap[x])):
				if self.mainMap[x][y].unit:
					if self.mainMap[x][y].unit.faction == self.parent.info.player:			# only mark visible if it is our own unit
						withinSight = [(x,y)]	# coord of self
						for iteration in range(self.mainMap[x][y].unit.sight):
							for coord in set(withinSight):
								neighbors = adjacentHexes(*coord, self.parent.info.mapWidth, self.parent.info.mapHeight)
								withinSight += neighbors
						for c in set(withinSight):
							try:
								self.mainMap[c[0]][c[1]].fogofwar = 0
								self.mainMap[c[0]][c[1]].seen = True
							except:
								print("Coordinate exceed map size in calculateFOW():", c)
				if hasattr(self.mainMap[x][y], 'owner') and self.mainMap[x][y].owner == self.parent.info.player:
					depotSquares.append((x, y))
					neighbors = adjacentHexes(x, y, self.parent.info.mapWidth, self.parent.info.mapHeight)
					for n in neighbors:
						depotSquares.append(n)
		# mark all squares around depots/HQ as visible
		for x, y in depotSquares:
			self.mainMap[x][y].fogofwar = 0
		# --- FOR TEST --- Reveal whole map ------------------------------------------------
		if self.parent.cmdArgs.reveal:
			for x in range(self.parent.info.mapHeight):
				for y in range(len(self.mainMap[x])):
					self.mainMap[x][y].fogofwar = 0
		# --- FOR TEST --- Reveal whole map ------------------------------------------------



	def getSquare(self, coord):
		""" returns the hexSquare with the given coordinates"""
		return self.mainMap[coord[0]][coord[1]]



	def currentSquare(self, coords = False):
		""" returns the currently hightlighted hexSquare ABSOLUTE, i.e. the HEX sqare number on map, not on screen """
		mapCursor = [self.cursorPos[0] + self.mapView[0], self.cursorPos[1]  + self.mapView[1]]
		if coords:
			# get the pixel coordinates from the hex coordinates
			forskydning = 71 if (self.cursorPos[1] % 2) != 0 else 0
			pixelCooords = [self.cursorPos[0] * 142 + forskydning + 7, self.cursorPos[1] * 40 + 9]
			return pixelCooords
		else:
			try:
				return self.mainMap[mapCursor[1]][mapCursor[0]]
			except:				# to avoid extremely rare exception where coord of odd line is +1
				return False


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
			self.contentMenu.reset()
			self.contentMenu.draw()




	def generateMap(self, action = None):
		""" generate the basic map to be used to draw main map and minimap """	
		self.calculateFOW()
		if action == 'move':
			self.markMovableSquares()
		elif action == 'attack':
			self.markAttackableSquares()
		width = (self.parent.info.mapWidth * 142) - 46  # dunno why 46 must be subtracted?
		height = (self.parent.info.mapHeight + 1) * 40
		self.map = pygame.Surface((width, height))
		self.map.fill(colors.historylineDark)
		for x in range(self.parent.info.mapHeight):
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
		width = (self.parent.info.mapWidth * 142) - 46			# dunno why 46 must be subtracted?
		height = (self.parent.info.mapHeight + 1) * 40
		tempMiniMap = self.map.copy()
		# scale minimap to max height of minimap area (392)
		scaleFactor = 392 / height
		self.miniMap = pygame.transform.scale(tempMiniMap, (width * scaleFactor, height * scaleFactor))
#		pygame.image.save(self.map, 'generatedMap.png')



	def drawMap(self):
		self.rectMap = pygame.draw.rect(self.parent.display, colors.almostBlack, (15, 15, 1098, 968), 4)							# map border (main map = 1098 / 968)
		self.parent.display.blit(self.map, [19, 19], (	self.mapView[0] * 142, self.mapView[1] * 40, 1090, 960))							# blit visible area of map
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
		widthPercentageDisplayed = 8 / self.parent.info.mapWidth
		heightPercentageDisplayed = 12 / int((self.parent.info.mapHeight + 1) / 2)
		# draw a rectangle to show the field of view on the miniMap
		markerOffsetX = self.mapView[0] / self.parent.info.mapWidth				# calculate marker offset
		markerOffsetY = self.mapView[1] / self.parent.info.mapHeight
		pygame.draw.rect(self.parent.display, colors.red, (miniMapXCoord -2 + int(w * markerOffsetX), 17 + int(h * markerOffsetY), int((w + 4) * widthPercentageDisplayed), int((h) * heightPercentageDisplayed)), 2)



	def drawTerrainGUI(self):
		""" fetches cursor position and fills out info on unit and terrain """
		TerrainGUI = pygame.Surface((662, 118))
		TerrainGUI.blit(self.backgroundTextureTerrain, (4, 4))
		pygame.draw.rect(TerrainGUI, colors.almostBlack, (0, 0, 662, 118), 4)		# window border
		square = self.currentSquare()
		if square and not square.fogofwar:
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
		if square and not square.fogofwar and square.unit:
			unitPanel = self.unitPanel.copy()
			unitPanel.blit(self.flags, [3, 3], (flagIndex[square.unit.country] * 88, 0, 88, 88))
			unitPanel.blit(square.unit.mapIcon, [-1, -1])
			unitPanel.blit(self.ranksGfx, [4, 103], (square.unit.experience * 88, 0, 88, 88))
			unitPanel.blit(square.unit.picture, [380, 3])
			gfx = font20.render(square.unit.name, True, (208, 185, 140)); 				unitPanel.blit(gfx, [236 - (gfx.get_width() / 2), 9])
			gfx = font20.render(self.parent.info.nameDict[square.unit.faction], True, (208, 185, 140)); 			unitPanel.blit(gfx, [236 - (gfx.get_width() / 2), 50])
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



	def cursorMove(self, direction):
		""" Values are left, right, up, down """
		verticalOdd = self.cursorPos[1] % 2 == 0
		if direction == 'Up':
			if self.cursorPos[1] > 2:
				self.cursorPos[1] -= 2
			elif self.mapView[1] >= 2:
				self.mapView[1] -= 2		# NB : ONLY even numbers, as two lines must be drawn as one!
			elif self.cursorPos[1] == 2:
				self.cursorPos[1] -= 2
		elif direction == 'Down':
			if self.cursorPos[1] < 20:
				self.cursorPos[1] += 2
			elif self.mapView[1] + 24 < self.parent.info.mapHeight:
				self.mapView[1] += 2		# NB : ONLY even numbers, as two lines must be drawn as one!
			elif self.cursorPos[1] == 20:
				self.cursorPos[1] += 2
		elif direction == 'Left':
			if self.cursorPos[0] > 0:
				if verticalOdd:
					self.cursorPos[1] += 1
					self.cursorPos[0] -= 1
				else:
					self.cursorPos[1] -= 1
			elif self.cursorPos[0] == 0:
				if self.mapView[0] > 0:
					self.mapView[0] -= 1
				elif self.mapView[0] == 0:
					if not verticalOdd:
						self.cursorPos[1] -= 1
		elif direction == 'Right':
			if self.cursorPos[0] < 6:
				if verticalOdd:
					self.cursorPos[1] += 1
				else:
					self.cursorPos[0] += 1
					self.cursorPos[1] -= 1
			elif self.cursorPos[0] == 6:
				if self.mapView[0] < self.parent.info.mapWidth - 8:	# 8 is screen width
					self.mapView[0] += 1
				elif self.mapView[0] == self.parent.info.mapWidth - 8:
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
				neighbors = adjacentHexes(*lastField, self.parent.info.mapWidth, self.parent.info.mapHeight)
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
				neighbors = adjacentHexes(*lastField, self.parent.info.mapWidth, self.parent.info.mapHeight)
				for n in reversed(neighbors):
					square = self.getSquare(n)
					if square.unit:
						if square.unit.faction != self.parent.info.player:		# if they are not ours
							neighbors.remove(n)
					elif square.fogofwar != 0 and square.fogofwar != 2:			# if field not clear
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
			if not paths:
				return False


	def showCapture(self, player, hexCaptured):
		""" show a short text / animation to inform o depot / HQ capture"""
		_flag = self.flags.subsurface( ((player - 1)  * 88, 0, 88, 88) )
		_bigFlag = pygame.transform.scale(_flag, (400, 300))
		_text = font60.render(hexCaptured.name + " captured!", True, colors.black) 	# [movementModifierText, rMovementModifierText]
		self.parent.display.blit(_bigFlag, [700, 350])
		self.parent.display.blit(_text, [900 - (_text.get_width() / 2), 470])
		pygame.display.update()
		pygame.time.delay(2000)



	def executeMove(self, movePath):
		""" Shows the movement of a unit along the path given by the points in the path, then updates map data """
		self.parent.mode = "normal"
		xFrom, yFrom = movePath[0]
		_fromCoord = movePath[0]
		xTo, yTo = movePath[-1]
		fromHex = self.mainMap[xFrom][yFrom]
		toHex = self.mainMap[xTo][yTo]
		# remove unit from matrix and save it, display map without unit
		if self.fromContent:
			_unitMoved = self.parent.interface.contentMenu.content.units[self.fromContent[0]][self.fromContent[1]]
			self.parent.interface.contentMenu.content.units[self.fromContent[0]][self.fromContent[1]] = False
			self.fromContent = False
		else:
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
					self.drawMap()														# Below is compensation for map scrolled down! Horizontal is not tested!
					self.parent.display.blit(_unitMoved.allIcons[rotation], [frameCoord[0]  - ( 48 * self.mapView[0] ), frameCoord[1] - ( 40 * self.mapView[1] )])		# must blit unit.allIcons[0-5]
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
		_delivered = False
		if toHex.content and _unitMoved.weight + toHex.content.storageActual() <= toHex.content.storageMax:			# if enough room, depot/HQ entered
			toHex.content.addUnit(_unitMoved)
			# change ownership and flag of Hex
			if toHex.owner != self.parent.info.player:
				toHex.owner = self.parent.info.player
				toHex.updateDepotColours(toHex.owner)
				self.showCapture(self.parent.info.player, toHex)
		elif toHex.unit and _unitMoved.weight + toHex.unit.content.storageActual() <= toHex.unit.content.storageMax:			# if enough room, unit entered
			toHex.unit.content.addUnit(_unitMoved)
		else:
			toHex.unit = _unitMoved
		# generate and display new map with unit
		self.generateMap()
		self.drawMap()
		pygame.display.update()
		return 1


