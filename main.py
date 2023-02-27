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
from level import Map
from hlrData import *

# --- Variables / Ressources ----------------------------------------------------------------------

version = '0.10'		# weapons done
colors = colorList

# --- Classes -------------------------------------------------------------------------------------


class Main():
	""" get data from API and display it """

	def __init__(self):
		self.width = 1800	# 1110 minimum,as it is smallest map
		self.height = 1000
		self.develop = False
		pygame.init()
		icon = pygame.image.load('gfx/icon.png')
		self.devModeFont = pygame.font.Font('freesansbold.ttf', 32)
		pygame.display.set_icon(icon)
		pygame.display.set_caption('Historyline 1914-1918 Remake')
		self.display = pygame.display.set_mode((self.width, self.height))
		self.viewDsp = [19,19]


	def run(self):
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.map = Map(self, 1)
		self.test = [0, 0]



	def checkInput(self):
		""" Checks and responds to input from keyboard and mouse """
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
		keysPressed = pygame.key.get_pressed()
		if keysPressed[pygame.K_q]:
			self.running = False
		elif keysPressed[pygame.K_ESCAPE]:
			self.running = False
		elif keysPressed[pygame.K_LEFT]:
			self.map.cursorMove('Left')
		elif keysPressed[pygame.K_RIGHT]:
			self.map.cursorMove('Right')
		elif keysPressed[pygame.K_UP]:
			self.map.cursorMove('Up')
		elif keysPressed[pygame.K_DOWN]:
			self.map.cursorMove('Down')
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
			self.viewDsp[1] = 10
		elif keysPressed[pygame.K_PAGEDOWN]:
			self.viewDsp[1] = -990


	def drawInfo(self):
		""" fetches cursor position and fills out info on unit and terrain """
		mapCursor = [self.map.cursorPos[0] + self.map.mapView[0], self.map.cursorPos[1]  + self.map.mapView[1]]
		square = self.map[mapCursor[1]][mapCursor[0]]
		# terrain
		self.display.blit(square.background, [1144, 446])
		if square.infra:	self.display.blit(square.infra, [1144, 446])
		self.display.blit(self.map.cursorGfx, [1132, 435])
		if square.movementModifier != None:
			self.display.blit(self.map.progressBar, [1460, 445], (0, 0, square.movementModifier * 30, 20))
		else:
			self.display.blit(self.map.iProgressBar, [1460, 445])
		if square.battleModifier != None:
			self.display.blit(self.map.progressBar, [1460, 475], (0, 0, square.battleModifier * 3, 20))	
		else:
			self.display.blit(self.map.iProgressBar, [1460, 475])
		self.display.blit(self.map.progressBar, [1460, 505], (0, 0, square.sightModifier * 30, 20))
		# unit
		if square.unit:
			self.display.blit(self.map.blankHex, [1144, 573])
			self.display.blit(square.unit.mapIcon, [1144, 573])
			self.display.blit(self.map.cursorGfx, [1132, 563])
			pygame.draw.rect(self.display, colors.almostBlack, (1124, 763, 662, 58), 4)							# weapons borders 1
			pygame.draw.rect(self.display, colors.almostBlack, (1124, 871, 662, 58), 4)							# weapons borders 2
			# weapons
			yCoords = [767, 821, 875, 929]			
			for y in range(4):
				weapon = square.unit.weapons[y]
				if weapon:
					# render weapon gfx background
					self.display.blit(weapon.picture, [1128, yCoords[y]])
					if weapon.ammo:
						# render ammo
						ammoText = font30.render(str(weapon.ammo), True, colors.grey, colors.almostBlack)
						rAmmoText = ammoText.get_rect()
						rAmmoText.topleft = (1140, yCoords[y] + 10)
						pygame.draw.rect(self.display, colors.almostBlack, (1128, yCoords[y], 41, 50), 0)
						self.display.blit(ammoText, rAmmoText)
					# render power
					powerText = font20.render(str(weapon.power), True, colors.grey)
					rPowerText = powerText.get_rect()
					rPowerText.topleft = (1441, yCoords[y] + 30)
					self.display.blit(powerText, rPowerText)
					# render range
					powerText = font20.render(str(weapon.rangeMin) + ' - ' + str(weapon.rangeMax), True, colors.grey)
					rPowerText = powerText.get_rect()
					rPowerText.topleft = (1728, yCoords[y] + 30)
					self.display.blit(powerText, rPowerText)
				else:
					self.display.blit(self.map.noWeapon, [1128, yCoords[y]])



#		print('Cursor on Hex:', mapCursor)
#		print(self.test)



	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.running:
			self.checkInput()
			self.map.draw()
			self.drawInfo()
			pygame.display.update()
			self.renderList = []
		pygame.quit()
		print('\n  Game terminated gracefully\n')


# --- Main  ---------------------------------------------------------------------------------------


#check arguments
parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=120))
parser.add_argument("-v", "--version",	action="store_true",	help="Print version and exit")
args = parser.parse_args()

obj =  Main()
obj.run()


# --- TODO ---------------------------------------------------------------------------------------
# - 
# - 
# - 


# --- NOTES --------------------------------------------------------------------------------------





