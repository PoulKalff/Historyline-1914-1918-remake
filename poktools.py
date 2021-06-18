# Poul Kalff python programming module
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import logging as log

# --- Variables ----------------------------------------------------------------------------------

lastChange = '09032021 : improved checkPackageExists() to not ccept '' as packet'

# --- Functions ----------------------------------------------------------------------------------


def add_method(cls):
	""" Decorator function to add a method to an object"""
	def decorator(func):
		def wrapper(self, *args, **kwargs):
			return func(*args, **kwargs)
		setattr(cls, func.__name__, wrapper)
		return func # returning func means func can still be used normally
	return decorator


def ensurePackage(package):
	""" Check whether APT package exists, installs if it not """
	if not checkPackage(package):
		installPackage(package)
	return True


def checkPackageInstalled(package):
	""" Check whether APT package is installed """
	if ' ' in package:
		return -1       # Please specify one package only
	raw_output = runExternal("dpkg -l " + package)
	lines = raw_output.split('\n')
	if len(lines) == 1:
		return False	# package is not known
	# check status of the package: we dont want packages marked as 'rc' (Removed, Configuration exists)
	packageStatusLines = lines[5:]	# removing header-lines
	exactPackage = ' ' + package + ' '	# putting space before and after to get exact match on package name in string (e.g. 'mc', but not 'mc-docs')
	for line in packageStatusLines:
		if exactPackage in line:
			if line.startswith('ii'):
				return True
	return False


def checkPackageExists(package):
	""" Check whether APT package exists """
	if ' ' in package:
		return -1       # Please specify one package only
	if package == '':
		return False
	raw_output = runExternal("apt policy " + package)
	lines = raw_output.split('\n')
	if len(lines) == 3:
		return False
	else:
		return True


def installPackage(package):
	""" Installs package via apt """
	reply = runExternal('sudo apt install ' + str(package) + ' -y')
	return reply


def readFileContents(self, fil):
	""" Read and return file contnts """
	f = open(fil,'r')
	data = f.read()
	f.close()
	return data


def writeFileContents(self, file, content):
	""" Write data to file """
	counter = 0
	while os.path.exists(self.file + '_BACKUP' + str(counter)):
		counter += 1
	shutil.copy(self.file, self.file + '_BACKUP' + str(counter))
	# write file
	nr = 0
	f = open(self.file, 'w')
	for p in self.posts:
		if p.valid:
			nr += 1
			f.writelines(p.toFile(nr))
	f.close()


def runExternal(command):
	""" Runs external process and returns output """
#	process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, stderr=open(os.devnull, 'w'))
#	output, err = process.communicate()
	output = subprocess.getoutput(command)      # New to Python3, untested!
	return output


# --- Classes ------------------------------------------------------------------------------------


class FlipSwitch():
	""" Represents a switch with on and off-state """

	def __init__(self, Ind):
		self._value = bool(Ind)

	def flip(self):
		if self._value == True:
			self._value = False
		else:
			self._value = True

	def get(self):
		return self._value

	def getString(self):
		return str(self._value)


class RangeIterator():
	# (v3) Represents a range of INTs from 0 -> X

	def __init__(self, Ind, loop=True):
		self.current = 0
		self.max = Ind
		self.loop = loop

	def inc(self, count=1):
		self.current += count
		self._test()

	def dec(self, count=1):
		self.current -= count
		self._test()

	def incMax(self, incCurrent = True):
		""" Increase both value and max valuse """
		self.max += 1
		if incCurrent:
			self.current += 1
		self._test()

	def decMax(self, count=1):
		""" Increase both value and max valuse """
		self.max -= count
		self.current -= count
		self._test()

	def _test(self):
		""" Tests that all is well, should be called after any change in values"""
		self.max = 0 if self.max < 0 else self.max
		if self.loop:
			if self.current > self.max:
				self.current -= self.max + 1
			elif self.current < 0:
				self.current += self.max + 1
		elif not self.loop:
			if self.current >= self.max:
				self.current = self.max
			elif self.current < 0:
				self.current = 0

	def get(self):
		return self.current


# --- Main Program -------------------------------------------------------------------------------

# Module cannot be called directly


# --- TODO ---------------------------------------------------------------------------------------
# - Skal have en log-function i en klasse... skal/boer fungere som i movietools
# - Skal teste runExternal, da den er aendret til Python3


