import sys

# --- Classes -------------------------------------------------------------------------------------

class AI:
	""" calculates moves for the opponent """

	def __init__(self, game):
		self.game = game
		self.collectivePossibleMoves = []



	def _getNearSquares(self, sqX, sqY):
		""" returns two lists of surrounding squares, one of adjecent squares, the other of squares adjacent to those  """
		out = [[],[]]
		nonAdjacentSquares = []
		nonAdjacentIndexes = [24, 23, 22, 21, 20, 19, 15, 14, 11, 10, 6, 5, 4, 3, 2, 1]
		allNearSquares = 	[
								(sqX - 2, sqY - 2), (sqX - 1, sqY - 2), (sqX, sqY - 2), (sqX + 1, sqY - 2), (sqX + 2, sqY - 2), 
								(sqX - 2, sqY - 1), (sqX - 1, sqY - 1), (sqX, sqY - 1), (sqX + 1, sqY - 1), (sqX + 2, sqY - 1), 
								(sqX - 2, sqY),     (sqX - 1, sqY), 					(sqX + 1, sqY), 	(sqX + 2, sqY), 
								(sqX - 2, sqY + 1), (sqX - 1, sqY + 1), (sqX, sqY + 1), (sqX + 1, sqY + 1), (sqX + 2, sqY + 1), 
								(sqX - 2, sqY + 2), (sqX - 1, sqY + 2), (sqX, sqY + 2), (sqX + 1, sqY + 2), (sqX + 2, sqY + 2)
							]
		for x in nonAdjacentIndexes:
			nonAdjacentSquares.append(allNearSquares.pop(x - 1))
		for coord in allNearSquares:
			if -1 < coord[0] < 7 and -1 < coord[1] < 7:
				out[0].append(coord)
		for coord in nonAdjacentSquares:
			if -1 < coord[0] < 7 and -1 < coord[1] < 7:
				out[1].append(coord)
		return out



	def getPossibleMoves(self):
		""" return a list of possible moves for ALL pieces """
		self.collectivePossibleMoves = []
		for x in range(7):
			for y in range(7):
				if self.game.boardContent[x][y] == self.game.players.active:
					self.collectivePossibleMoves += self.game._calculatePossibleMoves((x,y))
		return self.collectivePossibleMoves



	def analyzeAllMoves(self, bestMovesOnly = False):
		""" calculates a score for all moves """
		for move in self.collectivePossibleMoves:
			self.analyzeMove(move)
		# sort
		self.collectivePossibleMoves.sort(reverse=True, key=lambda x: x.score)
		if bestMovesOnly:
			# remove all moves that does not have top score, for better overview
			if self.collectivePossibleMoves:
				temp = []
				maxValue = max(self.collectivePossibleMoves, key=lambda value: value.score).score
				for move in self.collectivePossibleMoves:
					if move.score == float(maxValue):
						temp.append(move)
				self.collectivePossibleMoves = temp
		return True



	def analyzeMove(self, move):
		""" calculates a score for a move """
		score = 0.0
		enemyAdjacent = False
		enemyNear = False
		squaresGained = [(move.xTo, move.yTo)]
		adjacentTo, nearTo = self._getNearSquares(move.xTo, move.yTo)		# getting squares surrounding the TO-field
		adjacentFrom, nearFrom = self._getNearSquares(move.xFrom, move.yFrom)		# getting squares surrounding the FROM-field
		# make clone, in order to not change game data
		boardClone = copy.deepcopy(self.game.boardContent)
		for coord in adjacentTo:
			if boardClone[coord[0]][coord[1]] == self.game.players.opponent:
				boardClone[coord[0]][coord[1]] = self.game.players.active
		boardClone[move.xTo][move.yTo] = self.game.players.active	# plot move to
		if move.type == 2:
			boardClone[move.xFrom][move.yFrom] = 0	# plot move from, if jump
		# calculate captures
		for sqX2, sqY2 in adjacentTo:
			if self.game.boardContent[sqX2][sqY2] == self.game.players.opponent:
				score += 1.0
				squaresGained.append((sqX2, sqY2))
				move.scoreLog += '+C'
		# check type
		if move.type == 1:		# move is a split
			score += 1.0
			move.scoreLog += '+S'
		else:					# move is a jump
			# check if enemy is close to the square that has been left
			for m in adjacentFrom:
				if boardClone[m[0]][m[1]] == self.game.players.opponent:
					enemyAdjacent = True
			if not enemyAdjacent:
				for m in nearFrom:
					if boardClone[m[0]][m[1]] == self.game.players.opponent:
						enemyNear = True
			if enemyAdjacent:
				score -= 1.5
				move.scoreLog += '-Adjacent'
			elif enemyNear:
				score -= 1.0
				move.scoreLog += '-Near'
		# calculate most possible pieces that can be recaptured
		counterMoves = []
		move.recaptureable = 0
		for x in range(7):
			for y in range(7):
				if boardClone[x][y] == self.game.players.opponent:
					counterMoves += self.game._calculatePossibleMoves((x,y), boardClone)
		for cm in counterMoves:
			adjacentCm, tmp = self._getNearSquares(cm.xTo, cm.yTo)		# getting squares surrounding the TO-fiel
			piecesTaken = 0
			for sqX2, sqY2 in adjacentCm:
				if boardClone[sqX2][sqY2] == self.game.players.active:
					piecesTaken += 1
			move.recaptureable = piecesTaken if piecesTaken > move.recaptureable else move.recaptureable
		score -= move.recaptureable
		if move.recaptureable > 0:
			move.scoreLog += '-Recap' + str(move.recaptureable)
		move.score = score
		return True





