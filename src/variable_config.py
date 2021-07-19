import pygame as pg
from pygame import Color
from pygame.locals import *

#--------------------------------------------------------
# Runtime variables
#--------------------------------------------------------
# Simulation FPS
FPS_LIST = [1,2,5,10,25,60,100,150,1000]
FPS_SELECTION = 8 # Index corresponding to available option from FPS_LIST
DEFAULT_FPS_SELECTION = 4

# Simulation Skip Frame Number
SKIP_LIST = [0,5,10,20]
SKIP_SELECTION = 0 # Index corresponding to available option from SKIP_LIST
DEFAULT_SKIP_SELECTION = 4

# Selects a new agent automatically if the currently selected agent is removed from the simulation
SIMULATION_RUNNER_ALWAYS_HAVE_SELECTED_AGENT = True

# Render width and height
RENDER_WIDTH = 500
RENDER_HEIGHT = 700

# Window width and height
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000

# How many tiles should the grid have horizontally and vertically?
# CURRENTLY ALL GRIDS MUST BE SQUARE
GAME_GRID_WIDTH = 20
GAME_GRID_HEIGHT = GAME_GRID_WIDTH

# Total number of spaces 
NUM_SPACES = GAME_GRID_WIDTH * GAME_GRID_HEIGHT

# Not currently used.
SMELL_PROPAGATION_DISTANCE = GAME_GRID_WIDTH

# How much energy is spent moving from tile to tile
DEFAULT_TERRAIN_DIFFICULTY = 1

# Should food smell stack, or take the greatest value?
# Glitches can occur if this is turned off
SCENT_STACKING = True

# Does a round's score go down to zero if the player dies?
DEATH_PENALTY = True

# Self explanatory
BACKGROUND_COLOR = Color("#505050")
PAUSED_BACKGROUND_COLOR = Color("#303030")
NUM_AGENTS = 20
NUM_EVIL = 5
SMELL_DIST = 10

# What is the maximum amount of energy that a player can have?
MAX_ENERGY = GAME_GRID_WIDTH * 5

# The number of food pieces that will spawn each time there is no food
# on the grid.
MAX_NUM_FOOD_ON_GRID = int(NUM_SPACES / 20)

# Used to determine how many frames are skipped.
# Helps when you want the gamelogic to move faster than
# Your system can draw it.
SKIP_FRAMES = 0

# Determine if agents shouldn't be able to see further than they can smell; 
#  If True, only go off the scent matrix
SKIP_SIGHT = False

# How much food needs to be found before a round ends?
FOOD_PER_ROUND = MAX_NUM_FOOD_ON_GRID * 5

# What is the maximum amount of health that a player can have?
MAX_HEALTH = 100

MAX_GAME_STATES = 200

# When paused, allows to step through previously processed game states 
#  (up to MAX_GAME_STATES)
SAVE_STATES = True

# Render each agent's turn instead of the collective tick
TURN_VIEW = False

# Maximum number of game states that can be saved per round
MAX_SAVED_GAME_STATES = MAX_ENERGY

# Defines how smart the non-student agents are.
# A value between 0 and 1, where a lower value means the 
# agent will make a good choice less often
DEFAULT_INTELLIGENCE = 0.2

# Same as above, fut only applies to evil agents
DEFAULT_EVIL_INTELLIGENCE = 0.5

# Indicates whether or not it takes time to consume a plant
EAT_PLANT_INSTANT = False

# Indicates how much food needs to be eaten by the agent after it is pregnant
PREGNANCY_FOOD_GOAL = 50

# Indicates how old an agent must be before they're able to become pregnant &/or procreate
AGE_OF_CONSENT = 100

# Indicates period of time between pregnancies/procreation
PREGNANCY_COOLDOWN = 100

# Logging verbosity via STDOUT/STDERR
VERBOSE = True
#--------------------------------------------------------

#--------------------------------------------------------
# UNMODIFIABLE (simulation predicated upon these initial values to work)
#--------------------------------------------------------
SQUARE_SIZE = int(RENDER_WIDTH/GAME_GRID_WIDTH*0.8)

if MAX_NUM_FOOD_ON_GRID <= 1:
    MAX_NUM_FOOD_ON_GRID = 1
    
SIMULATION_RUNNER_PAUSED = False
SIMULATION_RUNNER_PAUSE_LOCK = False
SIMULATION_RUNNER_TERMINATING = False
SIMULATION_RUNNER_SIGNAL_REDRAW = False
SIMULATION_RUNNER_EXCEPTION_CAUGHT = False

selected_id = None

clock = pg.time.Clock()
delta_time = 0
#--------------------------------------------------------