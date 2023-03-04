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
flagIndex = {'Germany' : 0, 'France' : 1}

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
			self.map.mapView = [0, 0]
		elif keysPressed[pygame.K_PAGEDOWN]:
			self.map.mapView = [0, 24]


	def drawInfo(self):
		""" fetches cursor position and fills out info on unit and terrain """
		mapCursor = [self.map.cursorPos[0] + self.map.mapView[0], self.map.cursorPos[1]  + self.map.mapView[1]]
		square = self.map[mapCursor[1]][mapCursor[0]]
		# terrain
		self.display.blit(square.background, [1144, 446])
		if square.infra:	self.display.blit(square.infra, [1144, 446])
		self.display.blit(self.map.hexBorder, [1142, 444])
		if square.movementModifier != None:
			self.display.blit(self.map.progressBar, [1460, 444], (0, 0, square.movementModifier * 30, 20))
		else:
			self.display.blit(self.map.iProgressBar, [1460, 444])
		if square.battleModifier != None:
			self.display.blit(self.map.progressBar, [1460, 474], (0, 0, square.battleModifier * 3, 20))	
		else:
			self.display.blit(self.map.iProgressBar, [1460, 474])
		self.display.blit(self.map.progressBar, [1460, 504], (0, 0, square.sightModifier * 30, 20))
		# unit
		if square.unit:
			self.display.blit(self.map.unitPanel, [1135, 570])
			self.display.blit(square.unit.mapIcon, [1141, 569])
			pygame.draw.rect(self.display, colors.almostBlack, (1124, 763, 662, 58), 4)							# weapons borders 1
			pygame.draw.rect(self.display, colors.almostBlack, (1124, 871, 662, 58), 4)							# weapons borders 2
			self.display.blit(self.map.unitSkills, [1750, 565])
			self.display.blit(self.map.flags, [1156, 676], (flagIndex[square.unit.country] * 66, 0, 66, 66))
			self.display.blit(self.map.ranksGfx, [1156, 676], (square.unit.experience * 66, 0, 66, 66))
			self.display.blit(square.unit.picture, [1522, 573])
			gfx = font20.render(square.unit.name, True, (208, 185, 140)); self.display.blit(gfx, [1380 - (gfx.get_width() / 2), 575])
			gfx = font20.render(square.unit.faction, True, (208, 185, 140)); self.display.blit(gfx, [1380 - (gfx.get_width() / 2), 610])
			gfx = font20.render(str(square.unit.sight), True, (208, 185, 140)); self.display.blit(gfx, [1318 - (gfx.get_width() / 2), 662])
			gfx = font20.render(str(square.unit.speed), True, (208, 185, 140)); self.display.blit(gfx, [1392 - (gfx.get_width() / 2), 662])
			gfx = font20.render(str(square.unit.currentSize), True, (208, 185, 140)); self.display.blit(gfx, [1462 - (gfx.get_width() / 2), 662])
			gfx = font20.render(str(square.unit.armour), True, (208, 185, 140)); self.display.blit(gfx, [1318 - (gfx.get_width() / 2), 712])
			gfx = font20.render(str(square.unit.weight), True, (208, 185, 140)); self.display.blit(gfx, [1392 - (gfx.get_width() / 2), 712])
			gfx = font20.render(str(square.unit.fuel), True, (208, 185, 140)); self.display.blit(gfx, [1462 - (gfx.get_width() / 2), 712])
			# mark active skills
			for x in square.unit.skills:
				self.display.blit(self.map.skillsMarker, [1748, 535 + (x * 28)])
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


			print(self.map.cursorPos, self.map.mapView)

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





