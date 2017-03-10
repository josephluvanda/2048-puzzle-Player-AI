from random import randint
from BaseAI import BaseAI
from copy import deepcopy
import random


actionDic = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}

class PlayerAI(BaseAI):

    def __init__(self):
        self.max_thinking_depth = 2

    def getMove(self, grid):
        with open('log.log', 'a') as f:
            f.write(str(grid.map)+'\n')
            f.flush()
            f.close()
        moves = grid.getAvailableMoves()
        return self.decision(grid)
        #return moves[randint(0, len(moves) - 1)] if moves else None

    def minimize(self, node, alpha=0, beta=0):
        ''' Find the child with the lowest utility value '''

        if self.terminal(node):
            return self.evaluate(node, 2)

        min_child, min_utility = (None, float("inf"))

        node.successors(2)

        for child in node.children:
            utility = self.maximize(child, alpha, beta)

            if min_utility > utility:
                min_utility = utility
                min_child = child

        return (min_child, min_utility)

    def maximize(self, node, alpha=0, beta=0):
        ''' Find the child with the highest utility value '''

        if self.terminal(node):
            return self.evaluate(node, 1)

        max_child, max_utility = (None, -float("inf"))

        node.successors(1)

        for child in node.children:
            utility = self.minimize(child, alpha, beta)

            if max_utility < utility:
                max_utility = utility
                max_child = child

        return (max_child, max_utility)

    def terminal(self, node):
        return node.depth == self.max_thinking_depth


    def evaluate(self, node, player):
        ''' Return max or min tile value for given player '''
        val = 0
        if player == 1:  # max
            val = node.grid.getMaxTile()
        else:
            val = self.get_min_value(node.grid)
        return val

    def get_min_value(self, grid):
        val = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                val = min(val, grid.map[x][y])
        return val

    def decision(self, grid):

        parent = Node()
        parent.grid = deepcopy(grid)
        child, utility = self.maximize(parent)

        return child.move


class Node:
    ''' Node data structure '''
    def __init__(self, parent=None):
        self.grid = None
        self.parent = parent
        self.move = () # the move that led to current grid config
        self.move_str = ''
        self.children = []

        if not self.parent:
            self.depth = 0  # move number ahead of current play
        self.utility = 0

    def successors(self, player):
        ''' possible states for each player turn '''

        if player == 1:
            # Create new states of each avaible move
            moves = self.grid.getAvailableMoves()

            for move in moves:
                grid = deepcopy(self.grid)
                if grid.canMove([move]):
                    grid.move(move)
                    child = Node(self)
                    child.grid = grid
                    child.depth = self.depth + 1
                    child.move_str = actionDic[move]
                    child.move = move
                    self.children.append(child)

        if player == 2:  # MIN
            # Randomly insert a 2 or 4 tile in the grid

            cells = self.grid.getAvailableCells()

            for cell in cells:
                grid = deepcopy(self.grid)

                if grid.canInsert(cell):
                    new_tile = random.choice([2, 4])
                    grid.setCellValue(cell, new_tile)

                    child = Node(self)
                    child.grid = grid
                    child.depth = self.depth + 1
                    self.children.append(child)

            return self.children
