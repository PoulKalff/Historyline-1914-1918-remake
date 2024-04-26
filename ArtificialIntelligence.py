import sys
import math
import numpy

# --- Variables / Ressources ----------------------------------------------------------------------


# --- Functions -----------------------------------------------------------------------------------


# --- Classes -------------------------------------------------------------------------------------


class AI():
	""" Controls the opposing side (EC or CP) """


	def __init__(self, parent):
		self.parent = parent
		self.units = []
		# find each of the players units... how?
		for _line in parent.interface.mainMap:
			for _hex in _line:
				if _hex.unit and _hex.unit.faction == self.parent.info.opponent:
					self.units.append(_hex.unit)


	def moveAllUnits(self):
		""" iterate through the units, moving each one """
		for unit in self.units:
			self.moveUnit(unit)
		# some message to tell player that the sides have changed...?
		print("Your turn again, human player. Good luck!")
		self.parent.playerTurn = 1



	def moveUnit(self, unitToMove):
		""" calculate best movement for the given unit and move it """
		print('Now calculating movement for "' + unitToMove.name + '"...')
		# - call adajcent hexes to get all possible moves
		# - use some other function to calculate best possible move
		# - show the move? (perhaps user should choose wheter to show or not (like BI3))


