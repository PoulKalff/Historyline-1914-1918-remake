#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import curses
import locale
import poktools

# --- Variables -----------------------------------------------------------------------------------

version = "v0.081"   # fixed selectPath crash on window resize
locale.setlocale(locale.LC_ALL, '')

# --- Functions -----------------------------------------------------------------------------------


# --- Classes -------------------------------------------------------------------------------------

class File:
	""" Slave class used by SelectPath """
	def __init__(self, name):
		self.name = name
	def pad(self, data, width):
		return data + ' ' * (width - len(data))
	def render(self, depth, width):
		return self.pad('%s%s %s' % (' ' * 4 * depth, self.icon(), os.path.basename(self.name)), width)
	def icon(self): return '   '
	def traverse(self): yield self, 0
	def expand(self): pass
	def collapse(self): pass


class Dir(File):
	""" Slave class used by SelectPath """

	def __init__(self, name):
		File.__init__(self, name)
		try: self.kidnames = sorted(os.listdir(name))
		except: self.kidnames = None  # probably permission denied
		self.kids = None
		self.expanded = False
	def factory(self, name):    # copy of parent, rather than sending it with object
		if os.path.isdir(name): return Dir(name)
		else: return File(name)
	def children(self):
		if self.kidnames is None: return []
		if self.kids is None:
			self.kids = [self.factory(os.path.join(self.name, kid))
				for kid in self.kidnames]
		return self.kids
	def icon(self):
		if self.expanded: return '[-]'
		elif self.kidnames is None: return '[?]'
		elif self.children(): return '[+]'
		else: return '[ ]'
	def expand(self): self.expanded = True
	def collapse(self): self.expanded = False
	def traverse(self):
		yield self, 0
		if not self.expanded: return

		for child in self.children():
			for kid, depth in child.traverse():
				yield kid, depth + 1


class SelectPath:
	""" Presents a curses screen where user can select a path / file, returns result """

	def __init__(self, pScreen, startDir="/"):
		self.startDir = startDir
		self.screen = pScreen
		self.selected = []
		mydir = self.factory(self.startDir)
		mydir.expand()
		cursor = 3		# Cursor in view
		pending_action = None
		pending_exit = False
		pending_select = False
		height, width = self.screen.getmaxyx()
		while 1:
			self.screen.clear()
			if width < 100 or height < 6:
				self.screen.addstr(1, 1, "Windows too small to render!", curses.color_pair(1))
			else:
				line = 0
				offset = max(0, cursor - height + 3)
				for data, depth in mydir.traverse():
					if line == cursor:
						self.screen.attrset(curses.color_pair(7) | curses.A_BOLD)
						if pending_action:
							getattr(data, pending_action)()
							pending_action = None
						elif pending_select:
							if data.name in self.selected:
								self.selected.remove(data.name)
							else:
								self.selected.append(data.name)
						if pending_exit:
							return
					else:
						if data.name in self.selected:
							self.screen.attrset(curses.color_pair(14))
						else:
							self.screen.attrset(curses.color_pair(10))
					if 0 <= line - offset < height - 1:
						self.screen.addstr(line - offset, 0, data.render(depth, curses.COLS))
					line += 1
				self.screen.addstr(height - 1, 0, 'Use <space> to select/unselect items, <return> to accept selected items, <Q> or <escape> to cancel', curses.color_pair(1))
				pending_select = False
			self.screen.refresh()
			ch = self.screen.getch()
			if ch == curses.KEY_RESIZE:		# if terminal is resized, it will be caught here as an event
				height, width = self.screen.getmaxyx()
			if ch == curses.KEY_UP: cursor -= 1
			elif ch == curses.KEY_DOWN: cursor += 1
			elif ch == curses.KEY_PPAGE:
				cursor -= height
				if cursor < 0: cursor = 0
			elif ch == curses.KEY_NPAGE:
				cursor += height
				if cursor >= line: cursor = line - 1
			elif ch == curses.KEY_RIGHT: pending_action = 'expand'
			elif ch == curses.KEY_LEFT: pending_action = 'collapse'
			elif ch == 27 or ch == 113:		# <escape> or 'q'
				self.selected = []
				return
			elif ch == 32: pending_select = True		# <space>
			elif ch == ord('\n'): 
				pending_select = True
				pending_exit = True
			cursor %= line


	def factory(self, name):
		""" Slave function, to build up path """
		if os.path.isdir(name): return Dir(name)
		else: return File(name)


# --- Object CLasses -----------------------------------------------------------------------

class nceLine:
	""" Line object"""

	def __init__(self, direction, coord):
		self.coordinate = coord
		self.direction = direction
		self.visible = True
		self.color = 3


class nceMenuListItem():
	""" An item in a menu list """

	def __init__(self, text, constantColor, acutalColor):
		self.text = text
		self.constantColor = constantColor
		self.acutalColor = acutalColor


class nceLabel():
	""" Label object """

	def __init__(self, x, y, textString, color):
		self.x = x
		self.y = y
		self.type = 'nceLabel'
		self.id = None
		self.name = 'Unnamed_Label'
		self.color = color		# not used, only for reference
		self.content = [nceMenuListItem(textString, color, color)]
		self.frame = False


class nceFrame():
	""" Empty Frame object, for decoration """

	def __init__(self, x, y, w, h, color):
		self.x = x
		self.y = y
		self.type = 'nceFrame'
		self.id = None
		self.name = 'Unnamed_Frame'
		self.color = color
		self.content = []
		self.frame = [['╭' + ('─' * w) + '╮', color]]
		for i in range(h):
			self.frame.append(['│' + (' ' * w)  + '│', color])
		self.frame.append(['└' + ('─' * w) + '╯', color])


class nceInputBox():
	""" Dialog object, accepts text input from user """

	def __init__(self, editor, x, y, message, color, ajax = False):
		self.x = x
		self.y = y
		self.type = 'nceInputBox'
		self.id = None
		self.name = 'Unnamed_InputBox'
		self.color = color
		self.frame = True
		self.answer = None
		self.content = []
		self.message = message
		self.width = None
		self.editor = editor
		self.ajax = ajax


	def getInput(self):
		self.answer = self.editor(self.x + 3, self.y + 3, '', self.color, self.ajax)


class nceDialogBox():
	""" Dialog object, which can only be YES or NO """

	def __init__(self, x, y, message, color):
		self.x = x
		self.y = y
		self.type = 'nceDialogBox'
		self.id = None
		self.name = 'Unnamed_DialogBox'
		self.color = color
		self.frame = True
		self.answer = None
		self.content = []
		self.message = message
		self.width = None
		self.pointer = poktools.FlipSwitch(0)


	def updateKeys(self, _key):
		""" Recieves keys and moves on self. """
		if _key == curses.KEY_UP or _key == curses.KEY_DOWN:
			self.switch()
		elif _key == 10:           # Execute (Key ENTER)
			self.answer = self.pointer.get()


	def switch(self, _color = 16):
		""" Changes the marked selection"""
		self.pointer.flip()

		if self.pointer.get():
			self.content[2].acutalColor = 1
			self.content[3].acutalColor = 16
		else:
			self.content[2].acutalColor = 16
			self.content[3].acutalColor = 1


class nceMenu():
	""" Menu object
			content can be list of strings or list of lists of string and color"""

	def __init__(self, x, y, content, color):
		self.x = x
		self.y = y
		self.type = 'nceMenu'
		self.id = None
		self.name = 'Unnamed_Menu'
		self.color = color
		self.content = []
		self.scrollContent = False
		self.width = 0
		for item in content:
			if type(item) == list:
				self.content.append(nceMenuListItem(item[0], item[1], item[1]))
				if len(item[0]) > self.width:
					self.width = len(item[0])
			else:
				self.content.append(nceMenuListItem(item, self.color, self.color))
				if len(item) > self.width:
					self.width = len(item)
		self.frame = False
		self.id = None
		self.pointer = poktools.RangeIterator(len(self.content) - 1, False)
		self.actions = []		# actions bound to menu content
		self.linkedObjects = []		# objects that have identical content and are highlighted from this menu


	def _createFrame(self, content, width):
		result = []
		result.append(['╭' + ('─' * (width)) + '╮', self.color])        # Top
		self.contentItems = len(content)
		for i in range(self.contentItems):
			result.append(['│' + (' ' * (width))  + '│', self.color])
		result.append(['└' + ('─' * (width)) + '╯', self.color])        # Bottom
		return result


	def highlight(self, highligtedItem=None):
		""" Set all items to default color and highlight one"""
		self.pointer.current = highligtedItem
		if self.content:
			for obj in self.content:
				obj.acutalColor = obj.constantColor
			if highligtedItem != None:
				self.content[highligtedItem].acutalColor =  16


	def setWidth(self, _width, add=False):
		""" changes the width of menu and centers text of each item
				REMEMBER to recalculate self.x if necessary """
		_prevWidth = self.width
		if add:
			self.width += _width
		else:
			self.width = _width
		# recalculate frame
		self.frame = self._createFrame(self.content, self.width) if self.frame else False
		# recalculate items
		for item in self.content:
			while len(item.text) < self.width:
				item.text = ' ' + item.text + ' '
			item.text = item.text[:self.width]


	def setFrameColor(self, _color):
		""" Sets the color of the frame of the object, if object has a frame """
		self.color = _color
		if self.frame:
			for nr, i in enumerate(self.frame):
				self.frame[nr][1] = _color


	def setItemColor(self, _color, _itemNr = 'All'):
		""" Sets the color of the text of the item given by _itemNr """
		if _itemNr == 'All':
			start = 0; end = len(self.content)
		elif _itemNr > -1 and _itemNr < len(self.content):
			start = _itemNr; end = _itemNr + 1
		else:
			sys.exit('ERROR: Cannot set color to item number ' + str(_itemNr + 1) + ', since the menu ' + str(self) + ' only contains ' + str(len(self.content)) + ' items')
		for no in range(start, end):
			self.content[no].constantColor = _color
			if self.content[no].acutalColor != 16:
				self.content[no].acutalColor = _color


	def updateKeys(self, _key):
		""" Recieves keys and moves on self. """
		if _key == curses.KEY_UP:
			self.pointer.dec(1)
		elif _key == curses.KEY_DOWN:
			self.pointer.inc(1)
		self.highlight(self.pointer.get())
		# highlight linked objects
		for o in self.linkedObjects:
			o.highlight(self.pointer.get())
		return (self.id, _key)		# send key back, to handle in main program


class NCEngine:
	""" Presents the screen of a program 
			default colours are
				0 white
				1 red
				2 green
				3 orange
				4 blue
				5 purple
				6 cyan
				7 lightgrey
				8 darkgrey
				9 light red
				10 light green
				11 yellow
				12 light blue
				13 purple
				14 cyan
				15 dark white"""

	_borderColor = 0
	_backgroundColor = 17
	lines = []
	objects = {}	# objects can only be added by setter-functions, which will generate and return ID, by which object can be referenced
	drawStack = []	# list of order in which to draw objects
	ajaxFiltered = [None, None]		# filtered lists [all, filtered] used by textEditor, none by default
	running = True
	screenBorder = False
	heightFocus = 0

	def __init__(self, parent):
		self.screen = curses.initscr()
		self.screen.border(0)
		self.screen.keypad(1)
		self.screen.scrollok(0)
		self._getSize()
		self.parent = parent
		self.status = 'Init'
		self.exitKey = 113	# key to exit engine, default set to KEY_Q
		curses.noecho()
		curses.curs_set(0)
		# init colors
		curses.start_color()
		curses.use_default_colors()
		for i in range(0, curses.COLORS):
			curses.init_pair(i, i, curses.COLOR_BLACK)
		curses.init_pair(16, curses.COLOR_RED, curses.COLOR_WHITE)		# special selection color


	def wts(self, xCord, yCord, txt, col=0):
		""" Write to Screen. Wrapper that tests heigth/width before writing to screen  """
		height, width = self.screen.getmaxyx()
		txt = txt[:width - yCord]	# do not draw outside screen
		if xCord > height:
			 self.screen.addstr(1, 1, 'WARNING!! Program tried to write BELOW window! (height=' + str(height) + ', X-coordinate=' + str(xCord) + ')', curses.color_pair(0))
		elif yCord > width:
			 self.screen.addstr(1, 1, 'WARNING!! Program tried to write LEFT OF window! (width=' + str(width) + ', Y-coordinate=' + str(yCord) + ')', curses.color_pair(0))
		else:
			self.screen.addstr(xCord, yCord, str(txt), curses.color_pair(col))
		return True


	def _getSize(self):
		""" Update height/width/center """
		self.height, self.width = self.screen.getmaxyx()
		self.hcenter = int((self.width - 1) / 2)
		self.vcenter = (self.height - 1) / 2
#		self.wts(self.height - 3, 0, str(self.hcenter), 6)	# Debug


	def handleResize(self):
		""" corrects variables that would cause program to crash """
		activeObjectId = self.objects[self.drawStack[-1]].id
		if activeObjectId in [12, 13, 14, 15]:
			self.drawStack.pop()
		curPos = self.objects[self.drawStack[-1]].pointer.current = 0
		self.heightFocus = 0


	def digitsEditor(self, x, y, eString, color):			# UTESTET!
		""" Edits digits """
		self._getSize()
		xPos = int((x * self.width / 100) + 2 if type(x) == float else x)
		yPos = int((y * self.height / 100) - 1 if type(y) == float else y)
		pointer = poktools.RangeIterator(len(eString) - 1, False)
		keyPressed = ''
		teRunning = True
		self.wts(self.height - 1, 0, 'UP/DOWN cycles digit, ENTER accepts changes', 6)    # Overwrite Status
		self.screen.refresh()
		while teRunning:
			stringSliced = [eString[:pointer.get()], eString[pointer.get()], eString[pointer.get() + 1:]]
			self.wts(yPos, xPos, stringSliced[0], 5)
			self.wts(yPos, xPos + len(stringSliced[0]), stringSliced[1], 1)
			self.wts(yPos, xPos + len(stringSliced[0]) + len(stringSliced[1]), stringSliced[2], 5)
			self.wts(yPos, xPos + len(stringSliced[0]) + len(stringSliced[1]) + len(stringSliced[2]), ' ', 0)    # overwrite last char
			#self.wts(yPos + 2, xPos + 10, str(stringSliced) + ' - ' + str(keyPressed))      # Message output
			self.screen.refresh()
			keyPressed = self.screen.getch()
			focusedChar = int(stringSliced[1])
			if keyPressed == 259:             # Cursor UP
				if focusedChar < 9:
					stringSliced[1] = str(focusedChar + 1)
			elif keyPressed == 258:           # Cursor DOWN
				if focusedChar > 0:
					stringSliced[1] = str(focusedChar - 1)
			if keyPressed == 261:           # Cursor RIGHT
				pointer.inc()
				if len(stringSliced[2]) > 0 and stringSliced[2][0] == ':':
					pointer.inc()
			elif keyPressed == 260:           # Cursor LEFT
				if pointer.get() == 0:
					returnFile = stringSliced[0] + stringSliced[1] + stringSliced[2]
					teRunning = False
				else:
					pointer.dec()
					if len(stringSliced[0]) > 0 and stringSliced[0][-1] == ':':
						pointer.dec()
			elif keyPressed == 10:           # Return (Select)
				returnFile = stringSliced[0] + stringSliced[1] + stringSliced[2]
				teRunning = False
			elif keyPressed > 47 and keyPressed < 58:   # 0-9
				stringSliced[1] = chr(keyPressed)
				pointer.inc()
				if len(stringSliced[2]) > 0 and stringSliced[2][0] ==  ':':
					pointer.inc()
			eString = stringSliced[0] + stringSliced[1] + stringSliced[2]
		return returnFile


	def boolEditor(self, x, y, value, color):			# UTESTET!
		""" Edits True/False """
		bValue = 0 if value == 'False' else 1
		pointer = FlipSwitch(bValue)
		self._getSize()
		self.wts(self.height - 9, 0, 'UP/DOWN changes state, ENTER accepts changes', 6)    # Overwrite Status
		xPos = int((x * self.width / 100) + 2 if type(x) == float else x)
		yPos = int((y * self.height / 100) - 1 if type(y) == float else y)
		teRunning = True
		while teRunning:
			self.wts(yPos, xPos, pointer.getString() + ' ', color)
			self.screen.refresh()
			keyPressed = self.screen.getch()
			if keyPressed == 259 or keyPressed == 258:             # Cursor UP / Down
				pointer.flip()
			elif keyPressed == 260:           # Cursor LEFT
				teRunning = False
			elif keyPressed == 10:           # Return (Select)
				teRunning = False
		strValue = pointer.getString()
		returnValue = strValue + ' ' if len(strValue) == 4 else strValue
		return returnValue


	def textEditor(self, x, y, eString, color, updateAjax = False):
		""" Edits a line of text """
		eString += ' '
		pointer = poktools.RangeIterator(len(eString) - 1, False)
		keyPressed = ''
		stringSliced = [[], [], []]
		self._getSize()
		xPos = int((x * self.width / 100) + 2 if type(x) == float else x)
		yPos = int((y * self.height / 100) - 1 if type(y) == float else y)
		self.wts(yPos, xPos, eString, 16)     # overwrite line to edit
		editorRunning = True
		while editorRunning:
			if len(eString) > 0:
				stringSliced[0] = eString[:pointer.get()]
				stringSliced[1] = eString[pointer.get()]
				stringSliced[2] = eString[pointer.get() + 1:]
			self.wts(yPos, xPos, stringSliced[0], color)
			self.wts(yPos, xPos + len(stringSliced[0]), stringSliced[1], 20)
			self.wts(yPos, xPos + len(stringSliced[0]) + len(stringSliced[1]), stringSliced[2], color)
			self.wts(yPos, xPos + len(stringSliced[0]) + len(stringSliced[1]) + len(stringSliced[2]), ' ', 3)    # overwrite last char
#			self.wts(20, 2, "Lenght: " + str(len(eString)) + '   Pointer:' + str(pointer.get()) + '   PointerMax:' + str(pointer.max) + '  ' , 4)
#			self.wts(21, 2, str(stringSliced) + ' ' , 4)
#			self.wts(22, 2, str(len(stringSliced[0])) + ' ' + str(len(stringSliced[1])) + ' ' + str(len(stringSliced[2])) + ' ', 4)
			self.screen.refresh()
			keyPressed = self.screen.getch()
			if keyPressed == 261:            # Cursor RIGHT
				if len(stringSliced[2]) > 0:
					pointer.inc()
			elif keyPressed == 260:          # Cursor LEFT
				if len(stringSliced[0]) > 0:
					pointer.dec()
			elif keyPressed == 10:           # Return (Select)
				# updateAJAX functionality
				if hasattr(self.parent, 'ajax') and updateAjax:
					self.parent.ajax("")
				editorRunning = False
				return eString.strip()
			elif keyPressed == 330:          # Del
				if stringSliced[2] != ' ':
					stringSliced[1] = stringSliced[2][:1]
					stringSliced[2] = stringSliced[2][1:]
					if stringSliced[2] == '':
						stringSliced[2] = ' '
				elif stringSliced[2] == ' ':
					 stringSliced[1] = ''
					 stringSliced[2] = ' '
			elif keyPressed == 263:          # Backspace
				stringSliced[0] = stringSliced[0][:-1]
				pointer.decMax()
				# updateAJAX functionality
				if hasattr(self.parent, 'ajax') and updateAjax:
					self.parent.ajax("".join(stringSliced).strip())
			elif keyPressed < 256 and chr(keyPressed) in ',./-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ':
				stringSliced[1] = chr(keyPressed) + stringSliced[1]
				pointer.incMax()
				# updateAJAX functionality
				if hasattr(self.parent, 'ajax') and updateAjax:
					self.parent.ajax("".join(stringSliced).strip())
			if type(stringSliced) == list:
				eString = ''.join(stringSliced)


	def showColors(self):
		""" Show all colors available with their numbers (helper function) """
		colors = ['white', 'red', 'green', 'orange', 'blue', 'purple', 'cyan', 'lightgrey',
				 'darkgrey', 'light red', 'light green', 'yellow', 'light blue', 'purple', 'cyan', 'dark white']
		max = curses.COLORS if curses.COLORS <= 16 else 16
		self.screen.clear()
		for c in range(0, max):
			self.wts(c + 2, 1, "color " + str(c) + ' : ' + colors[c], c)
		self.wts(18, 1, "color 16 : red on white", 16)
		self.wts(20, 1, 'Color demo, displaying ' + str(max) + ' colors + 1 special')
		self.screen.refresh()
		ch = False
		while not ch:
			ch = self.screen.getch()
		self.exit('Color demo complete')


	def render(self):
		""" handles resize and displays the data in "data" """
		self._getSize()
		self.screen.clear()
		if self.width < 100 or self.height < 6:
			self.wts(1, 1, "Windows too small to render!" , 1)
		else:
			# render border
			if self.screenBorder:
				self.drawBorder()
			# render lines
			self.drawLines()
			# render status
			self.wts(self.height - 1, 1, self.status, 1)		# FUCKER
			# render objects
			self.drawObjects()
		self.screen.refresh()


	def updateStatus(self, newStatus = False):
		""" Update status, from the calling program """
		height, width = self.screen.getmaxyx()
		if newStatus:
			self.status = str(newStatus)
		spaces = width - len(self.status) - 2
		self.wts(height - 1, 1, self.status + ' ' * spaces , 1)
		self.screen.refresh()


	def drawObjects(self):
		""" Draw all objects in drawStack """
		for key in self.drawStack:
			o = self.objects[key]
			if o.rtc:	# only horisontal center is supported currently, and only absolute values
				hcenter = int((self.width - 1) / 2)
				posX = hcenter + o.x
				posY = o.y
			else:
				posX = int((o.x * self.width / 100) if type(o.x) == float else o.x)
				posY = int((o.y * self.height / 100) - 1 if type(o.y) == float else o.y)
			# frame
			if o.frame:
				for nr, item in enumerate(o.frame):
					self.wts(posY + nr, posX + 1, item[0], item[1])
			# text
			for no in range(self.height - 5):						# count through lines on screen, -5 lines used for frame
				if no <= len(o.content) - 1:				# if there is an item for this line
					if o.type == 'nceMenu' and o.scrollContent:
						item = o.content[no + self.heightFocus]
					else:
						item = o.content[no]
					try:
						self.wts(posY + no + 1, posX + 2, item.text[:o.width], item.acutalColor)
					except:
						self.exit('\n\n\nError occured in drawObjects, while drawing : \n\n\n      OBJECT= "' + 
							str(o.content) + '"\n\n\n      ITEM= "' + str(item)) + '"'
		return True


	def drawLines(self):
		""" Draw all lines added to object (except border) """
		intersections = [[], []]
		for l in self.lines:
			if l.visible:
				if l.direction == 'v':
					if l.rtc:
						position = l.coordinate + int((self.width - 1) / 2)
					else:
						position = int((l.coordinate * self.width / 100) if type(l.coordinate) == float else l.coordinate)
					intersections[0].append(position)
					for yPos in range(1, self.height - 2):
						self.wts(yPos, position, '│', self._borderColor)
					# endpoints
					self.wts(0, position, '┬',self._borderColor)
					self.wts(self.height - 2, position, '┴', self._borderColor)
				elif l.direction == 'h':
					if l.rtc:
						position = l.coordinate + ((self.height - 1) / 2)
					else:
						position = int((l.coordinate * self.height / 100) - 1 if type(l.coordinate) == float else l.coordinate)
					intersections[1].append(position)
					self.wts(position, 1, '─' * (self.width - 2), self._borderColor)
					# endpoints
					self.wts(position, 0, '├', self._borderColor)
					self.wts(position, self.width - 1, '┤', self._borderColor)
		# draw intersections
		for x in intersections[1]:
			for y in intersections[0]:
				self.wts(x, y, '┼', self._borderColor)
		self.verticalBoundaries = intersections[0]
		if self.screenBorder:
			self.verticalBoundaries.append(self.width)
		self.verticalBoundaries.sort()



	def drawBorder(self):
		""" Draw the staic border of the screen """
		# horizontal lines
		self.wts(0, 0, '╭' + '─' * (self.width - 2) + '╮', self._borderColor)						# Top
		self.wts(self.height - 2, 0, '└' + '─' * (self.width - 2) + '╯', self._borderColor)			# Bottom
		# vertical lines
		for yPos in range(1, self.height - 2):
			self.wts(yPos, 0, '│', self._borderColor)
			self.wts(yPos, self.width - 1, '│', self._borderColor)


	def getInput(self):
		""" Retrieve input and handle internally then return to calling program """
		keyPressed = self.screen.getch()
		if keyPressed == curses.KEY_RESIZE:		# if terminal is resized, it will be caught here as an event
			self.handleResize()
		curPos = self.objects[self.drawStack[-1]].pointer.get()
		noLines = len(self.objects[self.drawStack[-1]].content)
		self._getSize()
		if len(self.objects[self.drawStack[-1]].content) > self.height - 5:	# only move focus if items do not fit on screen
			if keyPressed == 259:		# arrow up
				if self.heightFocus > 0:
					self.heightFocus -= 1
			elif keyPressed == 258:		# arrow down
				if curPos >= self.height - 6 and curPos != noLines - 1:
					self.heightFocus += 1
		# if keyPressed == 120:	# X, for DEV
		# 	self.exit('Killed for debug:' + 
		# 		'\n----------------------------------' + 
		# 		'\n  Items:           ' + str(noLines) + 
		# 		'\n  Screen height-5: ' + str(self.height - 5) + 
		# 		'\n  Height Focus:    ' + str(self.heightFocus) + 
		# 		'\n  Cursor Position: ' + str(curPos))
		if keyPressed == self.exitKey:
			self.terminate()
		return keyPressed 		# return key for (possible) further action in calling program


	def terminate(self):
		# Set everything back to normal
		self.running = False
		self.screen.keypad(0)
		curses.echo()
		curses.nocbreak()
		curses.endwin()


	def exit(self, _value=None):
		# Set everything back to normal
		self.terminate()
		if not _value:
			sys.exit()
		if type(_value) == list:
			convertedList = '\nContents of list (' + str(len(_value)) + ' elements):\n'
			for item in _value:
				convertedList += '   ' + str(item) + '\n'
			sys.exit(convertedList)
		elif type(_value) == bool:
			sys.exit( '\nValue of boolean variable (' + str(type(_value)) + ')\n   ' + str( _value ) + '\n' )
		elif type(_value) == dict:
			convertedList = '\nContents of dict (' + str(len(_value)) + ' key/value pairs):\n'
			for k, v in _value.items():
				convertedList += '   ' + str(k) + ' : ' + str(v) + '\n'
			sys.exit(convertedList)
		elif type(_value) == int or type(_value) == str or type(_value) == float:
			sys.exit( '\nContents of variable (' + str(type(_value)) + ')\n   ' + str( _value ) + '\n' )
		else:		# assume object
			print()
			print("\nContents of object:", _value)
			for attr, value in _value.__dict__.items():
				print('  ', attr, ':', value)
			print()
			sys.exit()


# --- Setter Functions ----------------------------------------------------------------------------

	@property
	def borderColor(self):
		return self._borderColor

	@borderColor.setter
	def borderColor(self, val):
		self._borderColor = self.color[val.lower()] if type(val) == str else val


	@property
	def backgroundColor(self):
		return self._backgroundColor

	@backgroundColor.setter
	def backgroundColor(self, val):
		""" NB: self.screen.bkgd() uses background color of the pair, and default all colors are initiated with the same background """
		self._backgroundColor = self.color[val.lower()] if type(val) == str else val
		self.screen.bkgd(' ', curses.color_pair(val))


# --- Setter Functions ----------------------------------------------------------------------------

	def generateID(self):
		counter = 1
		while counter in self.objects.keys():
			counter += 1
		return counter		


	def addGridLine(self, type, pos, rtc, visible=True):
		obj = nceLine(type, pos)
		obj.rtc = True if rtc else False
		obj.color = 3
		self.lines.append(obj)
		return obj


	def addFrame(self, x, y, width, height, color, rtc):
		obj = nceFrame(x, y, width, height, color)
		obj.rtc = True if rtc else False
		obj.width = width
		obj.id = self.generateID()
		self.objects[obj.id] = obj
		return obj.id


	def addLabel(self, x, y, content, color, rtc):
		obj = nceLabel(x, y, content, color)
		obj.rtc = True if rtc else False
		obj.frame = False
		obj.width = len(content)
		obj.id = self.generateID()
		self.objects[obj.id] = obj
		return obj.id


	def addInputBox(self, message, color, ajax):
		""" Always appears in the center """
		self._getSize()
		width = len(message) + 2
		obj = nceInputBox(self.textEditor, self.hcenter - 1 - round(width / 2), 10, message, color, ajax)
		obj.rtc = False
		obj.frame = [	['╭' + ('─' * width) + '╮', color],
						['│' + (' ' * width) + '│', color],
						['├' + ('─' * width) + '┤', color],
						['│' + (' ' * width) + '│', color],
						['└' + ('─' * width) + '╯', color]]
		obj.content.append(nceMenuListItem(' ' + message + ' ', 0, 0))
		obj.content.append(nceMenuListItem('', 0, 0))
		obj.content.append(nceMenuListItem('', 0, 0))
		obj.width = width
		obj.id = self.generateID()
		self.objects[obj.id] = obj
		return obj.id


	def addDialogBox(self, message, color):
		""" Always appears in the center """
		self._getSize()
		if message == '': message = 'Please select YES or NO'
		width = len(message) + 2
		obj = nceDialogBox(self.hcenter - 1 - round(width / 2), 10, message, color)
		obj.rtc = False
		obj.frame = [	['╭' + ('─' * width) + '╮', color],
						['│' + (' ' * width) + '│', color],
						['├' + ('─' * width) + '┤', color],
						['│' + (' ' * width) + '│', color],
						['│' + (' ' * width) + '│', color],
						['└' + ('─' * width) + '╯', color]]
		menuText = []
		for text in ['NO ', 'YES']:
			while len(text) < width:
				text = ' ' + text + ' '
			menuText.append(text)
		obj.content.append(nceMenuListItem(' ' + message + ' ', 0, 0))
		obj.content.append(nceMenuListItem('', 0, 0))
		obj.content.append(nceMenuListItem(menuText[0][:width], 1, 16))
		obj.content.append(nceMenuListItem(menuText[1][:width], 2, 1))
		obj.width = width
		obj.id = self.generateID()
		self.objects[obj.id] = obj
		return obj.id


	def addMenu(self, x, y, content, color, frame, rtc):
		obj = nceMenu(x, y, content, color)
		obj.rtc = True if rtc else False
		obj.frame = obj._createFrame(content, obj.width) if frame else False
		obj.highlight(0)
		obj.id = self.generateID()
		self.objects[obj.id] = obj
		return obj.id


# --- Main ---------------------------------------------------------------------------------------

if sys.version_info < (3, 0):
	sys.stdout.write("Sorry, requires Python 3.x\n")
	sys.exit(1)



# --- TODO ---------------------------------------------------------------------------------------
# - Position objects relative to RIGHT SIDE / BOTTOM / VERTICAL CENTER
#		- Menu, set alignment when changing width (not automatically central)


