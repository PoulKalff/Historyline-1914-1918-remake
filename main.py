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
#from PIL import Image

from helperFunctions import *
from level import Map

# --- Variables / Ressources ----------------------------------------------------------------------

pygame.init()
version = '0.01'		# init
sounds = {}
font30 = pygame.font.Font('freesansbold.ttf', 30)
font60 = pygame.font.Font('freesansbold.ttf', 60)


# --- Classes -------------------------------------------------------------------------------------

class colorList:

	black =				(0, 0, 0)
	white =				(255, 255, 255)
	red =				(255, 0, 0)
	cyan =				(0, 255, 255)
	green =				(0, 255, 0)
	grey =				(150, 150, 150)
	darkGrey =			(50, 50, 50)
	almostBlack =		(20, 20, 20)
	orange =			(220, 162, 57)
	green =				(70, 180, 50)
	blue =				(80, 120, 250)
	background =		(55, 55, 55)
	yellow = 			(255, 255, 0)
	bi3 =				(68, 136, 77)
	historylineDark =	(49, 48, 33)
	historylineLight =	(107, 105, 90)


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


	def run(self):
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.map = Map(self, 1)




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
		elif keysPressed[pygame.K_PAGEUP]:
			self.viewDsp[1] = 10
		elif keysPressed[pygame.K_PAGEDOWN]:
			self.viewDsp[1] = -990






	def drawBorders(self):
		pygame.draw.rect(self.display, colors.almostBlack, (0, 0, 1800, 1000), 4)							# window border
		pygame.draw.rect(self.display, colors.almostBlack, (15, 15, 1098, 968), 4)								# map border

#		pygame.draw.rect(self.display, colors.almostBlack, (1045, 16,  865, 498), 4)					# right upper border
#		pygame.draw.rect(self.display, colors.almostBlack, (1045, 535, 865, 498), 4)						# right lower border
		# hide overflow
#		pygame.draw.rect(self.display, colors.historylineDark, (15, 983, 1098, 13))										# map bottom



#		pygame.draw.rect(self.display, colors.background, (0, 0, self.width, 15))							# window top
#		pygame.draw.rect(self.display, colors.background, (0, 0, 15, self.height))						# window left
#		pygame.draw.rect(self.display, colors.background, (self.width - 8, 0, 8, self.height))			# window right
#		pygame.draw.rect(self.display, colors.background, (1035, 0, 5, self.height))						# middle
		return True



	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.running:
			self.checkInput()
			self.map.draw()
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





