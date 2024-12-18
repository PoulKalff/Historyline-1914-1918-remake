#!/usr/bin/python3
import warnings
import os
import sys
import pygame
import argparse
import pygame.locals
from os import environ
from gui import GUI
from ArtificialIntelligence import AI
from mapEditor import generateMap, MapEditor
from hlrData import *

# --- Variables / Ressources ----------------------------------------------------------------------

version = '0.80'		# added map-editor
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.simplefilter("ignore")

# --- Classes -------------------------------------------------------------------------------------

class Main():
	""" get data from API and display it """

	def __init__(self, args):
		self.cmdArgs = args
		self.width = 1800	# 1110 minimum, as it is smallest map
		self.height = 1000
		self.playerTurn = 1 	# 1 (human) or 2 (computer). Human player always begins
		if args.mapedit:
			args.editor = MapEditor(self)
		pygame.init()
		icon = pygame.image.load('gfx/gameIcon.png')
		self.devModeFont = pygame.font.Font('freesansbold.ttf', 32)
		pygame.display.set_icon(icon)
		pygame.display.set_caption('Historyline 1914-1918 Remake')
		self.display = pygame.display.set_mode((self.width, self.height))
		self.mouseClick = pygame.time.Clock()
		self.holdEscape = False
		self.round = 1
		self.mode = "normal"		# selection mode: normal, actionMenu, weaponMenu, selectMoveTo, moveTo, selectAttack, attack
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.interface = GUI(self)
		self.computerPlayer = AI(self)
		self.ownUnits = self.getAllUnits(self.info.player)
		self.test = [0, 0]


	def gameOver(self):
		activePlayer = "Human Player" if self.playerTurn == 1 else "Computer Player"
		sys.exit("Game over, winner is " + str(activePlayer))



	def findHex(self, _mX, _mY):
		""" Determine which Hex the mouse is in """
		_mX -= 21
		_mY -= 21
		# calculate where we are in horizontal
		xNoHex = int(_mX / 142)
		yNoHex = int(_mY / 80) * 2
		xInHex = _mX % 142
		yInHex = _mY % 80
		odd = True if yInHex < 40 else False		# Define half hex row, determine if odd or even
		if xInHex < 23:		# Define 4 columns, determine which one
			field = 1
			# determine if we are left or right of diagonal. 
			if odd:
				# manage reverese slope. Reverse diagonal is given by Y = W - (X * (H / W))
				if yInHex < 23 - (xInHex * (40 / 23)):	# 1.7391304347826086
					xHexSelected = xNoHex - 1
					yHexSelected = yNoHex - 1
				else:
					xHexSelected = xNoHex
					yHexSelected = yNoHex
			else:
				yInHex -= 40
				# Manage slope. Diagonal is given by Y = X * (H / W)
				if yInHex < xInHex * (40 / 23):	# 1.7391304347826086
					xHexSelected = xNoHex
					yHexSelected = yNoHex
				else:
					xHexSelected = xNoHex - 1
					yHexSelected = yNoHex + 1
		elif xInHex < 74:
			field = 2
			xHexSelected = xNoHex
			yHexSelected = yNoHex
		elif xInHex < 96:
			field = 3
			xInHex -= 74
			# determine if we are left or right of diagonal. Diagonal is given by Y = X * (H / W)	>
			if odd:
				if yInHex < xInHex * (40 / 23):	# 1.7391304347826086
					xHexSelected = xNoHex
					yHexSelected = yNoHex - 1
				else:
					xHexSelected = xNoHex
					yHexSelected = yNoHex
			else:
				yInHex -= 40
				# manage reverese slope. Reverse diagonal is given by Y = W - (X * (H / W))
				if yInHex < 23 - (xInHex * (40 / 23)):	# 1.7391304347826086
					xHexSelected = xNoHex
					yHexSelected = yNoHex
				else:
					xHexSelected = xNoHex
					yHexSelected = yNoHex + 1
		else:
			field = 4
			xHexSelected = xNoHex
			yHexSelected = yNoHex - 1 if odd else yNoHex + 1
		# identify invalid areas, i.e top, bottom or sides
		if xNoHex == 0 and field == 1:		# if outside hexes on left side
			return False
		if xNoHex == 7 and field == 3:		# if outside hexes on right side
			return False
		if yHexSelected < 0:				# if above hexes
			return False
		if yHexSelected >  22:				# if below hexes
			return False
#		print("   Field %i, %s (%i/%i)" % (field, "Odd" if odd else "Even", yNoHex, xNoHex))	# debug
		return [xHexSelected, yHexSelected]



	def handleSelection(self):
		""" Handles user selection by SPACE or MOUSE """
		cursorHex = self.interface.currentSquare()
		if self.mode == "normal":
			if cursorHex.content:	# if square has content ability
				if cursorHex.owner != self.info.opponent:
					self.interface.contentMenu.create(cursorHex)
					self.mode = "showContent"
			else:
				if cursorHex.unit and cursorHex.unit.faction == self.info.player:
					self.interface.actionMenu.create()
					self.mode = "actionMenu"
		elif self.mode == "selectMoveTo":
			if cursorHex.fogofwar == 0 or cursorHex.fogofwar == 2:				# if field is clear, execute move, else cancel move and return to normal mode	
				moveFrom = self.interface.movingFrom.position
				moveTo = cursorHex.position
				movePath = self.interface.findPath(moveFrom, moveTo)


		#		self.interface.movingFrom.unitToMove = self.interface.movingFrom.unit




				# fromHex = self.interface.movingFrom
				# print()
				# print("fromHex.unit", 		fromHex.unit.name)
				# print("fromHex.unitToMove", fromHex.unitToMove.name)
				# print("fromHex.position", 	fromHex.position)
				# print()
				# print("CHECKITOUT")


				self.interface.executeMove(movePath)
				self.mode = "normal"
			else:
				self.interface.generateMap()
				self.mode = "normal"
		elif self.mode == "selectAttack":
			if cursorHex.fogofwar:				# if field is clear, show menu selection menu, else cancel move and return to normal mode
				self.interface.generateMap()
				self.mode = "normal"
			else:
				self.interface.weaponMenu.create(self.interface.fromHex)
				self.mode = "weaponMenu"
		return True



	def getAllUnits(self, oneSideOnly = False):
		""" Returns a list of all units in the game, or if side is given, only one units of one side"""
		_units = []
		for _line in self.interface.mainMap:
			for _hex in _line:
				if _hex.unit:
					_hex.unit.position = _hex.position
					_units.append(_hex.unit)
					if _hex.unit.content:
						for _unit in _hex.unit.content.units[0]:
							if _unit:
								_unit.position = _hex.position
								_units.append(_unit)
						for _unit in _hex.unit.content.units[1]:
							if _unit:
								_unit.position = _hex.position
								_units.append(_unit)
				elif _hex.content:
					for _unit in _hex.content.units[0]:
						if _unit:
							_unit.position = _hex.position
							_units.append(_unit)
					for _unit in _hex.content.units[1]:
						if _unit:
							_unit.position = _hex.position
							_units.append(_unit)
		# all units collected
		if oneSideOnly:
			return [x for x in _units if x.faction == oneSideOnly ]
		else:
			return _units



	def handleChangeMode(self):
		self.display.blit(self.interface.modeChange, [403, 500])
		pygame.display.update()
		_changeMode = True
		while _changeMode:
			for event in pygame.event.get():
				# Keyboard
				keysPressed = pygame.key.get_pressed()
				if keysPressed[pygame.K_q] or keysPressed[pygame.K_ESCAPE]:
					_changeMode = False
					pygame.time.delay(150)
				elif keysPressed[pygame.K_F1]:
					self.round += 1
					pygame.draw.rect(self.display, colors.historylineBrown, (405, 502, 317, 122))
					_nextRoundText = font60.render('Round ' + str(self.round), True, colors.historylineLight) 
					self.display.blit(_nextRoundText, [450, 540])
					pygame.display.update()
					pygame.time.delay(2000)
					_changeMode = False
					self.playerTurn = 2



	def checkInput(self):
		""" Checks and responds to input from keyboard and mouse """
		for event in pygame.event.get():
			# Quit
			if event.type == pygame.QUIT:
				self.running = False
			# Mouse
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mX, mY = pygame.mouse.get_pos()
				if self.mouseClick.tick() < 500:						# if doubleclick detected
					self.handleSelection()
				elif self.interface.rectMap.collidepoint(mX, mY):		# if inside map
					result =  self.findHex(mX, mY)
					if result:
						self.interface.cursorPos = result
				elif self.interface.rectMini.collidepoint(mX, mY):		# if inside miniMap			sparkmig
					percentageX = (mX - self.interface.rectMini.x) / self.interface.rectMini.width
					percentageY = (mY - self.interface.rectMini.y) / self.interface.rectMini.height
					maxDispX = self.info.mapWidth - 8	# because 8 is the shown screen width
					dispX = int(percentageX * percentageX * 10)
					dispX = int(maxDispX) if dispX > maxDispX else dispX
					dispX = 0 if dispX < 0 else dispX
					self.interface.mapView[0] = dispX
					maxDispY = (self.info.mapHeight + 1) / 2
					dispY = int(percentageY * percentageY * 50)
					dispY = int(maxDispY) if dispY > maxDispY else dispY
					dispY = 0 if dispY < 0 else dispY
					self.interface.mapView[1] = dispY
					self.interface.cursorPos = [int((percentageX + 0.05) * 7), int((percentageY + 0.05) * 23)]	# add 5% to be able to reach last hexes
				else:
					print("outside both maps",  mX, mY)
		# Keyboard
		keysPressed = pygame.key.get_pressed()
		if keysPressed[pygame.K_q]:
			self.running = False
		elif keysPressed[pygame.K_ESCAPE]:
			if self.holdEscape:
				self.holdEscape = False
				pygame.time.delay(500)
			else:
				self.running = False
		elif keysPressed[pygame.K_LEFT]:
			self.interface.cursorMove('Left')
		elif keysPressed[pygame.K_RIGHT]:
			self.interface.cursorMove('Right')
		elif keysPressed[pygame.K_UP]:
			self.interface.cursorMove('Up')
		elif keysPressed[pygame.K_DOWN]:
			self.interface.cursorMove('Down')
		elif keysPressed[pygame.K_SPACE]:
			self.handleSelection()
		elif keysPressed[pygame.K_e]:
			if self.cmdArgs.mapedit:
				pygame.time.delay(150)
				self.cmdArgs.editor.showMenus()
		elif keysPressed[pygame.K_F1]:
			self.handleChangeMode()
		# ------------------------------------- test begin -------------------------------------
		elif keysPressed[pygame.K_KP4]:
			self.test[0] -= 1
		elif keysPressed[pygame.K_KP6]:
			self.test[0] += 1
		elif keysPressed[pygame.K_KP8]:
			self.test[1] -= 1
		elif keysPressed[pygame.K_KP2]:
			self.test[1] += 1
		elif keysPressed[pygame.K_d]:
	#		test = self.getAllUnits(0)
	#		for t in test:
	#			print(t.name, t.moved)

			cursorHex = self.interface.currentSquare()
#			print(cursorHex.unit)
#			print(cursorHex.unit.faction == self.info.player)
#			print(cursorHex.unit.moved)

			print(cursorHex.unit.name, cursorHex.unit.moved)


#			print(self.interface.mainMap[5][0].name, self.interface.mainMap[5][0].owner)
#			print(self.interface.mainMap[18][5].name, self.interface.mainMap[18][5].owner)
#			obj = self.interface.mainMap[45][6]
#			print(obj.position)
#			print(  self.interface.currentSquare().position  )
			sys.exit()
		# ------------------------------------- test end ---------------------------------------
		elif keysPressed[pygame.K_PAGEUP]:
			self.interface.mapView = [0, 0]
		elif keysPressed[pygame.K_PAGEDOWN]:
			self.interface.mapView = [0, 24]



	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.running:
			if self.playerTurn == 1:
				if self.mode == "actionMenu":
					self.interface.actionMenu.checkInput()
				elif self.mode == "weaponMenu":
					self.interface.weaponMenu.checkInput()
				elif self.mode == "showContent":
					self.interface.contentMenu.checkInput()
				else:
					self.checkInput()
			else:
				self.computerPlayer.moveAllUnits()
				self.interface.resetUnits()
			self.interface.draw()
			pygame.display.update()
		pygame.quit()
		print('\n  Game terminated gracefully\n')


# --- Main  ---------------------------------------------------------------------------------------


#check arguments
parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=120))
parser.add_argument('levelMap')
parser.add_argument("-v", "--version",		action="store_true",	help="Print version and exit")
parser.add_argument("-n", "--hexnumbers",	action="store_true",	help="Show numbers on hex fields (for DEV)")
parser.add_argument("-g", "--generate",		action="store_true",	help="Generates and saves a new map file")
parser.add_argument("-r", "--reveal",		action="store_true",	help="Always show entire map (for DEV)")
parser.add_argument("-m", "--mapedit",		action="store_true",	help="Map editor enabled (for DEV)")
args = parser.parse_args()

# handle commandline arguments
if args.version:
	sys.exit("\n  " + str(version) + "\n")
if args.generate:
	filename = generateMap()
	sys.exit('\n  Generated new map was saved as "' + filename + '"\n')
args.mapPath = "levels/" + args.levelMap + ".json"
if not os.path.exists(args.mapPath):
	print("\n  The level '" + str(args.levelMap) + "' does not exist.")
	print("    These are the level files:")
	levelFiles = os.listdir("levels")
	for level in levelFiles:
		print("      ", level[:-5])
	print()
	sys.exit()

# run game
obj =  Main(args)






# --- TODO --------------------------------------------------------------------------------------- 
# - Calculate hex movement with lower move cost (ie. roads) :	Collect all possible paths within range, calculate collect movepoints for all squares in each path!
#	- units must block adjacent hexes, ie. higher movement costs
# - Develop opponenet AI

# - Content of supply truck should be moved to depot, if truck enters depot
# - kan ikke tage depot fra supplycar
# - genskrive del som er taget ud af artificial intelligence



# --- BUGS --------------------------------------------------------------------------------------- 
# - 



# --- BEYOND ORIGINAL ----------------------------------------------------------------------------
# - artillery should be able to destroy infrastructure
# - create units to supply ammo
# - create units to supply fuel
# - create units to build infrastructure






