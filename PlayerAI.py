from random import randint
from BaseAI import BaseAI
from copy import deepcopy
import random
import logging


actionDic = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}


class PlayerAI(BaseAI):

    def __init__(self):
        self.max_thinking_depth = 3
        logging.basicConfig(filename='log.log', level=logging.DEBUG)
        self.nodes_expanded_max = 0
        self.nodes_expanded_min = 0

    def getMove(self, grid):

        moves = grid.getAvailableMoves()
        return self.decision(grid)
        #return moves[randint(0, len(moves) - 1)] if moves else None

    def minimize(self, node, alpha=0, beta=0):
        ''' Find the child with the lowest utility value '''

        if self.terminal(node):
            return (node, self.evaluate(node, 2))

        min_child, min_utility = (node, float("inf"))
        #logging.info('Min Node depth: %d move %d parent %s' %(node.depth, node.move, node.parent))
        node.successors(2)
        self.nodes_expanded_min += len(node.children)

        for child in node.children:
            _child, utility = self.maximize(child, alpha, beta)
            #min_child = _child

            if min_utility > utility:
                min_utility = utility
                min_child = child

            #alpha-beta pruning
            if min_utility <= alpha:
                break

            if min_utility < beta:
                beta = min_utility

        return (min_child, min_utility)

    def maximize(self, node, alpha=0, beta=0):
        ''' Find the child with the highest utility value '''

        if self.terminal(node):
            #logging.info('Node depth %d ' % node.depth)
            return (node, self.evaluate(node, 1))

        max_child, max_utility = (node, -float("inf"))
        #logging.info('Max Node depth: %d move %s parent %s' %(node.depth, node.move, node.parent))
        node.successors(1)
        self.nodes_expanded_max += len(node.children)

        for child in node.children:
            if child.move == -1 :
                logging.info('INvalid child move in {} - MAX'.format(child))
            _child, utility = self.minimize(child, alpha, beta)
            #logging.info('Terminal Node Depth: %d grid:%s' % (_child.depth, _child.grid))
            #max_child = _child

            if max_utility < utility:
                #logging.info('Current max utility: %d' % utility)
                max_utility = utility
                max_child = child

            # alpha beta pruning implementation
            if max_utility >= beta:
                break

            if max_utility > alpha:
                alpha = max_utility

        if not max_child:
            logging.info('Max child is null ...parent child nodes {}'.format(node.children))
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
        #return val
        logging.info("Max tile : %d for Player %d " %( node.grid.getMaxTile(), player))
        return node.grid.getMaxTile()

    def get_min_value(self, grid):
        val = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                val = min(val, grid.map[x][y])
        return val

    def decision(self, grid):

        parent = Node()
        parent.grid = deepcopy(grid)
        child, utility = self.maximize(parent, -float('inf'), float('inf'))

        if not child:
            logging.error('Move : %s  state %s parent move %s' %( child.move, child.grid.map, child.parent.move ))
            #return randint(0,4)

        logging.info('Expanded nodes by MAX %d by MIN %d' %( self.nodes_expanded_max, self.nodes_expanded_min))
        return child.move


class Node:
    ''' Node data structure '''
    def __init__(self, parent=None):
        self.grid = None
        self.parent = parent
        self.move = 2  # the move that led to current grid config
        self.move_str = ''
        self.children = []

        if not self.parent:
            self.depth = 0  # move number ahead of current play
        else:
            self.depth = parent.depth + 1

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
                    # child.depth = self.depth + 1
                    #child.move_str = actionDic[move
                    #logging.info('Max move {}'.format(move))
                    child.move = move
                    self.children.append(child)

        if player == 2:  # MIN
            # Randomly insert a 2 or 4 tile in the grid

            cells = self.grid.getAvailableCells()

            for cell in cells:
                grid = deepcopy(self.grid)

                if grid.canInsert(cell):
                    possible_tiles = [2, 4]

                    if randint(0, 99) < 100 * 0.9:
                        new_tile = possible_tiles[0]
                    else:
                        new_tile = possible_tiles[1]
                    # new_tile = random.choice([2, 4])
                    grid.setCellValue(cell, new_tile)

                    child = Node(self)
                    child.grid = grid
                    child.move = cell
                    #logging.info('Min move {}'.format(cell))
                    #child.depth = self.depth + 1
                    self.children.append(child)

            return self.children
