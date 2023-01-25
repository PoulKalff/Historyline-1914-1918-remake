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
from level import Level

# --- Variables / Ressources ----------------------------------------------------------------------

pygame.init()
version = '0.01'		# init
sounds = {}
font30 = pygame.font.Font('freesansbold.ttf', 30)
font60 = pygame.font.Font('freesansbold.ttf', 60)


# --- Classes -------------------------------------------------------------------------------------

class Main():
	""" get data from API and display it """

	def __init__(self):
		self.width = 900
		self.height = 700
		self.time_down = 0.0
		self.time_elapsed = 0.0
		self.develop = False
		pygame.init()
		pygame.display.set_caption('HLR')
		self.display = pygame.display.set_mode((self.width, self.height))
		self.viewDsp = [10,10]


	def run(self):
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.level = Level(self, 1)




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
			if self.viewDsp[0] <= 0:
				self.viewDsp[0] += 10
		elif keysPressed[pygame.K_RIGHT]:
			if self.width - self.viewDsp[0] <= self.level.mapWidth - 40:
				self.viewDsp[0] -= 10 
		elif keysPressed[pygame.K_UP]:
			if self.viewDsp[1] <= 0:
				self.viewDsp[1] += 10
		elif keysPressed[pygame.K_DOWN]:
			if self.height - self.viewDsp[1] <= self.level.mapHeight + 40:
				self.viewDsp[1] -= 10


	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.running:
			self.checkInput()
			self.level.update()
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





