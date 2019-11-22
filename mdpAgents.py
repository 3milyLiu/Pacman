# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import time

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        #print "Starting up MDPAgent!"
        name = "Pacman"
        # Store values
        self.mapCoords = []
        self.mapDictionary = {}
        self.pathCoords = []

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        #print "Running registerInitialState for MDPAgent!"
        #print "I'm at:"
        #print api.whereAmI(state)
        self.makeMap(state)

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"
        self.mapCoords = []
        self.mapDictionary = {}
        self.pathCoords = []

    # Makes a map of the grid
    def makeMap(self, state):
        corners = api.corners(state)
        walls = api.walls(state)
        xAxis = []
        yAxis = []
        for corner in corners:
            xAxis.append(corner[0])
            yAxis.append(corner[1])

        # maximum X and Y for the map
        maxX = max(xAxis)
        maxY = max(yAxis)

        # create grid
        for x in range (maxX + 1):
            for y in range (maxY + 1):
                if (x,y) not in self.mapCoords:
                    self.mapCoords.append((x,y))
        # all coords that are not wall
        for i in self.mapCoords:
            if i not in walls and i not in self.pathCoords:
                self.pathCoords.append(i)

    # Updates the map
    # ghosts, state of ghosts, capsules, food and walls
    def updateMap(self, state):
        ghost = api.ghosts(state)
        ghostStates = api.ghostStates(state)
        capsule = api.capsules(state)
        food = api.food(state)
        wall = api.walls(state)

        for node in self.mapDictionary:
            if node in wall:
                self.mapDictionary.update({node: 'X'})

        return self.mapDictionary

    # This function calls the legalActions API and returns if the move is legal
    def getAction(self, state):
        if not self.mapDictionary:
            for coords in self.mapCoords:
                self.mapDictionary.update({coords:0})

        self.updateMap(state)
        mD = self.mapDictionary
        self.compute(state, mD)
        direction = self.optimalPolicy(state, mD)
        legal = api.legalActions(state)
        if direction == 'northP':
            return api.makeMove('North', legal)
        if direction == 'eastP':
            return api.makeMove('East', legal)
        if direction == 'southP':
            return api.makeMove('South', legal)
        if direction == 'westP':
            return api.makeMove('West', legal)

    # Function takes co-ordinates and returns the maximum expected utility for it
    # used for value iteration later
    def expectedUtitlity(self, mapDictionary, x, y):
        # dictionary to hold expected utility
        self.utilDictionary = {
        'northMEU' : 0,
        'eastMEU' : 0,
        'southMEU' : 0,
        'westMEU' : 0}
        x = int(x)
        y = int(y)
        north = (x, y + 1)
        east = (x + 1, y)
        south = (x, y - 1)
        west = (x - 1, y)
        stop = (x, y)

        # Direction pacman is currently facing 0.8
        # To the right of pacman 0.1
        # To the left of pacman 0.1
        mDstop = 0.1 * self.mapDictionary[stop]
        # if north is not wall x MEU else MEU of staying there
        # if other directions are not walls x MEU of those else MEU of staying there
        if self.mapDictionary[north] != 'X':
            self.utilDictionary['northMEU'] = 0.8 * self.mapDictionary[north]
        else:
            self.utilDictionary['northMEU'] = 0.8 * self.mapDictionary[stop]
        if self.mapDictionary[east] != 'X':
            self.utilDictionary['northMEU'] += 0.1 * self.mapDictionary[east]
        else:
            self.utilDictionary['northMEU'] += mDstop
        if self.mapDictionary[west] != 'X':
            self.utilDictionary['northMEU'] += 0.1 * self.mapDictionary[west]
        else:
            self.utilDictionary['northMEU'] += mDstop

        if self.mapDictionary[east] != 'X':
            self.utilDictionary['eastMEU'] = 0.8 * self.mapDictionary[east]
        else:
            self.utilDictionary['eastMEU'] = 0.8 * self.mapDictionary[stop]
        if self.mapDictionary[north] != 'X':
            self.utilDictionary['eastMEU'] += 0.1 * self.mapDictionary[north]
        else:
            self.utilDictionary['eastMEU'] += mDstop
        if self.mapDictionary[south] != 'X':
            self.utilDictionary['eastMEU'] += 0.1 * self.mapDictionary[south]
        else:
            self.utilDictionary['eastMEU'] += mDstop

        if self.mapDictionary[south] != 'X':
            self.utilDictionary['southMEU'] = 0.8 * self.mapDictionary[south]
        else:
            self.utilDictionary['southMEU'] = 0.8 * self.mapDictionary[stop]
        if self.mapDictionary[east] != 'X':
            self.utilDictionary['southMEU'] += 0.1 * self.mapDictionary[east]
        else:
            self.utilDictionary['southMEU'] += mDstop
        if self.mapDictionary[west] != 'X':
            self.utilDictionary['southMEU'] += 0.1 * self.mapDictionary[west]
        else:
            self.utilDictionary['southMEU'] += mDstop

        if self.mapDictionary[west] != 'X':
            self.utilDictionary['westMEU'] = 0.8 * self.mapDictionary[west]
        else:
            self.utilDictionary['westMEU'] = 0.8 * self.mapDictionary[stop]
        if self.mapDictionary[north] != 'X':
            self.utilDictionary['westMEU'] += 0.1 * self.mapDictionary[north]
        else:
            self.utilDictionary['westMEU'] += mDstop
        if self.mapDictionary[south] != 'X':
            self.utilDictionary['westMEU'] += 0.1 * self.mapDictionary[south]
        else:
            self.utilDictionary['westMEU'] += mDstop

        self.mapDictionary[(x, y)] = max(self.utilDictionary.values())
        return self.mapDictionary[(x, y)]

    # MEU function is applied to the whole grid
    # iterates until convergence
    def compute(self, state, Dictionary):
        ghost = api.ghosts(state)
        ghostStates = api.ghostStates(state)
        capsule = api.capsules(state)
        food = api.food(state)
        wall = api.walls(state)

        # 1 ghost
        if len(ghost) == 1:
            # ghost co-ordinates and its states
            ghost1x = int(ghostStates[0][0][0])
            ghost1y = int(ghostStates[0][0][1])
            ghost1xy = (ghost1x, ghost1y)
            ghost1State = ghostStates[0][1]
            doNotEnter = []
            if ghost1State == 0:
                for i in range(1, 2):
                    if (ghost1x + i, ghost1y) in self.mapCoords:
                        doNotEnter.append((ghost1x +  i, ghost1y))
                    if (ghost1x - i, ghost1y) in self.mapCoords:
                        doNotEnter.append((ghost1x + i, ghost1y))
                    if (ghost1x, ghost1y + i) in self.mapCoords:
                        doNotEnter.append((ghost1x, ghost1y + i))
                    if (ghost1x, ghost1y - i) in self.mapCoords:
                        doNotEnter.append((ghost1x, ghost1y - i))

            #rewards and penalty
            ghostPenalty = -500
            capsuleReward = 10
            foodReward = 10
            safeGhost = 10
            noReward = 0
            doNotEnterPenalty = -500
            discountFactor = 0.7
            iterations = 50
            while iterations > 0:
                # a copy of the map, values are stored between iterations
                copy = Dictionary.copy()
                for x, y in Dictionary:
                    #value iteration
                    if (x, y) in self.pathCoords and (x, y) == ghost1xy and ghost1State == 0:
                        Dictionary[(x, y)] = ghostPenalty + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) == ghost1xy and ghost1State == 1:
                        Dictionary[(x, y)] = safeGhost + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) in doNotEnter:
                        Dictionary[(x,y)] = doNotEnterPenalty + discountFactor * self.expectedUtitlity(copy, x, y)
                    elif (x, y) in self.pathCoords and (x, y) not in food and (x, y) not in ghost and (x, y) not in capsule:
                        Dictionary[(x, y)] = noReward + discountFactor * self.expectedUtitlity(copy, x, y)
                    elif (x, y) in self.pathCoords and (x, y) in capsule:
                        Dictionary[(x, y)] = capsuleReward + discountFactor * self.expectedUtitlity(copy, x, y)
                    elif (x, y) in self.pathCoords and (x, y) in food:
                        Dictionary[(x, y)] = foodReward + discountFactor * self.expectedUtitlity(copy, x, y)
                iterations -= 1

        # 2 ghosts
        if len(ghost) == 2:
            # ghost co-ordinates and its states
            ghost1x = int(ghostStates[0][0][0])
            ghost1y = int(ghostStates[0][0][1])
            ghost1xy = (ghost1x, ghost1y)
            ghost1State = ghostStates[0][1]
            ghost2x = int(ghostStates[1][0][0])
            ghost2y = int(ghostStates[1][0][1])
            ghost2xy = (ghost2x, ghost2y)
            ghost2State = ghostStates[1][1]
            doNotEnter = []
            if ghost1State == 0:
                for i in range (1, 3):
                    if (ghost1x + i, ghost1y) in self.pathCoords:
                        doNotEnter.append((ghost1x + i, ghost1y))
                    if (ghost1x - i, ghost1y) in self.pathCoords:
                        doNotEnter.append((ghost1x - i, ghost1y))
                    if (ghost1x, ghost1y + i) in self.pathCoords:
                        doNotEnter.append((ghost1x, ghost1y + i))
                    if (ghost1x, ghost1y - i) in self.pathCoords:
                        doNotEnter.append((ghost1x, ghost1y - i))

            #rewards and penalty
            ghostPenalty = -500
            capsuleReward = 10
            foodReward = 10
            safeGhost = 10
            noReward = 0
            doNotEnterPenalty = -500
            discountFactor = 0.7
            iterations = 50
            # value iteration
            while iterations > 0:
                copy = Dictionary.copy()
                for x, y in Dictionary:
                    if (x, y) in self.pathCoords and (x, y) == ghost1xy and ghost1State == 0:
                        Dictionary[(x, y)] = ghostPenalty + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) == ghost2xy and ghost2State == 0:
                        Dictionary[(x, y)] = ghostPenalty + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) == ghost1xy and ghost1State == 1:
                        Dictionary[(x, y)] = safeGhost + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) == ghost2xy and ghost2State == 1:
                        Dictionary[(x, y)] = safeGhost + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) in doNotEnter:
                        Dictionary[(x, y)] = doNotEnterPenalty + discountFactor * self.expectedUtitlity(copy, int(round(x)), int(round(y)))
                    elif (x, y) in self.pathCoords and (x, y) in capsule:
                        Dictionary[(x, y)] = capsuleReward + discountFactor * self.expectedUtitlity(copy, x, y)
                    elif (x, y) in self.pathCoords and (x, y) in food:
                        Dictionary[(x, y)] = foodReward + discountFactor * self.expectedUtitlity(copy, x, y)
                    elif (x, y) in self.pathCoords and (x, y) not in food and (x, y) not in capsule and (x, y) not in ghost:
                        Dictionary[(x, y)] = noReward + discountFactor * self.expectedUtitlity(copy, x, y)
                iterations -= 1

    # returns the best move
    def optimalPolicy(self, state, optimal):
        whereAmI = api.whereAmI(state)
        #dictionary hold utility
        self.utility = {
        'northP': 0,
        'eastP': 0,
        'southP': 0,
        'westP': 0}
        #moves x y
        north = (whereAmI[0], whereAmI[1] + 1)
        east = (whereAmI[0] + 1, whereAmI[1])
        south = (whereAmI[0], whereAmI[1] - 1)
        west = (whereAmI[0] - 1, whereAmI[1])
        stop = whereAmI
        # Direction pacman is currently facing 0.8
        # To the right of pacman 0.1
        # To the left of pacman 0.1
        mDstop1 = 0.1 * self.mapDictionary[stop]
        mDStop8 = 0.8 *self.mapDictionary[stop]
        # if north is not wall x MEU else MEU of staying there
        # if other directions are not walls x MEU of those else MEU of staying there
        if self.mapDictionary[north] != 'X':
            self.utility['northP'] = 0.8 * self.mapDictionary[north]
        else:
            self.utility['northP'] = mDStop8
        if self.mapDictionary[east] != 'X':
            self.utility['northP'] += 0.1 * self.mapDictionary[east]
        else:
            self.utility['northP'] += mDstop1
        if self.mapDictionary[west] != 'X':
            self.utility['northP'] += 0.1 * self.mapDictionary[west]
        else:
            self.utility['northP'] += mDstop1

        if self.mapDictionary[east] != 'X':
            self.utility['eastP'] = 0.8 * self.mapDictionary[east]
        else:
            self.utility['eastP'] = mDStop8
        if self.mapDictionary[north] != 'X':
            self.utility['eastP'] += 0.1 * self.mapDictionary[north]
        else:
            self.utility['eastP'] += mDstop1
        if self.mapDictionary[south] != 'X':
            self.utility['eastP'] += 0.1 * self.mapDictionary[south]
        else:
            self.utility['eastP'] += mDstop1

        if self.mapDictionary[south] != 'X':
            self.utility['southP'] = 0.8 * self.mapDictionary[south]
        else:
            self.utility['southP'] = mDStop8
        if self.mapDictionary[east] != 'X':
            self.utility['southP'] += 0.1 * self.mapDictionary[east]
        else:
            self.utility['southP'] += mDstop1
        if self.mapDictionary[west] != 'X':
            self.utility['southP'] += 0.1 * self.mapDictionary[west]
        else:
            self.utility['southP'] += mDstop1

        if self.mapDictionary[west] != 'X':
            self.utility['westP'] = 0.8 * self.mapDictionary[west]
        else:
            self.utility['westP'] = mDStop8
        if self.mapDictionary[north] != 'X':
            self.utility['westP'] += 0.1 * self.mapDictionary[north]
        else:
            self.utility['westP'] += mDstop1
        if self.mapDictionary[south] != 'X':
            self.utility['westP'] += 0.1 * self.mapDictionary[south]
        else:
            self.utility['westP'] += mDstop1
        # hgihest MEU move
        return max(self.utility, key = self.utility.get)
