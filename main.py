#!/usr/bin/python3

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import io
import os
import sys
import math
import time
import json
import pygame
import random
import requests
import argparse
import pygame.locals
from io import BytesIO
from gui import GUI
from hlrData import *

# --- Variables / Ressources ----------------------------------------------------------------------

version = '0.54'		# units move almost completed

# --- Classes -------------------------------------------------------------------------------------


class Main():
	""" get data from API and display it """

	def __init__(self, args):
		self.cmdArgs = args
		self.width = 1800	# 1110 minimum, as it is smallest map
		self.height = 1000
		self.develop = False
		pygame.init()
		icon = pygame.image.load('gfx/gameIcon.png')
		self.devModeFont = pygame.font.Font('freesansbold.ttf', 32)
		pygame.display.set_icon(icon)
		pygame.display.set_caption('Historyline 1914-1918 Remake')
		self.display = pygame.display.set_mode((self.width, self.height))
		self.mouseClick = pygame.time.Clock()
		self.holdEscape = False
		self.mode = "normal"		# selection mode: normal, actionMenu, selectMoveTo, moveTo, selectAttack, attack


	def run(self):
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.playerSide = 'Central Powers'			# hardcoded, for now
		self.interface = GUI(self, 1)
		self.test = [0, 0]


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
			if cursorHex.unit:
				self.interface.actionMenu.create()
				self.mode = "actionMenu"
		elif self.mode == "selectMoveTo":
			if cursorHex.fogofwar:				# if field is clear, execute move, else cancel move and return to normal mode
				self.interface.generateMap()
				self.mode = "normal"
			else:
				moveFrom = self.interface.movingFrom.position
				moveTo = cursorHex.position
				movePath = self.interface.findPath(moveFrom, moveTo)
				self.interface.executeMove(movePath)
				self.mode = "normal"
		elif self.mode == "selectAttack":
			if cursorHex.fogofwar:				# if field is clear, execute move, else cancel move and return to normal mode
				self.interface.generateMap()
				self.mode = "normal"
			else:
				self.handleAttack(cursorHex.unit)
		return True



	def handleAttack(self, enemyUnit):
		""" Handles the attack of an enemy unit """


		# select a weapon
		for w in enemyUnit.weapons:
			if w:
				print(w.name)



		# calculate attack
		print("Attacking", enemyUnit.name)




		# regenerate map
		self.interface.generateMap()
		self.mode = "normal"




		sys.exit("notImplemented error: select a unit to attack (main.py, line 158)")
		return True



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
				elif self.interface.rectMini.collidepoint(mX, mY):		# if inside miniMap
					percentageX = (mX - self.interface.rectMini.x) / self.interface.rectMini.width
					percentageY = (mY - self.interface.rectMini.y) / self.interface.rectMini.height
					maxDispY = (self.interface.squareHeight + 1) / 2
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
			if self.holdEscape == True:
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
		# ------------------------------------- test begin -------------------------------------
		elif keysPressed[pygame.K_KP4]:
			self.test[0] -= 1
		elif keysPressed[pygame.K_KP6]:
			self.test[0] += 1
		elif keysPressed[pygame.K_KP8]:
			self.test[1] -= 1
		elif keysPressed[pygame.K_KP2]:
			self.test[1] += 1
		# ------------------------------------- test end ---------------------------------------
		elif keysPressed[pygame.K_PAGEUP]:
			self.interface.mapView = [0, 0]
		elif keysPressed[pygame.K_PAGEDOWN]:
			self.interface.mapView = [0, 24]




	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.running:
			if self.mode == "actionMenu":
				self.interface.actionMenu.checkInput()
			else:
				self.checkInput()
			self.interface.draw()
			pygame.display.update()
		pygame.quit()
		print('\n  Game terminated gracefully\n')


# --- Main  ---------------------------------------------------------------------------------------


#check arguments
parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=120))
parser.add_argument("-v", "--version",		action="store_true",	help="Print version and exit")
parser.add_argument("-n", "--hexnumbers",	action="store_true",	help="Show numbers on hex fields")
args = parser.parse_args()

obj =  Main(args)
obj.run()






# --- TODO --------------------------------------------------------------------------------------- 
# - show contents of unit
# - attack mode
#		handleAttack, line 158




# --- BUGS --------------------------------------------------------------------------------------- 
# - 



# --- NOTES --------------------------------------------------------------------------------------
# - 




