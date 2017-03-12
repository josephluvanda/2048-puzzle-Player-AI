from random import randint
from BaseAI import BaseAI
from copy import deepcopy
import random
import logging
import time


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
        ''' Returns terminal node evaluation value '''
        val = 0

        # heuristics
        ws = weighted_sum(node.grid)
        ms = monotic_score(node.grid)
        ets =  empty_tiles_score(node.grid)
        val = ets - ws + ms
        return val

    def get_min_value(self, grid):
        val = 0
        for x in xrange(grid.size):
            for y in xrange(grid.size):
                val = min(val, grid.map[x][y])
        return val

    def decision(self, grid):
        # Best of the worst. Find a move with lowest outcome penalty
        parent = Node()
        parent.grid = deepcopy(grid)
        start_time = time.clock()

        child, utility = self.maximize(parent, -float('inf'), float('inf'))

        if not child:
            logging.error('Move : %s  state %s parent move %s' %( child.move, child.grid.map, child.parent.move ))

        logging.info('Expanded nodes by MAX %d by MIN %d' %( self.nodes_expanded_max, self.nodes_expanded_min))
        logging.info('Elapsed Time :%fs' % ( time.clock() - start_time ))
        return child.move


def weighted_sum(grid):
    ''' ws = w1f1 + w2f2 .... wnfn'''
    prob = {2: 0.9, 4: 0.1}
    ws = 0
    for x in xrange(grid.size):
        for y in xrange(grid.size):
            val = grid.map[x][y]
            if val == 2 or val == 4:
                ws += prob[val] * val
    #logging.info("Weighted sum : %d" % ws)
    return ws


def empty_tiles_score(grid):
    ''' Assign score points according to number of empty cell in a grid '''
    val = 0
    points = 10
    total = 0
    for x in xrange(grid.size):
        for y in xrange(grid.size):
            val += grid.map[x][y]
            if val == 0:
                val += points
    return total


def monotic_score(grid):
    ''' Score points to number of adjacent cells with identical values '''
    points = 10
    total = 0

    for x in xrange(grid.size):
        for y in xrange(grid.size):
            val = grid.map[x][y]
            # Left comparison
            if y - 1 >= 0 and grid.map[x][y-1] == val:
                total += points
            # Right comparison
            if y + 1 < grid.size and grid.map[x][y+1] == val:
                total += points
            # Up comparison
            if x - 1 >= 0 and grid.map[x-1][y] == val:
                total += points
            # Down comparison
            if x + 1 < grid.size and grid.map[x+1][y] == val:
                total += points
    return total



class Node:
    ''' Node data structure '''
    def __init__(self, parent=None):
        self.grid = None
        self.parent = parent
        self.move = 2  # the move that led to current grid config
        self.children = []

        if not self.parent:
            self.depth = 0  # move number ahead of current play
        else:
            self.depth = parent.depth + 1

    def sort_moves(self, moves):
        # move ordering
        # favor DLRU order
        order = [1, 2, 3, 0]
        return sorted(moves, key=lambda d: order.index(d))

    def successors(self, player):
        ''' possible states for each player turn '''

        if player == 1:
            # Create new states of each avaible move
            moves = self.grid.getAvailableMoves()
            #logging.info('Unorder moves :{}'.format(moves))

            #moves = self.sort_moves(moves)

            for move in moves:
                grid = deepcopy(self.grid)
                if grid.canMove([move]):
                    grid.move(move)
                    child = Node(self)
                    child.grid = grid
                    # logging.info('Max move {}'.format(move))
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
                    self.children.append(child)

            return self.children
