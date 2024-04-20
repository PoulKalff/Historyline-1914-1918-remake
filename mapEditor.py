import sys
import json
import time
import math
import numpy
import pygame
from hlrData import *

# --- Variables / Ressources ----------------------------------------------------------------------

pygame.init()
menuTitles = 	[
					font30.render("Hex Tiles:", True, colors.black),
					font30.render("Infrastructure:", True, colors.black),
					font30.render("Units:", True, colors.black)
				]

# --- Functions -----------------------------------------------------------------------------------


def generateMap(self):
	""" generate a new map with placeholder data, and save to file """

	sys.exit(" def generateMaps(self): ")

	height = 47
	width = 12
	name = 'test'
	no = 0
	player = 'test'
	print('{')
	print('\t"mapName" :\t"' + name + '",')
	print('\t"mapNo" :\t' + str(no) + ',')
	print('\t"player" :\t"' + player + '",')

	print('\t"tiles"\t:{')
	for x in range(height):
		print('\t\t\t\t"line' + str(x + 1) + '":\t[', end="")
		_width = width if x % 2 == 0 else width - 1 
		for y in range(_width):
			print('["i","",""]', end="")
			if y < _width - 1:
				print(', ', end="")
		print("]", end="")
		if x < height - 1:
			print(',')
		else:
			print()
	print('\t\t}')
	print('}')


# --- Classes -------------------------------------------------------------------------------------


class MapEditor():
	""" Allows editing of Hex, Infrastructur and Units """


	def __init__(self, parent):
		self.parent = parent
		self.activeMenu = RangeIterator(3)
		# add hex tiles
		summer = []
		winter = []
		for n in bgTiles.keys():
			if n.endswith("_w"):
				winter.append(n)
			else:
				summer.append(n)
		# add infrastructure
		infra = []
		for n in infraIcons.keys():
			infra.append(n)
		_infra = [[],[],[]]
		for i in infra:
			if i.startswith("road") or i.startswith("path") or i == "<none>":
				_infra[0].append(i)
			elif i.startswith("trench") or i.startswith("stream"):
				_infra[1].append(i)
			else:
				_infra[2].append(i)
		# add units
		ecUnits = []
		cpUnits = []
		for n in unitsParameters.keys():
			if n.startswith("CP_"):
				cpUnits.append(n)
			else:
				ecUnits.append(n)
		self.menus = []
		self.menuContent = 	[	[sorted(summer), 	sorted(winter)], 
								[sorted(_infra[0]), sorted(_infra[1]), sorted(_infra[2])], 
								[sorted(ecUnits), 	sorted(cpUnits)]]		# divided into 3 menus, each of 3 columns
		self.cursorPos = [RangeIterator(len(self.menuContent[self.activeMenu.get()])), RangeIterator(len(   self.menuContent[0][0]  ))]
		# create menu gfx
		for no3, page in enumerate(self.menuContent):
			_menu = pygame.Surface((600, 950))	
			pygame.draw.rect(_menu, colors.red, (0, 0, 600, 950))			# window background
			pygame.draw.rect(_menu, colors.black, (0, 0, 600, 950), 4)		# window border
			pygame.draw.rect(_menu, colors.black, (10, 40, 580, 2))			# top line
			pygame.draw.rect(_menu, colors.black, (10, 800, 580, 2))		# bottom line
			_menu.blit(menuTitles[no3], [10, 10])							# page title
			for no1, column in enumerate(page):
				for no2, name in enumerate(column):
					gfx = font15.render(name, True, colors.black)
					_menu.blit(gfx, [10 + 200 * no1 , 47 + 20 * no2])
			self.menus.append(_menu)



	def showMenus(self):
		""" displays the three editor menus """
		self.menuRunning = True
		while self.menuRunning:
			self.parent.display.blit(self.menus[self.activeMenu.get()], (1124, 15))
			# cusor
			pygame.draw.rect(self.parent.display, colors.green, (	1128 + self.cursorPos[0].get() * 197, 
																	59 + self.cursorPos[1].get() * 20, 
																	198,
																	20), 3)
			pygame.display.update()
			self.checkInput()
		# process selection
		_selection = [self.activeMenu.get(), self.cursorPos[0].get(), self.cursorPos[1].get()]
		_selName = self.menuContent[_selection[0]][_selection[1]][_selection[2]]
		currentSquare = self.parent.interface.currentSquare()
		mapCursor = [self.parent.interface.cursorPos[0] + self.parent.interface.mapView[0], self.parent.interface.cursorPos[1]  + self.parent.interface.mapView[1]]
		# assign new hex object and generate map
		if _selection[0] == 0:
			self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].background = bgTiles[_selName]
			_fileWriteData = _selName
		elif _selection[0] == 1:
			if  _selName == "<none>":
				self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].infra = None
				_fileWriteData = ""
			else:
				if self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].infra == None:
					self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].infra = [infraIcons[_selName]]
					_fileWriteData = [_selName]
				else:
					self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].infra.append(infraIcons[_selName])
					with open(self.parent.cmdArgs.mapPath) as json_file:
						jsonLevelData = json.load(json_file)
						_fileWriteData = jsonLevelData["tiles"]["line" + str(mapCursor[1] + 1)][mapCursor[0]][_selection[0]]
					_fileWriteData.append(_selName)
		elif _selection[0] == 2:
			self.parent.interface.mainMap[mapCursor[1]][mapCursor[0]].unit = Unit(_selName) if _selName != "<none>" else None
			_fileWriteData = _selName if _selName != "<none>" else ""
		self.parent.interface.generateMap()
		# assign the name of the tile to the .json-file, to preserve the change
		with open(self.parent.cmdArgs.mapPath) as json_file:
			jsonLevelData = json.load(json_file)
			jsonLevelData["tiles"]["line" + str(mapCursor[1] + 1)][mapCursor[0]][_selection[0]] = _fileWriteData
		self.saveData(jsonLevelData)




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




	def checkInput(self):
		""" Checks and responds to input from keyboard and mouse """
		for event in pygame.event.get():
			# Quit
			if event.type == pygame.QUIT:
				pass
		# Keyboard
		keysPressed = pygame.key.get_pressed()
		if keysPressed[pygame.K_LEFT]:
			_originalRow = self.cursorPos[1].get()
			self.cursorPos[0].dec()
			nowNoRows = len(self.menuContent[self.activeMenu.get()][self.cursorPos[0].get()])
			self.cursorPos[1] = RangeIterator(	nowNoRows	)
			self.cursorPos[1].count = _originalRow if _originalRow < self.cursorPos[1].max else self.cursorPos[1].max - 1
			pygame.time.delay(150)
		elif keysPressed[pygame.K_RIGHT]:
			_originalRow = self.cursorPos[1].get()
			self.cursorPos[0].inc()
			nowNoRows = len(self.menuContent[self.activeMenu.get()][self.cursorPos[0].get()])
			self.cursorPos[1] = RangeIterator(	nowNoRows	)
			self.cursorPos[1].count = _originalRow if _originalRow < self.cursorPos[1].max else self.cursorPos[1].max - 1
			pygame.time.delay(150)
		elif keysPressed[pygame.K_UP]:
			self.cursorPos[1].dec()
			pygame.time.delay(150)
		elif keysPressed[pygame.K_DOWN]:
			self.cursorPos[1].inc()
			pygame.time.delay(150)
		elif keysPressed[pygame.K_TAB]:
			self.activeMenu.inc()
			self.cursorPos[0] = RangeIterator(len(self.menuContent[self.activeMenu.get()]))
			self.cursorPos[1].count = 0
			pygame.time.delay(150)
		elif keysPressed[pygame.K_RETURN]:
			self.menuRunning = False

















