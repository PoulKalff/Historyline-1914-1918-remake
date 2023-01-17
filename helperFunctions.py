

class colorList:
	black =			(0, 0, 0)
	white =			(255, 255, 255)
	red =			(255, 0, 0)
	cyan =			(0, 255, 255)
	green =			(0, 255, 0)
	grey =			(150, 150, 150)
	lightGrey =		(150, 150, 150)
	almostBlack =	(20, 20, 20)
	orange =		(220, 162, 57)
	green =			(70, 180, 50)
	blue =			(80, 120, 250)
	background =	(55, 55, 55)
	yellow = 		(255, 255, 0)



class renderObject():
	""" An object to be rendered """

	def __init__(self, frame, coord, pri, descr='None'):
		self.frame = frame
		self.coordinate = coord
		self.priority = pri
		self.description = descr



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



class PlayerMovement():
	""" Representation of the current movement of the player. (Is it necessarry? Could it be simplified?) """

	def __init__(self):
		self.left = False
		self.right = False
		self.up = False
		self.down = False

	def verticalMove(self, direction):
		self.down = False
		if direction:
			self.left = False
			self.right = True
		else:
			self.left = True
			self.right = False

	def goUp(self):
		self.up = True
		self.down = False

	def goDown(self):
		self.up = False
		self.down = True

	def stop(self):
		self.left = False
		self.right = False
		self.up = False
		self.down = False

	def isMoving(self):
		if self.left or self.right or self.up or self.down:
			return True
		else:
			return False

	def show(self):
		print(int(self.left), int(self.right), int(self.up), int(self.down))