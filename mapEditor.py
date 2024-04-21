import os
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


def generateMap():
	""" generate a new map with placeholder data, and save to file """
	name = 		input("Name of the Map : ").capitalize()
	height = 	int(input("Height of the Map : "))
	width = 	int(input("Widthh of the Map : "))
	no = 		input("Number of the Map : ")
	_player = 	input("Map player (EC/CP) : ")
	_type =		input("Summer or Winter (s/w) : ")
	filename =	"level" + str(no) + "_" + _player.lower() + ".json"
	expPath =	os.path.join("levels", filename)
	if _player.upper() == "EC":
		player = "Entente Cordial"
	elif _player.upper() == "CP":
		player = "Central Powers"
	else:
		sys.exit("Error... please select EC or CP")
	if _type.lower() == "w":
		tile = "grass_w"
	else: 
		tile = "grass"
	tiles = {}
	hexEntry = [tile, "",""]
	jsonData = {
					"mapName" :	None,
					"mapNo" :	None,
					"player" :	None,
					"tiles" :	{}
				}
	# assemble data
	jsonData["mapName"] = name
	jsonData["mapNo"] = no
	jsonData["player"] = player
	for x in range(height):
		key  = "line" + str(x + 1)
		value = []
		_width = width if x % 2 == 0 else width - 1 
		for y in range(_width):
			value.append(hexEntry)
		tiles[key] = value
	jsonData["tiles"] = tiles
	with open(expPath, "w") as json_file:
		json.dump(jsonData, json_file, indent=4)
	return filename


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
		currentSquare = self.parent.interface.currentSquare()
		while self.menuRunning:
			self.parent.display.blit(self.menus[self.activeMenu.get()], (1124, 15))
			# cusor
			_selection = [self.activeMenu.get(), self.cursorPos[0].get(), self.cursorPos[1].get()]
			_selName = self.menuContent[_selection[0]][_selection[1]][_selection[2]]
			pygame.draw.rect(self.parent.display, colors.green, (	1128 + self.cursorPos[0].get() * 197, 
																	59 + self.cursorPos[1].get() * 20, 
																	198,
																	20), 3)
			# display selection
			if _selection[0] == 0:
				self.parent.display.blit(bgTiles[_selName], [1150, 850])
			else:
				self.parent.display.blit(currentSquare.background, [1150, 850])
			if _selection[0] == 1:
				if _selName != "<none>":
					self.parent.display.blit(infraIcons[_selName], [1150, 850])
			elif _selection[0] == 2:
				if _selName != "<none>":
					unitDisplay = Unit(_selName)
					self.parent.display.blit(unitDisplay.allIcons[0], [1150, 842])
			pygame.display.update()
			self.checkInput()



	def executeChange(self):
		""" execute selection and update map """
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
		# assign the name of the tile to the .json-file, to preserve the change
		with open(self.parent.cmdArgs.mapPath) as json_file:
			jsonLevelData = json.load(json_file)
			jsonLevelData["tiles"]["line" + str(mapCursor[1] + 1)][mapCursor[0]][_selection[0]] = _fileWriteData
		self.saveData(jsonLevelData)
		# redraw all to show change
		self.parent.interface.generateMap()
		self.parent.interface.draw()
		pygame.display.update()




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
			if event.type == pygame.QUIT:
				pass
			# Mouse
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mX, mY = pygame.mouse.get_pos()
				if self.parent.mouseClick.tick() < 500:						# if doubleclick detected
					self.executeChange()
				elif self.parent.interface.rectMap.collidepoint(mX, mY):		# if inside map
					result =  self.parent.findHex(mX, mY)
					if result:
						self.parent.interface.cursorPos = result
						self.parent.interface.draw()
						pygame.display.update()
				elif 1128 < mX < 1728 and 59 < mY < 969:			# inside menu area
					menuX = mX - 1128
					menuY = mY - 59
					cellX = math.floor(menuX / 200)
					cellY = math.floor(menuY / 20)
					menu = self.menuContent[self.activeMenu.get()]
					# check if valid column
					if cellX > len(menu) - 1:
						pass		# invalid column, ignore
					else:
						# check if valid row
						if cellY > len(menu[cellX]) - 1:
							pass		# invalid row, ignore
						else:
							self.cursorPos[1].count = cellY
							self.cursorPos[0].count = cellX
				else:
					pass	# outside Menu area
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
			self.executeChange()
			pygame.time.delay(150)
		elif keysPressed[pygame.K_e]:
			self.menuRunning = False
			pygame.time.delay(150)
		elif keysPressed[pygame.K_q]:
			self.menuRunning = False
			pygame.time.delay(150)
 












