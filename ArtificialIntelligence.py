


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
			print('   Now calculating movement for "' + unitToMove.name + '" at ' + str(unitToMove.position))
		# get all possible moves
		x, y = unitToMove.position
		square = self.parent.interface.mainMap[x][y]
		# allPossibleMoves = self.parent.interface.markMovableSquares(square, unitToMove)
		# self.parent.interface.resetSquares()
		# allPossibleTargets = self.parent.interface.markAttackableSquares(square)
		# self.parent.interface.resetSquares()
		# if showCalculations:
		# 	print("      Moves available:", len(allPossibleMoves))
		# 	print("      Targets available:", len(allPossibleTargets))








		# load a set of rules from JSON or whatever? Use these to calculate. But How? Which format?



	#	print("      Move chosen:", "and WHY?")


		# --- for DEV ----------------------------------------------------
#		for move in allPossibleTargets:
#			print(move)
#		self.parent.interface.markFields(allPossibleTargets)
		# --- for DEV ----------------------------------------------------


		# --- for DEV ----------------------------------------------------
	#	for move in allPossibleMoves:
	#		print(move)
	#	self.parent.interface.markFields(allPossibleMoves)
		# --- for DEV ----------------------------------------------------




		# - use some other function to calculate best possible move
		# - show the move? (perhaps user should choose wheter to show or not (like BI3))


