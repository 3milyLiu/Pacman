# sampleAgents.py
# parsons/07-oct-2017
#
# Version 1.1
#
# Some simple agents to work with the PacMan AI projects from:
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

# RandomAgent
#
# A very simple agent. Just makes a random pick every time that it is
# asked for an action.
class RandomAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)

# RandomishAgent
#
# A tiny bit more sophisticated. Having picked a direction, keep going
# until that direction is no longer possible. Then make a random
# choice.
class RandomishAgent(Agent):

    # Constructor
    #
    # Create a variable to hold the last action
    def __init__(self):
         self.last = Directions.STOP

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        # If we can repeat the last action, do it. Otherwise make a
        # random choice.
        if self.last in legal:
            return api.makeMove(self.last, legal)
        else:
            pick = random.choice(legal)
            # Since we changed action, record what we did
            self.last = pick
            return api.makeMove(pick, legal)

# SensingAgent
#
# Doesn't move, but reports sensory data available to Pacman
class SensingAgent(Agent):

    def getAction(self, state):

        # Demonstrates the information that Pacman can access about the state
        # of the game.

        # What are the current moves available
        legal = api.legalActions(state)
        print "Legal moves: ", legal

        # Where is Pacman?
        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        # Where are the ghosts?
        print "Ghost positions:"
        theGhosts = api.ghosts(state)
        for i in range(len(theGhosts)):
            print theGhosts[i]

        # How far away are the ghosts?
        print "Distance to ghosts:"
        for i in range(len(theGhosts)):
            print util.manhattanDistance(pacman,theGhosts[i])

        # Where are the capsules?
        print "Capsule locations:"
        print api.capsules(state)

        # Where is the food?
        print "Food locations: "
        print api.food(state)

        # Where are the walls?
        print "Wall locations: "
        print api.walls(state)

        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are.
        return api.makeMove(Directions.STOP, legal)

# GoWestAgent
#
# Always tries to have Pacman go west on the grid when it is possible.
class GoWestAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.WEST in legal:
            return api.makeMove(Directions.WEST, legal)
        else:
            if Directions.STOP in legal:
                legal.remove(Directions.STOP)
            # Random choice between the legal options.
            return api.makeMove(random.choice(legal), legal)

# HungryAgent
#
# Uses information about the location of the food to try to move towards the
# nearest food.
class HungryAgent( Agent ):

    def getAction( self, state ):
        legal = api.legalActions( state )
        if Directions.STOP in legal:
            legal.remove( Directions.STOP )

        successors = [ ( state.generateSuccessor( 0, action ), action ) for action in legal ]
        scored = []
        for state, action in successors:
            score, dist = self.foodScore( state )
            scored.append( (score, dist, action) )
        bestScore = min( scored )[ 0 ]
        bestActions = [ tp[1:] for tp in scored if tp[0] == bestScore ]
        return sorted( bestActions, key = lambda x: x[0] )[ 0 ][ 1 ]

    def foodScore( self, state ):
        dist, food = self.nearestFood( state )
        return len( api.food( state ) ), dist

    def nearestFood( self, state ):
        pacman = api.whereAmI( state )
        foodMap = api.food( state )
        if foodMap:
            distances = [ abs( (x - pacman[ 0 ] ) ) + abs( ( y - pacman[ 1 ] ) ) for ( x, y ) in foodMap  ]
            return min( zip( distances, foodMap ) )
        else:
            return ( 0, ( 0, 0 ) )

# SurvivalAgent
#
# Uses the location of Pacman and the ghosts (and any other information that
# may be helpful) to stay alive as long as possible.
class SurvivalAgent( Agent ):

    def getAction( self, state ):
        legal = api.legalActions( state )
        if Directions.STOP in legalMoves:
            legal.remove( Directions.STOP )

        successors = [ ( state.generateSuccessor( 0, action ), action ) for action in legal ]
        scores = [ (self.ghostScore( api.whereAmI( state), api.ghosts( state)), action) for state, action in successors ]
        bestScore = max( scores )[ 0 ]
        bestActions = [ pair[ 1 ] for pair in scores if pair[ 0 ] == bestScore]
        return random.choice( bestActions )

    def ghostScore( self, pacman, ghosts ):
        return min( [ util.manhattanDistance( pacman, ghost ) for ghost in ghosts ] )

class CornerSeekingAgent(Agent):

    def __init__(self):
         self.BL = False
         self.TL = False
         self.BR = False
         self.TR = False

    def final(self, state):
         self.BL = False
         self.TL = False
         self.BR = False
         self.TR = False

    def getAction(self, state):

        # Get extreme x and y values for the grid
        corners = api.corners(state)
        print corners
        # Setup variable to hold the values
        minX = 100
        minY = 100
        maxX = 0
        maxY = 0

        # Sweep through corner coordinates looking for max and min
        # values.
        for i in range(len(corners)):
            cornerX = corners[i][0]
            cornerY = corners[i][1]

            if cornerX < minX:
                minX = cornerX
            if cornerY < minY:
                minY = cornerY
            if cornerX > maxX:
                maxX = cornerX
            if cornerY > maxY:
                maxY = cornerY

        legal = api.legalActions(state)
        print legal
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        pacman = api.whereAmI(state)
        #print pacman

        # bottom left corner
        # check
        if pacman[0] == minX + 1:
            if pacman[1] == minY + 1:
                print "Got to BL!"
                self.BL = True

        # bottom left corner. West then south
        if self.BL == False:
            if pacman[0] > minX + 1:
                if Directions.WEST in legal:
                    return api.makeMove(Directions.WEST, legal)
                else:
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)
            else:
                if Directions.SOUTH in legal:
                    return api.makeMove(Directions.SOUTH, legal)
                else:
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)

        # top left corner
        # check
        if pacman[0] == minX + 1:
           if pacman[1] == maxY - 1:
                print "Got to TL!"
                self.TL = True

        # top left corner. West then North.
        if self.TL == False:
            if pacman[0] > minX + 1:
                if Directions.WEST in legal:
                    return api.makeMove(Directions.WEST, legal)
                else:
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)
            else:
                if Directions.NORTH in legal:
                    return api.makeMove(Directions.NORTH, legal)
                else:
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)

        # top right corner
        # check
        if pacman[0] == maxX - 1:
           if pacman[1] == maxY - 1:
                print "Got to TR!"
                self.TR = True

        # top right corner. East then north
        if self.TR == False:
            if pacman[0] < maxX - 1:
                if Directions.EAST in legal:
                    return api.makeMove(Directions.EAST, legal)
                else:
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)
            else:
                if Directions.NORTH in legal:
                    return api.makeMove(Directions.NORTH, legal)
                else:
                    pick = random.choice(legal)
                    return api.makeMove(pick, legal)

        # bottom right corner (south)
        if pacman[0] == maxX - 1:
           if pacman[1] == minY + 1:
                print "Got to BR!"
                self.BR = True
                return api.makeMove(Directions.STOP, legal)
           else:
               print "Nearly there"
               return api.makeMove(Directions.SOUTH, legal)

        print "Not doing anything!"
        return api.makeMove(Directions.STOP, legal)
