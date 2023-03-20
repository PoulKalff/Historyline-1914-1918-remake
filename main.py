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

version = '0.50'		# gfx interface done

# --- Classes -------------------------------------------------------------------------------------


class Main():
	""" get data from API and display it """

	def __init__(self):
		self.width = 1800	# 1110 minimum,as it is smallest map
		self.height = 1000
		self.develop = False
		pygame.init()
		icon = pygame.image.load('gfx/gameIcon.png')
		self.devModeFont = pygame.font.Font('freesansbold.ttf', 32)
		pygame.display.set_icon(icon)
		pygame.display.set_caption('Historyline 1914-1918 Remake')
		self.display = pygame.display.set_mode((self.width, self.height))


	def run(self):
		self.initGame()
		self.loop()


	def initGame(self):
		self.running = True
		self.playerSide = 'Central Powers'			# hardcoded, for now
		self.interface = GUI(self, 1)
		self.test = [0, 0]


	def doAction(self, result):
		""" execute action selected in the action menu """
		if result == 0:
			print('Attack')
		elif result == 1:	# MOVE
			self.interface.markMovableSquares()



		elif result == 2:
			print('View unit content')
		elif result == 3:
			print('Closed actionMenu, back to main loop')



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
			self.interface.cursorMove('Left')
		elif keysPressed[pygame.K_RIGHT]:
			self.interface.cursorMove('Right')
		elif keysPressed[pygame.K_UP]:
			self.interface.cursorMove('Up')
		elif keysPressed[pygame.K_DOWN]:
			self.interface.cursorMove('Down')
		elif keysPressed[pygame.K_SPACE]:
			self.interface.actionMenu.show(self.interface.currentSquare())
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
			if self.interface.actionMenu.active:
				result = self.interface.actionMenu.checkInput()
				if result != None:
					self.doAction(result)
			else:
				self.checkInput()
			self.interface.draw()
			pygame.display.update()
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





