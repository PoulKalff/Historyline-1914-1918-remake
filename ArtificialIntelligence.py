import sys
import math
import numpy

# --- Variables / Ressources ----------------------------------------------------------------------

showCalculations = True

# --- Functions -----------------------------------------------------------------------------------


# --- Classes -------------------------------------------------------------------------------------


class AI():
	""" Controls the opposing side (EC or CP) """


	def __init__(self, parent):
		self.parent = parent



	def moveAllUnits(self):
		""" iterate through the units, moving each one. Called from main each round """
		if showCalculations:
			print("\nCalculating computer player movements:")
			print("----------------------------------------------")
		for unit in self.parent.getAllUnits(0):
			self.moveUnit(unit)
		# some message to tell player that the sides have changed...?
		if showCalculations:
			print("----------------------------------------------")
		self.parent.playerTurn = 1



	def moveUnit(self, unitToMove):
		""" calculate best movement for the given unit and move it """
		if showCalculations:
			print('   Now calculating movement for "' + unitToMove.name + '"...' + str(unitToMove.position))
		# call adajcent hexes to get all possible moves
		allPossibleMoves = self.parent.interface.getMovableSquares(self.parent.interface.getSquare(unitToMove.position))
		print("      Moves available:", len(allPossibleMoves))



		# - use some other function to calculate best possible move
		# - show the move? (perhaps user should choose wheter to show or not (like BI3))


