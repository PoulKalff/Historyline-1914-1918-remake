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
from helperFunctions import *

# --- Variables / Ressources ----------------------------------------------------------------------

version = '0.01'		# init

# --- Classes -------------------------------------------------------------------------------------


class Main():
	""" get data from API and display it """

	def __init__(self):
		self.width = 1800	# 1110 minimum,as it is smallest map
		self.height = 1000
		self.develop = False
		pygame.init()
		self.devModeFont = pygame.font.Font('freesansbold.ttf', 32)
		pygame.display.set_caption('Historyline 1914-1918 Remake')
		self.display = pygame.display.set_mode((self.width, self.height))
		self.viewDsp = [19,19]
		self.cursorX2 = pygame.image.load('gfx/cursor_double.png')


	def run(self):
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.map = Map(self, 1)
		self.test = [1537, 716]



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
			self.test[0] -= 1
		elif keysPressed[pygame.K_RIGHT]:
			self.map.cursorMove('Right')
			self.test[0] += 1
		elif keysPressed[pygame.K_UP]:
			self.map.cursorMove('Up')
			self.test[1] -= 1
		elif keysPressed[pygame.K_DOWN]:
			self.map.cursorMove('Down')
			self.test[1] += 1
		elif keysPressed[pygame.K_PAGEUP]:
			self.viewDsp[1] = 10
		elif keysPressed[pygame.K_PAGEDOWN]:
			self.viewDsp[1] = -990


	def drawBorders(self):
		""" Draws borders and text """
		pygame.draw.rect(self.display, colors.almostBlack, (0, 0, 1800, 1000), 4)							# window border
		pygame.draw.rect(self.display, colors.almostBlack, (15, 15, 1098, 968), 4)								# map border (main map = 1098 / 968)
		pygame.draw.rect(self.display, colors.historylineLight , (1124, 15,  662, 400), 0)					# minimap background
		pygame.draw.rect(self.display, colors.almostBlack, (1124, 15,  662, 400), 4)							# minimap border
		pygame.draw.rect(self.display, colors.almostBlack, (1124, 426, 662, 273), 4)							# unused middle window border
		pygame.draw.rect(self.display, colors.almostBlack, (1124, 710, 662, 273), 4)						# unused lower window border
		self.display.blit(*self.map.movementModifierText)
		self.display.blit(*self.map.battleModifierText)
		return True


	def drawInfo(self):
		""" fetches cursor position and fills out info on unit and terrain """
		mapCursor = [self.map.cursorPos[0] + self.map.mapView[0], self.map.cursorPos[1]  + self.map.mapView[1]]
		square = self.map[mapCursor[1]][mapCursor[0]]
		self.display.blit(pygame.transform.scale2x(square.background), [1180, 483])
		if square.infra:	self.display.blit(pygame.transform.scale2x(square.infra), [1180, 483])
		if square.unit:		self.display.blit(pygame.transform.scale2x(square.unit.mapIcon), [1180, 483])
		self.display.blit(self.cursorX2, [1155, 463])
		# texts
		mmText = font50.render(str(square.movementModifier), True, colors.darkRed)
		rmmText = mmText.get_rect()
		rmmText.topleft = (1555, 501)
		self.display.blit(mmText, rmmText)
		bmText = font50.render(str(square.battleModifier), True, colors.darkRed)
		rbmText = bmText.get_rect()
		rbmText.topleft = (1555, 600)
		self.display.blit(bmText, rbmText)


#		print('Cursor on Hex:', mapCursor) 
#		print(self.test)



	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.running:
			self.checkInput()
			self.map.draw()
			self.drawInfo()
			self.drawBorders()
			pygame.display.update()
			self.renderList = []
		pygame.quit()
		print('\n  Game terminated gracefully')


# --- Main  ---------------------------------------------------------------------------------------


#check arguments
parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=120))
parser.add_argument("-v", "--version",	action="store_true",	help="Print version and exit")
args = parser.parse_args()


colors = colorList

obj =  Main()
obj.run()


# --- TODO ---------------------------------------------------------------------------------------


# --- NOTES --------------------------------------------------------------------------------------





