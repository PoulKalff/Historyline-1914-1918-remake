#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import curses
import locale
import socket
import shutil
import filecmp
import poktools
import subprocess
from filecmp import dircmp
from ncengine import NCEngine, nceMenuListItem, SelectPath

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

# --- Variables -----------------------------------------------------------------------------------

version = "v0.90"   # completed Version2

statusArray = { 1 : ["Directory", 3], 2 : ["Installing..", 4], 3 : ["<= Different =>", 1], 4 : ["OK", 2], 5 : ["Missing =>", 1], 
				6 : ["<= Missing", 1], 7 : ["<= Missing =>", 1],  8 : ["Missing", 1], 9 : ["Installed", 2] }

actionMenuArray = [
	[' -> Backup  ', ' <- Restore ', ' Compare    ', ' Edit Descr ', ' Forget     '],
	[' Install    ', ' Edit Dsc   ', ' Forget    ']]

actionMenuStatusArray = [
	['Copy the select item from the OS to the backup-folder', 'Copy the select item from the backup-folder back to the OS', 'Compare the selected item to the backed up version', 'Change the description of the selected item', 'Remove the item from the list of items to track'],
	['Install the package on the system', 'Change the description of the package', 'Stop keeping track of the package']]

centralMenuStatusArray = [
	['Select a file or directory on the OS to add to list', 'View a list of APT-packages'],
	['Write the name of an APT-package to add to list (if it exists)', 'View a list of configuration-file']]

basicConfigFile = '{\n  "host": "%s",\n  "backupPath": "%s",\n  "configFiles": [],\n  "aptPackages": []\n}\n'

# --- Functions -----------------------------------------------------------------------------------

def getStatusCode(statusText):
	statusCode = None
	for key, value in statusArray.items():
		if statusText.strip() == value[0].strip():
			statusCode = key
	return statusCode


# --- Classes -------------------------------------------------------------------------------------

class menuItem():
	""" An item in a menu list """

	def __init__(self, name, statusText, description):
		self.name = name
		self.status = statusText
		self.statusCode = getStatusCode(statusText)
		self.description = description


class BackupTools:
	""" Presents the screen of a program """

	def __init__(self):
		self.hostname = socket.gethostname()
		self.rootPath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		self.checkConfigFile()
		# init view
		self.view = NCEngine(self)
		self.view.borderColor = 2
		self.view.screenBorder = True
		self.view.backgroundColor = 1
		self.ajaxLists = [[],[]]
		# write patience-notice on main screen, while program loads
		self.view.screen.addstr(2, 2, str('Program is analyzing data, please wait...'), curses.color_pair(1))
		self.view.screen.refresh()
		self.viewMode = 1
		self.setupInterface()
		self.switchView()
		self.loop()


	def setupInterface(self):
		""" Loads data and starts up the interface of both viewmodes"""
		loadedData = self.readFromFile()
		# opret objekter
		self.view.addGridLine('h', 2, False)
		self.view.addGridLine('v', 9, True)
		self.view.addGridLine('v', -9, True)
		self.view.addLabel(0, 0, 'Configuration file and path:', 0, False)
		self.view.addLabel(0, 0, 'Apt Packages:', 0, False)
		self.view.addLabel(-14 - len(self.hostname), 0, '[' + self.hostname.upper() + ']', 4, True)
		self.view.addLabel(-5, 0, 'Status:', 0, True)
		self.view.addLabel(9, 0, 'Description:', 0, True)
		# generate 2 x 3 main menus
		id_A2 = self.view.addMenu(-9, 2, [statusArray[item[2]] for item in loadedData[0]], 3, False, True)
		id_B2 = self.view.addMenu(-9, 2, [statusArray[item[2]] for item in loadedData[1]], 3, False, True)
		self.view.objects[id_A2].setWidth(15)
		self.view.objects[id_B2].setWidth(15)
		self.view.objects[id_A2].scrollContent = True
		self.view.objects[id_B2].scrollContent = True
		id_A3 = self.view.addMenu(9, 2, [item[1] for item in loadedData[0]], 3, False, True)
		id_B3 = self.view.addMenu(9, 2, [item[1] for item in loadedData[1]], 3, False, True)
		id_A1 = self.view.addMenu(0, 2, [item[0] for item in loadedData[0]], 3, False, False)
		id_B1 = self.view.addMenu(0, 2, [item[0] for item in loadedData[1]], 3, False, False)
		self.view.objects[id_A1].actions.append(self.showSelectionMenu)
		self.view.objects[id_B1].actions.append(self.showSelectionMenu)
		self.view.objects[id_A3].scrollContent = True
		self.view.objects[id_B3].scrollContent = True
		self.view.objects[id_A1].scrollContent = True
		self.view.objects[id_B1].scrollContent = True
		# colour every second line
		for item in range(0, len(self.view.objects[id_A1].content),2):
			self.view.objects[id_A1].setItemColor(5, item)
		for item in range(0, len(self.view.objects[id_B1].content),2):
			self.view.objects[id_B1].setItemColor(5, item)
		for nr, item in enumerate(self.view.objects[id_A1].content):
			if os.path.isdir(item.text):
				self.view.objects[id_A1].setItemColor(10, nr)
		self.view.objects[id_A1].linkedObjects.extend([self.view.objects[id_A2], self.view.objects[id_A3]])
		self.view.objects[id_B1].linkedObjects.extend([self.view.objects[id_B2], self.view.objects[id_B3]])
		# name primary menus
		self.view.objects[id_A1].name = 'config file list'
		self.view.objects[id_A2].name = 'config file status'
		self.view.objects[id_A3].name = 'config file description'
		self.view.objects[id_B1].name = 'apt package list'
		self.view.objects[id_B2].name = 'apt package status'
		self.view.objects[id_B3].name = 'apt package description'
		# create central menus
		id_centralMenu1 = self.view.addMenu(-18, 20, [['Add New Item', 3], ['Switch View', 3]], 3, True, True)
		obj = self.view.objects[id_centralMenu1]
		obj.name = 'config files central menu'
		obj.setWidth(33)
		obj.actions.append(self.addItem)
		obj.actions.append(self.switchView)
		id_centralMenu2 = self.view.addMenu(-18, 20, [['Add New Package', 3], ['Switch View', 3]], 3, True, True)
		obj = self.view.objects[id_centralMenu2]
		obj.name = 'apt packages central menu'
		obj.setWidth(33)
		obj.actions.append(self.addPackage)
#		obj.actions.append(self.addInstalledPackages)
		obj.actions.append(self.switchView)
		# create action menus.... both are set at position 0,0, overwritten when opened
		id_actionMenuConfig = self.view.addMenu(0,0, [[item, 3, 3] for item in actionMenuArray[0]], 3, True, False)
		obj = self.view.objects[id_actionMenuConfig]
		obj.setFrameColor(2)
		obj.setItemColor(6)
		obj.actions.append(self.updateItem)
		obj.actions.append(self.restoreItem)
		obj.actions.append(self.compareItems)
		obj.actions.append(self.editDescription)
		obj.actions.append(self.removeMenuItem)
		id_actionMenuApt = self.view.addMenu(0, 0, [[item, 3, 3] for item in actionMenuArray[1]], 3, True, False)
		obj = self.view.objects[id_actionMenuApt]
		obj.setFrameColor(2)
		obj.setItemColor(6)
		obj.actions.append(self.installPackage)
		obj.actions.append(self.editDescription)
		obj.actions.append(self.removeMenuItem)
		# comparing labels/menus
		self.view.addLabel(0, 0, 'Original', 3, False)
		self.view.addLabel(0, 0, 'Backed up', 3, True)
		self.view.addMenu(0, 2, [' ' for item in range(self.view.height - 6)], 12, True, False)
		self.view.addMenu(1, 2, [' ' for item in range(self.view.height - 6)], 12, True, True)
		self.view.addDialogBox('Are you sure that you want to overwrite the original', self.view.borderColor)
		self.view.addInputBox('Write the name of the new package', self.view.borderColor, True)
		self.view.status = 'Select an item'
		return 1


	def loop(self):
		""" Ensure that view runs until terminated by user """
		while self.view.running:
			# regulate width of main menu items, to prevent text overlapping
			mainMenuWidth = int((self.view.width - 24) / 2)
			self.view.objects[8].width = mainMenuWidth
			self.view.objects[9].width = mainMenuWidth
			self.view.objects[10].width = mainMenuWidth
			self.view.objects[11].width = mainMenuWidth
			self.view.render()
			self.checkKey(self.view.getInput())
		self.view.terminate()
		sys.exit('\n Program terminated by user\n')


	def switchView(self):
		""" Changes between the two views """
		if self.viewMode == 1:
			self.viewMode = 0
			self.view.drawStack = [1,3,4,5,6,8,10]
			self.view.objects[6].highlight(0)
			self.view.objects[8].highlight(0)
			self.view.objects[10].highlight(0)
			self.view.heightFocus = 0
		else:
			self.viewMode = 1
			self.view.drawStack = [2,3,4,5,7,9,11]
			self.view.objects[7].highlight(0)
			self.view.objects[9].highlight(0)
			self.view.objects[11].highlight(0)
			self.view.heightFocus = 0
		self.view.status = 'Viewmode set to show ' + ('CONFIG FILES' if not self.viewMode else 'APT PACKAGES')
		return 1


	def showSelectionMenu(self):
		""" Create the selectionMenu """
		menuId = 15 if self.viewMode else 14
		self.view.drawStack.append(menuId)
		index, menuItem = self.getHighlightedMenuItem()
		# reset pointer, reposition menu
		obj = self.view.objects[menuId]
		obj.highlight(0)
		obj.x = len(menuItem.name) + 2
		obj.y = index + 3
		# correct coordX if menu below screen
		if self.viewMode:
			if obj.y > self.view.height - 7:
				obj.y = self.view.height - 7
		else:
			if obj.y > self.view.height - 9:
				obj.y = self.view.height - 9
		# color disabled items red
		obj.setItemColor(10)
		if menuItem.statusCode == 9:
			obj.setItemColor(1, 0)
		elif menuItem.statusCode == 4:
			obj.setItemColor(1, 0)
			obj.setItemColor(1, 1)
		elif menuItem.statusCode == 5:
			obj.setItemColor(1, 1)
			obj.setItemColor(1, 2)
		elif menuItem.statusCode == 6:
			obj.setItemColor(1, 0)
			obj.setItemColor(1, 2)
		elif menuItem.statusCode == 7:
			obj.setItemColor(1, 0)
			obj.setItemColor(1, 1)
			obj.setItemColor(1, 2)
		self.view.status = actionMenuStatusArray[self.viewMode][0]
		return 1


	def showCentralMenu(self):
		""" Create the centralMenu """
		if self.view.height < 25:
			self.view.status = "Window too small to show menu"
			return 0
		if self.viewMode:
			self.view.drawStack.append(13)
			self.view.objects[13].highlight(0)
		else:
			self.view.drawStack.append(12)
			self.view.objects[12].highlight(0)
		self.view.status = centralMenuStatusArray[self.viewMode][self.view.objects[self.view.drawStack[-1]].pointer.get()] 
		return 1


	def checkKey(self, key):
		""" Checks and handles keys """
		activeObject = self.view.objects[self.view.drawStack[-1]]
		menuID, keyCode = activeObject.updateKeys(key)
		if keyCode == 258 or keyCode == 259:			# Key UP/DOWN
			# set status according to menu
			if menuID == 10 or menuID == 11:	# primary menus
				self.view.status = 'Select an item'
			elif menuID == 12 or menuID == 13:	# central menus
				self.view.status = centralMenuStatusArray[self.viewMode][activeObject.pointer.get()] 
			elif menuID == 14:	# selection menu
				pass 
		elif keyCode == 260:							# Key LEFT
			if menuID == 14 or menuID == 15:	# only register if selectionMenu
				self.view.drawStack.pop()
		elif keyCode == 261:							# Key RIGHT
			if menuID != 12 and menuID != 13:	# if not in central menu
				keyCode = 10		# overwite keycode to execute
		elif keyCode == 32:								# Key Space
			if  activeObject.id == 10 or activeObject.id == 11:
				self.showCentralMenu()
			elif activeObject.id == 12 or activeObject.id == 13:
				self.view.drawStack.pop()
		elif keyCode == 100:									# Key D, (DEBUG)
			self.view.exit(" DUMPING VARIABLE >>>>>  " + str(  self.view.objects ))
		if keyCode == 10:			# Execute (ENTER)
			if menuID == 10 or menuID == 11:	# primary menus
				activeObject.actions[0]()
			else:
				activeObject.actions[activeObject.pointer.get()]()
		return 1


	def installPackage(self):
		index, menuItem = self.getHighlightedMenuItem()
		if menuItem.statusCode == 9:
			self.view.updateStatus('ERROR: Package "' + menuItem.name + '" is already installed!')
			self.view.drawStack.pop()
			return 0
		package = menuItem.name
		if poktools.checkPackageInstalled(package):
			self.view.updateStatus('"' + package + '" is already installed, status seems to be wrong')
		else:
			height, width = self.view.screen.getmaxyx()
			self.view.updateStatus('Installing package, please be patient...')
			poktools.installPackage(package)
			self.view.objects[7].content[index].text = '   Installed   ' 					# update status
			self.view.objects[7].content[index].constantColor = statusArray[9][1]			# update status colour
			self.view.drawStack.pop()
			self.view.updateStatus('"' + package + '" has been installed')
		return 1


	def ajax(self, _filter):
		""" function called on each keystroke from textEditor, updates lists and calls redraw """
		self.ajaxLists[1] = []
		for item in self.ajaxLists[0]:
			if item.startswith(_filter):
				self.ajaxLists[1].append(item)
		# find the ajax list and update it
		obj = self.view.objects[self.ajaxMenuId]
		obj.content = []
		menuContent = self.ajaxLists[1][:10]
		for item in menuContent:
			obj.content.append(nceMenuListItem(item, obj.color, obj.color))
			if len(item) > obj.width:
				obj.width = len(item)
		if menuContent:
			obj.setWidth(len(max(menuContent, key = len)) + 2)
		# force redraw
		self.view.render()


	def addPackage(self):
		""" Shows systems' installed packages, loops to install """
		self.view.drawStack.pop()
		installedPackages = [ item.text for item in self.view.objects[11].content ]
		commandGetAvailable = "grep ^Package /var/lib/apt/lists/* | awk '{print $2}' | sort -u"
		reply = poktools.runExternal(commandGetAvailable)
		packages = reply.split('\n')
		while packages[0].startswith('grep'):	# remove stderr output
			packages.pop(0)
		self.ajaxLists[0] = packages
		self.ajaxLists[1] = packages[:10]
		commandGetInstalled = "cat /var/log/apt/history.log* | grep 'Commandline: apt install' | sed 's/Commandline: apt install //g'"
		reply = poktools.runExternal(commandGetInstalled)
		packages = reply.split('\n')
		packages2 = []
		for p in packages:
			if '-y' in p:
				p = p.replace('-y', '')
				p = p.strip()
			packages2.append(p.strip())
		packagesString = " ".join(packages2)
		packages3 = list(set(packagesString.split()))
		packages3.sort()
		for p in installedPackages:
			if p in packages3:
				packages3.remove(p)
		running = True
		# run loop while adding packages
		while running:
			superString = ''
			for p in packages3:
				while len(p) < 30:
					p = p + ' '
				superString += p
			chunks = [superString[i:i + 30] for i in range(0, len(superString), 30)]
			lines = ["".join(chunks[i:i+6]) + '\n' for i in range(0, len(chunks), 6) ]
			# add labels
			xCord =	int( (self.view.width - len(lines[0])) / 2  )
			bigFrameId = self.view.addFrame(xCord - 1, 10, len(lines[0]), len(lines), self.view.borderColor, False)
			self.view.drawStack.append(bigFrameId)
			# label to hide shrinking bigFrame
			labelUnderBigFrameId = self.view.addLabel(xCord - 2, 11 + len(lines), (len(lines[0]) + 2) * ' ', 8, False)
			self.view.drawStack.append(labelUnderBigFrameId)
			frameId = self.view.addFrame(xCord - 1, 8, 58, 1, self.view.borderColor, False)
			self.view.objects[frameId].frame[2][0] = self.view.objects[frameId].frame[2][0].replace('└', '├')
			self.view.objects[frameId].frame[2][0] = self.view.objects[frameId].frame[2][0].replace('╯', '┴')
			self.view.drawStack.append(frameId)
			headerId = self.view.addLabel(xCord - 1, 8, ' Packages manually installed on system (and not watched): ', 0, False)
			self.view.drawStack.append(headerId)
			for no, l in enumerate(lines):
				color = 5 if (no % 2) == 0 else 6
				labelId = self.view.addLabel(xCord, 10 + no, l.rstrip(), color, False)
				self.view.drawStack.append(labelId)
				noOfLines = no
			self.view.drawStack.append(21)
			obj = self.view.objects[21]
			obj.y = noOfLines + 14
			obj.content[0].text = ' Package to add (empty to end) '
			self.ajaxMenuId = self.view.addMenu(20, noOfLines + 14, self.ajaxLists[1][:10], 3, True, True)
			self.view.drawStack.append(self.ajaxMenuId)
			self.view.objects[self.ajaxMenuId].setWidth(2, True)
			self.view.objects[self.ajaxMenuId].highlight()
			self.view.render()
			obj.getInput()
			newPackage = obj.answer
			if newPackage == '':
				running = False
			elif newPackage in [item.text for item in self.view.objects[11].content]:
				self.view.status = 'Apt-package "' + newPackage + '" is already in the list'
			elif poktools.checkPackageExists(newPackage):
				if newPackage in packages3:
					packages3.remove(newPackage)
				if poktools.checkPackageInstalled(newPackage):
					self.view.objects[7].content.append(nceMenuListItem('   Installed   ', 2, 2))
				else:
					self.view.objects[7].content.append(nceMenuListItem('    Missing    ', 0, 0))
				self.view.objects[9].content.append(nceMenuListItem('-', 3, 3))
				self.view.objects[11].content.append(nceMenuListItem(str(newPackage), 0, 0))
				self.view.objects[7].pointer.incMax(False)
				self.view.objects[9].pointer.incMax(False)
				self.view.objects[11].pointer.incMax(False)
				self.writeToFile()
				self.view.status = "'" + str(newPackage) + "' added"
			else:
				self.view.status = 'No apt-package called "' + newPackage + '" exists'
			self.view.drawStack = [2, 3, 4, 7, 9, 11]
			keys = list(self.view.objects.keys())
			for k in keys:
				if k > 21:
					self.view.objects.pop(k)
		return 1


	def getHighlightedMenuItem(self):
		""" Returns the highligted menu item object """
		if self.viewMode:
			index = self.view.objects[11].pointer.get()
			name = self.view.objects[11].content[index].text
			status = self.view.objects[7].content[index].text
			description = self.view.objects[9].content[index].text
		else:
			index = self.view.objects[10].pointer.get()
			name = self.view.objects[10].content[index].text
			status = self.view.objects[6].content[index].text
			description = self.view.objects[8].content[index].text
		return (index, menuItem(name, status, description))


	def removeMenuItem(self):
		""" Removes an item and its backup file, if any 
				NB: any backup of the item is deliberately not removed """
		index, menuItem = self.getHighlightedMenuItem()
		menuId = 11 if self.viewMode else 10
		self.view.objects[menuId].content.pop(index)
		self.view.objects[menuId - 2].content.pop(index)
		self.view.objects[menuId - 4].content.pop(index)
		self.view.objects[menuId].pointer.dec(1)
		self.view.objects[menuId].pointer.max -= 1
		self.view.objects[menuId].highlight(index - 1)
		self.view.objects[menuId - 2].highlight(index - 1)
		self.view.objects[menuId - 4].highlight(index - 1)
		self.view.drawStack.pop()
		self.writeToFile()
		self.view.status = 'Package forgotten' if self.viewMode else 'Item removed'
		return 1


	def createPath(self, path):
		""" ensure that given string exists, create if it not """
		dirs = []
		path = os.path.dirname(path)
		while path != '/':
			path, lastDir  = os.path.split(path)
			dirs.append(lastDir)
		dirs.reverse()
		fullPath = ''
		for d in dirs:
			fullPath += '/' + d
			if not os.path.exists(fullPath):
				os.mkdir(fullPath)
				os.chmod(fullPath, 0o777)
		return True


	def updateItem(self):
		""" Copies a config-file to the backup directory """
		self.view.drawStack.pop()
		index, menuItem = self.getHighlightedMenuItem()
		if menuItem.statusCode == 4:
			self.view.updateStatus('ERROR: File/Directory and backup are the same')
			return 0
		if menuItem.statusCode == 6 or menuItem.statusCode == 7:
			self.view.updateStatus('ERROR: Package "' + menuItem.name + '" is missing from file system, and can therefore not be backed up!')
			return 0
		self.view.updateStatus('Copying files, please be patient...')
		src = menuItem.name
		fil = os.path.split(src)[1]
		dst = os.path.join(self.backupPath, src.lstrip('/'))
		self.createPath(dst)		# ensure that path exists
		try:
			if os.path.isdir(src):
				if os.path.exists(dst):	# if dir exists, it must be removed before re-copy
					shutil.rmtree(dst)
				shutil.copytree(src, dst)
				for root, dirs, files in os.walk(dst):
					for d in dirs:
						os.chmod(os.path.join(root, d), 0o777)
					for f in files:
						os.chmod(os.path.join(root, f), 0o777)
			else:
				if os.path.exists(src):
					shutil.copy(src, dst)
					os.chmod(dst, 0o777)
				else:
					self.view.status = 'Item does not exist!'
					return 0
		except:
			self.view.exit('\n  EXCEPTION: Could not copy file "' + src  + '"\n')
		self.view.objects[6].content[index].text = '       OK      ' 					# update status
		self.view.objects[6].content[index].constantColor = statusArray[4][1]			# update status colour
		self.view.status = 'Item was copied to backup'
		return 1


	def restoreItem(self):
		""" Restores a config.file from the backup directory """
		self.view.drawStack.pop()
		index, menuItem = self.getHighlightedMenuItem()
		if menuItem.statusCode == 4:
			self.view.updateStatus('ERROR: File/Directory and backup are the same')
			return 0
		if menuItem.statusCode == 5 or menuItem.statusCode == 7:
			self.view.updateStatus('ERROR: Package "' + menuItem.name + '" is missing from backup, and can therefore not be restored!')
			return 0
		itemType = 'file'
		fileNameOrig = menuItem.name
		self.view.updateStatus('Verify overwriting')
		self.view.drawStack.append(20)
		obj = self.view.objects[20]
		obj.answer = None
		while obj.answer == None:
			self.view.render() 
			key = self.view.getInput()
			obj.updateKeys(key)
		self.view.drawStack.pop()
		if obj.answer == False:
			self.view.status = "Restore was cancelled"
			return 0
		pathOrig, fileName = os.path.split(fileNameOrig)
		fileNameBack = os.path.join(self.backupPath, fileNameOrig.lstrip('/'))
		if not os.path.exists(pathOrig):
			os.makedirs(pathOrig)
		if not os.path.exists(fileNameBack):
			self.view.status = "Backup of item does not exist!"
			return 0
		if os.path.isdir(fileNameBack):
			itemType = 'directory'
			if os.path.exists(fileNameOrig): # if dir exists, it must be removed before re-copy
				shutil.rmtree(fileNameOrig)
			shutil.copytree(fileNameBack, fileNameOrig)
			for root, dirs, files in os.walk(fileNameOrig):
				for d in dirs:
					os.chmod(os.path.join(root, d), 0o777)
				for f in files:
					os.chmod(os.path.join(root, f), 0o777)
		else:
			shutil.copy(fileNameBack, fileNameOrig)
		self.view.objects[6].content[index].text = '       OK      ' 					# update status
		self.view.objects[6].content[index].constantColor = statusArray[4][1]			# update status colour
		self.view.status = 'Original ' + itemType + ' overwritten with backup'
		return 1


	def editDescription(self):
		""" Edits the description of an item """
		self.view.drawStack.pop()
		index, menuItem = self.getHighlightedMenuItem()
		selectedItemText = menuItem.description
		menuId = 9 if self.viewMode else 8
		editedItemText = self.view.textEditor(11 + self.view.hcenter, 3 + index, selectedItemText, 16, False)
		self.view.objects[menuId].content[index].text = editedItemText		# update view / menu
		self.writeToFile()
		self.view.status = "Description edited"
		return 1


	def compareItems(self, created=False):
		""" Determines the type of item """
		self.view.drawStack.pop()
		index, menuItem = self.getHighlightedMenuItem()
		if menuItem.statusCode == 5 or menuItem.statusCode == 6 or menuItem.statusCode == 7:
			self.view.updateStatus('ERROR: Package "' + menuItem.name + '" is missing from backup and/or filesystem!')
			return 0
		fileNameOrig = menuItem.name
		fileName = os.path.split(fileNameOrig)[1]
		fileNameBack = os.path.join(self.backupPath, fileNameOrig.lstrip('/'))
		if not os.path.exists(fileNameOrig):
			self.status = "Source File does not exist!"
			return 0
		elif not os.path.exists(fileNameBack):
			self.status = "Backup of File does not exist!"
			return 0
		if os.path.isdir(fileNameOrig):
			dirLevel = fileNameBack.count(os.sep) - fileNameOrig.count(os.sep)	# Find the number of subdirs on right side, to make indents equal
			leftSide = []
			for root, dirs, files in os.walk(fileNameOrig):
				path = root.split(os.sep)
				leftSide.append( ((len(path) - 2) * '   ') + os.path.basename(root))
				for file in files:
					leftSide.append( ((len(path) -  1) * '   ') + file)
			rightSide = []
			for root, dirs, files in os.walk(fileNameBack):
				path = root.split(os.sep)
				rightSide.append( ((len(path) - (2 + dirLevel)) * '   ') + os.path.basename(root))
				for file in files:
					rightSide.append( ((len(path) - (1 + dirLevel)) * '   ') + file)
		else:
			fileContentOrig = open(fileNameOrig, 'r').read().replace('\t', '    ')
			fileContentBack = open(fileNameBack, 'r').read().replace('\t', '    ')
			leftSide = fileContentOrig.split('\n')
			rightSide = fileContentBack.split('\n')
		# remove main window lines
		self.view.lines[0].visible = False
		self.view.lines[1].visible = False
		self.view.lines[2].visible = False
		self.view.drawStack = [16,17,18,19]
		maxChars = max(len(max(leftSide, key=len)), len(max(leftSide, key=len)))
		maxLines = len(leftSide)
		tbLeft = self.view.objects[18]
		tbRight = self.view.objects[19]
		tbLeft.content[0].acutalColor = tbLeft.content[0].constantColor
		tbRight.content[0].acutalColor = tbRight.content[0].constantColor
		self.view.status = 'Comparing versions of the file "' + fileName + '". Press direction keys to navigate, "Q" key to end...'
		compareItemsRunning = True
		focus = [0, 0]		# Horisontal Focus, Vertical Focus
		self.view.exitKey = 255		# set exitkey above ASCII table to disable key while compare is running
		inFocusLeft = False; inFocusRight = False	# this is to prevent error if inFocusLeft or inFocusRight has no value 
		cmpWindowHeight = self.view.height - 6
		cmpWindowWidth = self.view.hcenter - 3
		# redrawing loop, update window
		while compareItemsRunning:
			self.view._getSize()
			tbLeft.setWidth( int(self.view.width / 2) - 2 )
			tbRight.setWidth( int(self.view.width / 2) - 4 )
			# calculate textbox content
			for nr in range(cmpWindowHeight):
				if nr + focus[1] < len(leftSide):
					inFocusLeft = leftSide[nr + focus[1]][focus[0]:focus[0] + cmpWindowWidth]
					tbLeft.content[nr].text = inFocusLeft
				if nr + focus[1] < len(rightSide):
					inFocusRight = rightSide[nr + focus[1]][focus[0]:focus[0] + cmpWindowWidth]
					tbRight.content[nr].text = inFocusRight
				if inFocusRight == inFocusLeft:
					tbLeft.content[nr].acutalColor = 2
					tbRight.content[nr].acutalColor = 2
				else:
					tbLeft.content[nr].acutalColor = 1
					tbRight.content[nr].acutalColor = 1
			self.view.render()
			# check Keys
			key = self.view.getInput()
			if key == curses.KEY_UP:
				if focus[1] > 0:
					focus[1] -= 1
			elif key == curses.KEY_DOWN:
				if focus[1] < maxLines - cmpWindowHeight - 1:
					focus[1] += 1
			elif key == curses.KEY_LEFT:
				if focus[0] > 0:
					focus[0] -= 1
			elif key == curses.KEY_RIGHT:
				if focus[0] < maxChars - cmpWindowWidth:
					focus[0] += 1
			elif key == 113 or key == 27:     # Keypress Q or escape = End compare
				compareItemsRunning = False
		# reset to main program items
		self.view.drawStack = [1,3,4,5,6,8,10]
		self.view.lines[0].visible = True
		self.view.lines[1].visible = True
		self.view.lines[2].visible = True
		for x in range(0, len(self.view.objects[18].content)):
			self.view.objects[18].content[x].text = ''
		for x in range(0, len(self.view.objects[19].content)):
			self.view.objects[19].content[x].text = ''
		self.view.exitKey = 113
		return 1


	def addItem(self):
		""" Add a new item to the list """
		self.view.drawStack.pop()
		fileList = SelectPath(self.view.screen).selected
		for fileName in fileList:
			if fileName in [item.text for item in self.view.objects[10].content]:
				self.view.updateStatus('ERROR: Item is already in the list')
			else:
				self.view.objects[6].content.append(nceMenuListItem('   Missing =>  ', 0, 0))
				self.view.objects[8].content.append(nceMenuListItem('-', 0, 0))
				self.view.objects[10].content.append(nceMenuListItem(str(fileName), 0, 0))
				self.view.objects[6].pointer.incMax(False)
				self.view.objects[8].pointer.incMax(False)
				self.view.objects[10].pointer.incMax(False)
				self.writeToFile() 
				self.view.updateStatus("Item(s) added succesfully")
		return 1


	def _setStatus(self, data):
		""" Internal function to sets status for loaded objects. Status exists only per session """
		for pair in data[0]:
			fileName = os.path.split(pair[0])[1]
			srcPath = pair[0]
			dstPath = os.path.join(self.backupPath, srcPath.lstrip('/'))
			if os.path.isdir(srcPath):					# Handle DIR comparison
				dcmp = dircmp(srcPath, dstPath)
				if not os.path.exists(dstPath):
					pair.append(5)
				elif dcmp.left_list == dcmp.right_list:
					pair.append(4)
				else:
					pair.append(3)
			elif not os.path.exists(srcPath):
				if os.path.exists(dstPath):
					pair.append(6)               # no source
				else:
					pair.append(7)               # no source, no dest
			elif not os.path.exists(dstPath):
				pair.append(5)               # no dest
			elif os.popen("cmp '" + srcPath + "' '" + dstPath + "'").read() == '':   # since cmp cannot help us
				if filecmp.cmp(srcPath, dstPath):
					pair.append(4)           # source == dest
				else:
					pair.append(3)           # source != dest
			else:
				pair.append(3)               # source != dest
		for pair in data[1]:
			pair.append(int(poktools.checkPackageInstalled(pair[0]) + 8))
		return data


	def checkConfigFile(self):
		""" Check for valid cfg-file and load it only if one exists """
		self.cfgFilename = self.hostname + '.json'
		configPath = os.path.join(self.rootPath, 'config')
		self.configFilePath = os.path.join(configPath, self.cfgFilename)
		if os.path.exists(self.configFilePath):
			return True
		else:	 # ask to create, then create or die
			qstCreate = '?'
			while qstCreate.upper() != 'Y' and qstCreate.upper() != 'N':
				print('\n  A JSON-file for this host : ' + self.cfgFilename + ' was not found. Create it now? (y/n)? : ', end=''),
				qstCreate = input()
			if qstCreate.upper() == 'N':
				sys.exit('    No configuration-file for this host, cannot continue...\n')
			elif qstCreate.upper() == 'Y':
				fh = open(self.configFilePath, 'w')
				fh.writelines(basicConfigFile % (self.hostname, self.rootPath))
				fh.close()
				os.chmod(self.configFilePath, 0o777)
				sys.exit('    Configuration file created! Please notice that backuppath is set to root path\n' + 
					     '      which is not optimal. Plase set it to your prefered location in the confiuration file:\n' +
					     '        "' + self.configFilePath + '"\n' +
					     '      and restart program\n')
			else:
				sys.exit('Program error, exiting....')


	def readFromFile(self):
		""" read from config file for current host """
		cfg = [[],[]]
		backupDir = self.hostname + '.backup'
		fh = open(self.configFilePath, 'r')
		rawData = json.load(fh)
		fh.close()
		self.hostname = rawData['host']
		self.backupPath = rawData['backupPath']
		if not os.path.exists(self.backupPath) and os.path.isdir(self.backupPath):
			os.mkdir(self.backupPath)
			print("'" + self.backupPath + "' did not exist but was created")
		allItems = []
		# self.backupPath is ok, get cfg-entries
		data = [[],[]]
		data[0] = self.sortList(rawData['configFiles'])
		data[1] = self.sortList(rawData['aptPackages'])
		return self._setStatus(data)


	def sortList(self, listOfItems):
		""" Sorts the list alphabetially on the first item in list """
		listOfItems.sort(key = lambda listOfItems: listOfItems[0])
		return listOfItems


	def writeToFile(self): 
		""" Writes back the modified data to the xml-file """
		fh = open(self.cfgFilename, 'w') 
		dataToWrite = { 'host' : self.hostname, 'backupPath' : self.backupPath, 'configFiles' : [], "aptPackages": [] }
		for item in range(0, len(self.view.objects[10].content)):
			dataToWrite['configFiles'].append([self.view.objects[10].content[item].text, self.view.objects[8].content[item].text])
		for item in range(0, len(self.view.objects[11].content)):
			dataToWrite['aptPackages'].append([self.view.objects[11].content[item].text, self.view.objects[9].content[item].text])
		json.dump(dataToWrite, fh, indent=2)
		fh.close()
		return 1


# --- Setter Functions ----------------------------------------------------------------------------

	# experimental, aliases for commonly used values

	@property
	def mainMenuIndex(self):
		return self.view.objects[10 + self.viewMode].pointer.get()

	@property
	def activeMenuIndex(self):
		return self.view.objects[-1].pointer.get()


# --- Main  ---------------------------------------------------------------------------------------

if os.getuid() != 0:
	sys.exit('\n  Must be run with admin priviliges\n')
else:
	pMT = BackupTools()


# --- TODO ---------------------------------------------------------------------------------------
# - 



