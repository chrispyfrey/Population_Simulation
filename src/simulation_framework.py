import pygame as pg
from pygame.font import Font
import numpy as np
import random
import sys
from os import path
from PIL import Image, ImageFilter
from variable_config import *
#import time
from enum import Enum
from math import sqrt
import traceback
import pickle
#import dill

#random.seed(99)

# Initialize pygame.
#pg.init()

# Get the current path of the python file. Used to load a font resource.
ABS_PATH = path.dirname(path.realpath(__file__))

EXCEPTION_CAUGHT = False

AGENT_ID = 0

HANDLED_TICK = 0

class ObjectType(Enum):
    PLANT = 0
    EVIL = 1
    NEUTRAL = 2
    PREGNANT = 3
    BABY = 4
   
def draw_outline(pg_font, desired_text, x, y, surface):
    surface.blit(pg_font.render(desired_text, 0, (0, 0, 0)), (x-1, y))
    surface.blit(pg_font.render(desired_text, 0, (0, 0, 0)), (x+1, y))
    surface.blit(pg_font.render(desired_text, 0, (0, 0, 0)), (x, y-1))
    surface.blit(pg_font.render(desired_text, 0, (0, 0, 0)), (x, y+1))
    
def fast_dist(x1,y1,x2,y2):
    return np.linalg.norm(np.array((x1,y1))-np.array((x2,y2)))

def dir2offset(direction):
    difficulty_multiplier = 1
    x = 0
    y = 0
    d = direction
    if d >= 0 and d <= 8:
        if d in [0,1,2]:
            y = -1
        elif d in [3,4,5]:
            y = 0
        else:
            y = 1

        if d in [0,3,6]:
            x = -1
        elif d in [1,4,7]:
            x = 0
        else:
            x = 1

        # Diagonal movements are more costly than cardinal movements
        if x != 0 and y != 0:
            difficulty_multiplier = sqrt(2)
    else:
        print("Invalid direction, staying still")
    return x, y, difficulty_multiplier

# Draw the grid without anything else.
def drawGenericGrid(self,surface,rect,num_x,num_y):

    total_x = rect.width
    total_y = rect.height
    grid_pos_x = rect.x
    grid_pos_y = rect.y
    
    line_width = 1
    square_size = int(rect.width/num_x)
    line_color = pg.Color("#000000")

    for i in range(num_y + 1):
        pg.draw.rect(
                    surface,
                    line_color,
                    pg.Rect(
                        grid_pos_x,
                        grid_pos_y, 
                        1, 
                        total_y)
                )
        grid_pos_x += square_size
        if num_x == 3 and i == 2:
            grid_pos_x += 1

    grid_pos_x = rect.x

    for i in range(num_x + 1):
        pg.draw.rect(
                    surface,
                    line_color,
                    pg.Rect(
                        grid_pos_x,
                        grid_pos_y, 
                        total_x, 
                        1)
                )
        grid_pos_y += square_size
        if num_y == 3 and i == 2:
            grid_pos_y += 1

# A class that allows for the saving and restoring of the game.
class GameState():
    def __init__(self, in_game_manager):
        self.pickled_game_manager = None
        try:
            #dill.detect.trace(False)
            self.pickled_game_manager = pickle.dumps(in_game_manager)
        except Exception as e:
            traceback.print_exc()
            sys.exit(9)

    def restore(self):
        game_manager = None
        try:
           game_manager = pickle.loads(self.pickled_game_manager)
        except Exception as e:
            traceback.print_exc()
            sys.exit(9)
        return game_manager

# class SensoryMatrix:
class GameObject:
    """ TODO: ADD DOCSTRING """
    def __init__(self,x,y,raw_img_path=None,stage=None):
        if raw_img_path == None:
            raw_img_path = path.join(ABS_PATH, "art_assets","ERROR")
        self.type = None
        self.difficulty = DEFAULT_TERRAIN_DIFFICULTY
        self.x = x
        self.y = y
        self.stage = stage
        self.alive = True
        self.raw_img_path = raw_img_path
        self.calc_img_path(raw_img_path)
        self.loadImg(self.img_path)
        self.energy = 0    
        self.max_energy = 100

    def __getstate__(self):
        attributes = self.__dict__.copy()
        del attributes['img']
        del attributes['img_rect']
        return attributes
    
    def __setstate__(self, state):
        #print("Within setstate of GameObject")
        self.__dict__ = state
        self.calc_img_path(self.raw_img_path)
        self.loadImg(self.img_path)
    
    def consume(self,energy):
        self.energy += energy
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def deplete(self,energy):
        self.energy -= energy
        if self.energy <= 0:
            self.die()
    
    def die(self):
        global HANDLED_TICK
        self.alive = False
        self.death_tick = HANDLED_TICK
        
    def loadImg(self, img_path):
        self.img = pg.image.load(img_path)
        self.img = pg.transform.smoothscale(self.img,(SQUARE_SIZE,SQUARE_SIZE))
        self.img_rect = self.img.get_rect()

    def calc_img_path(self, raw_img_path):
        if self.stage is not None:
            img_path = f"{raw_img_path}{self.stage}.png"
        else:
            img_path = f"{raw_img_path}.png"
        if path.exists(img_path):
            self.img_path = img_path
        else:
            print(f"ERROR: FILE NOT FOUND ({img_path})")
            sys.exit(101)

    def move_instant(self,x,y):
        """ Move to a location without using energy """
        self.x = x
        self.y = y

    def move_probabalistic(self, movement_matrix):
        """ Input a 3x3 matrix, pick a direction based on probabilities """

        movement_list = list(range(0,9))
        movement = random.choices(movement_list,weights=movement_matrix.flatten().tolist())
        return movement[0]

    def draw(self,x,y,surface):
        surface.blit(self.img, self.img_rect.move(x,y))

class Plant(GameObject):
    def __init__(self,x=None, y=None):
        self.stage = 1
        self.raw_img_path = path.join(ABS_PATH, "art_assets","plant_growth","plant")
        super().__init__(x,y,self.raw_img_path,stage=self.stage)
        # Probability of growth per round
        self.growth_rate = 0.9
        self.num_stages = 5
        self.max_energy = 100
        self.energy = 10
        self.energy_steps = int(self.max_energy / self.num_stages)

    def tick(self):
        if random.random() < self.growth_rate:
            self.grow()

        new_stage = self.energy2stage()
        if new_stage != self.stage:
            self.stage = new_stage
            self.calc_img_path(self.raw_img_path)
            self.loadImg(self.img_path)

    def grow(self):
        self.energy += 1
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    # Calculate stage based on energy level:
    def energy2stage(self):
        for i in range(self.num_stages+1):
            if self.energy <= i * self.energy_steps:
                return i
        return i

class Agent(GameObject):
    def __init__(self,x=None,y=None,raw_img_path=None,parent_1=None,parent_2=None,stats=None,birth_tick=0):
        global AGENT_ID
        self.sprite_path = path.join(ABS_PATH, "art_assets","agent_faces","neutral")
        if raw_img_path is None:
            self.raw_img_path = path.join(self.sprite_path,"agent_faces")
        else:
            self.raw_img_path = raw_img_path

        super().__init__(x,y,self.raw_img_path)
        if stats == None:
            self.stats = AgentStats(parent_1=parent_1,parent_2=parent_2)
        else:
            self.stats = stats
        self.sense = AgentSense()
        self.movement_choice = 4
        self.max_energy = MAX_ENERGY * ((self.stats.stats["energy"]/self.stats.gene_cap-0.5)+1)
        self.energy = self.max_energy
        self.health = MAX_HEALTH * ((self.stats.stats["health"]/self.stats.gene_cap-0.5)+1)
        self.score = 0
        self.alive = True
        self.type = ObjectType.NEUTRAL
        self.pregnant = -1
        self.id = AGENT_ID
        AGENT_ID += 1
        self.sense.id = self.id
        self.good_choice_chance = DEFAULT_INTELLIGENCE
        self.score = 0
        self.age = 0
        self.mate = None
        self.last_pregnant_age = -PREGNANCY_COOLDOWN
        self.selected = False
        self.is_pregnant = False
        self.mating_cooldown = 0
        self.mating_cooldown_max = 5
        self.children = 0
        self.birth_tick = birth_tick
        self.death_tick = -1
              
    def __setstate__(self, state):
        self.__dict__ = state
        self.calc_color()
        
    def choose_sprite(self):
        def finalize_sprite(old_path):    
            if old_path != self.raw_img_path:
                self.calc_img_path(self.raw_img_path)
                self.calc_color()
      
        if self.raw_img_path:
            old_raw_path = self.raw_img_path
        else:
            old_raw_path = None

        is_baby = self.age < AGE_OF_CONSENT
        self.is_pregnant = self.pregnant > 0
        
        sprite_file_name = "agent_faces"

        if is_baby:
            sprite_file_name += "_baby"
        elif self.is_pregnant:
            sprite_file_name += "_procreation"
        if not self.alive:
            sprite_file_name += "_dead"
            self.raw_img_path = path.join(self.sprite_path,sprite_file_name)
            finalize_sprite(old_raw_path)
            return

        if self.selected:
            sprite_file_name += "_main"
        #elif self.type == ObjectType.EVIL:
            #sprite_file_name += "_evil"
        self.raw_img_path = path.join(self.sprite_path,sprite_file_name)
        finalize_sprite(old_raw_path)
        return

    def consume(self,energy):
        self.energy += energy
        if self.energy > self.max_energy:
            self.energy = self.max_energy
        if self.pregnant >= 0:
            self.pregnant += energy
        
        health_score = self.health/MAX_HEALTH
        if health_score < 0.001:
            health_score = 0.001
        energy_score = self.energy/MAX_ENERGY
        if energy_score < 0.001:
            energy_score = 0.001

        self.score += energy * health_score * energy_score

    def tick(self):
        if self.mating_cooldown > 0:
            self.mating_cooldown -= 1
        if self.energy <= 0 or self.health <= 0:
            self.die()

        if self.selected and self.alive:
            self.heal()
        # if self.type == ObjectType.EVIL:
        #     print(f"EVIL: {self.age}")
        # else:
        #     print(f"GOOD: {self.age}")

    def choose_movement(self):
        move = random.randint(0,8)
        self.good_choice_chance = (self.stats.stats["intelligence"]/self.stats.gene_cap)*0.75
        if random.random() <= self.good_choice_chance:
            smell_list = list(self.sense.food_smell.flatten())
            move = smell_list.index(max(smell_list))
            if sum(smell_list) < 100:
                move = random.randint(0,8)

        return move

    def move(self,x,y,difficulty):
        self.x = x
        self.y = y
        self.energy -= difficulty

    def heal(self):
        if self.health < MAX_HEALTH:
            self.health += 1
            self.deplete(1)
            self.calc_color()

    def die(self):
        global HANDLED_TICK
        # self.raw_img_path = path.join(ABS_PATH, "art_assets","agent_faces","agent_faces_dead")
        # self.calc_img_path(self.raw_img_path)
        # self.loadImg(self.img_path)
        blue = 0
        if self.type == ObjectType.EVIL:
            blue = 255
        self.img.fill(pg.Color(255,0,blue,1),special_flags=pg.BLEND_MIN)
        self.alive = False
        self.death_tick = HANDLED_TICK

    def select(self):
        self.selected = True

    def calc_color(self):
        self.loadImg(self.img_path)
        red_color =  int(255-(255 * (self.health/MAX_HEALTH)))
        if self.health < 0 or red_color > 255:
            red_color = 255
        elif red_color < 0:
            red_color = 0
        
        self.img.fill(pg.Color(255,255-red_color,255-red_color,1),special_flags=pg.BLEND_MIN)

    def take_damage(self, damage):
        hit = damage*(self.stats.stats["endurance"]/self.stats.gene_cap)
        self.health -= hit
        if self.health >= 0:
            self.calc_color()
        else:
            self.die()

        return hit
    
    def draw(self,x,y,surface):
        self.choose_sprite()
        if self.type == ObjectType.EVIL:
            self.img.fill(pg.Color("#AAAAFF"),special_flags=pg.BLEND_MIN)
        surface.blit(self.img, self.img_rect.move(x,y))
        if self.selected:
            self.sense.draw(surface)

    def attempt_mate(self,mate):
        if self.age >= AGE_OF_CONSENT and self.pregnant == -1 and self.mating_cooldown <= 0:
            if mate.id != self.id and mate.type == self.type and mate.is_pregnant == False and mate.alive and mate.age >= AGE_OF_CONSENT:
                #if (target_agent.age - target_agent.last_pregnant_age >= PREGNANCY_COOLDOWN):
                if self.x == mate.x and self.y == mate.y:
                    fertility_score = mate.stats.stats["fertility"] + self.stats.stats["fertility"]  
                    needed = random.randint(0,self.stats.gene_cap*2)
                    if fertility_score >= needed:
                        if VERBOSE:
                            print(f"{self.id} has impregnated {mate.id}!")
                        mate.is_pregnant = True
                        mate.pregnant = 0
                        mate.current_mate = self
                        mate.baby_stats = AgentStats(parent_1=self,parent_2=mate)
                        self.mating_cooldown = self.mating_cooldown_max
    
    def give_birth(self,x,y,g_tick):
        self.is_pregnant = False
        self.pregnant = -1
        self.last_pregnant_age = self.age
        
        
        if (self.type != ObjectType.EVIL):
            if self.mate != None:
                baby = Agent(x, y,stats=self.baby_stats,birth_tick=g_tick)
            else:
                baby = Agent(x, y,parent_1=self,parent_2=self,birth_tick=g_tick)

        else:
            if self.mate != None:
                baby = EvilAgent(x, y,parent_1=self,parent_2=self.mate,birth_tick=g_tick)
            else:
                baby = EvilAgent(x, y,parent_1=self,parent_2=self,birth_tick=g_tick)
        
        self.mate = None
        self.baby_stats = None
        baby.energy = PREGNANCY_FOOD_GOAL
        self.deplete(PREGNANCY_FOOD_GOAL)
        self.children += 1
        if self.mate != None:
            self.mate.children += 1
        return baby

class EvilAgent(Agent):
    def __init__(self,x=None,y=None,parent_1=None,parent_2=None,birth_tick=0):
        self.raw_img_path = None
        super().__init__(x,y,parent_1=parent_1,parent_2=parent_2)
        self.sprite_path = path.join(ABS_PATH, "art_assets","agent_faces","evil")
        self.choose_sprite()
        self.type = ObjectType.EVIL
        self.good_choice_chance = DEFAULT_EVIL_INTELLIGENCE
        self.sense.type = ObjectType.EVIL
        self.max_energy = MAX_ENERGY * 2
        self.energy = self.max_energy
        self.birth_tick = birth_tick
    
    def choose_movement(self):
        move = random.randint(0,8)
        self.good_choice_chance = (self.stats.stats["intelligence"]/self.stats.gene_cap)*0.75
        if random.random() <= self.good_choice_chance:
            smell_list = list(self.sense.creature_smell.flatten())
            move = smell_list.index(max(smell_list))
            if sum(smell_list) < 100:
                move = random.randint(0,8)

        return move

class AgentSense:
    def __init__(self):
        self.sm_font = Font(path.join(ABS_PATH,"Retron2000.ttf"), 11)

        self.sight_dist_from_agent = 2
        self.smell_dist_from_agent = 1

        self.sight_range = self.sight_dist_from_agent * 2 + 1
        self.smell_range = self.smell_dist_from_agent * 2 + 1

        self.reset_sight()
        self.reset_smell()
        
        self.sight_rects = []
        self.smell_rects = []


        self.type = ObjectType.NEUTRAL
        
        for i in range(4):
            sight_rect = pg.Rect(
                            10 + 60 * i,
                            RENDER_HEIGHT - 60,
                            50,
                            50
                            )
            self.sight_rects.append(sight_rect)


        for i in range(2):
            smell_rect = pg.Rect(
                            10 + 60 * 4 + 60 * i,
                            RENDER_HEIGHT - 60,
                            50,
                            50
                            )
            self.smell_rects.append(smell_rect)

    # Reference: https://realpython.com/python-pickle-module/
    def __getstate__(self):
        #print("Within getState of AgentSense")
        attributes = self.__dict__.copy()
        del attributes['sight_rects']
        del attributes['smell_rects']
        del attributes['sm_font']
        return attributes
    
    def __setstate__(self, state):
        #print("Within setstate of AgentSense")
        self.__dict__ = state
        self.sm_font = Font(path.join(ABS_PATH,"Retron2000.ttf"), 11)
        self.sight_rects = []
        for i in range(4):
            sight_rect = pg.Rect(
                            10 + 60 * i,
                            RENDER_HEIGHT - 60,
                            50,
                            50
                            )
            self.sight_rects.append(sight_rect)
        self.smell_rects = []
        for i in range(2):
            smell_rect = pg.Rect(
                            10 + 60 * 4 + 60 * i,
                            RENDER_HEIGHT - 60,
                            50,
                            50
                            )
            self.smell_rects.append(smell_rect)
    
    def reset_sight(self):
        self.elevation_sight = np.zeros((self.sight_range,self.sight_range))
        self.food_sight = np.zeros((self.sight_range,self.sight_range))
        self.creature_sight = np.zeros((self.sight_range,self.sight_range))
        self.danger_sight = np.zeros((self.sight_range,self.sight_range))

    def apply_sight_to_array(self):
        self.sight_senses = []

        self.sight_senses.append(self.elevation_sight)
        self.sight_senses.append(self.food_sight)
        self.sight_senses.append(self.creature_sight)
        self.sight_senses.append(self.danger_sight)

    def apply_smell_to_array(self):
        self.smell_senses = []

        self.smell_senses.append(self.food_smell)
        self.smell_senses.append(self.creature_smell)

    def reset_smell(self):
        self.food_smell = np.zeros((self.smell_range,self.smell_range))
        self.creature_smell = np.zeros((self.smell_range,self.smell_range))
        
    def draw(self, surface):

        if not SKIP_SIGHT:
            draw_outline(self.sm_font, f"Terrain", 10, RENDER_HEIGHT-80, surface)
            surface.blit(self.sm_font.render(f"Terrain", 0, (255, 0, 0)), (10, RENDER_HEIGHT - 80))
            
            draw_outline(self.sm_font, f"Food", 80, RENDER_HEIGHT-80, surface)
            surface.blit(self.sm_font.render(f"Food", 0, (255, 0, 0)), (80, RENDER_HEIGHT - 80))
            
            draw_outline(self.sm_font, f"Agent", 135, RENDER_HEIGHT-80, surface)
            surface.blit(self.sm_font.render(f"Agent", 0, (255, 0, 0)), (135, RENDER_HEIGHT - 80))
            
            draw_outline(self.sm_font, f"Danger", 190, RENDER_HEIGHT-80, surface)
            surface.blit(self.sm_font.render(f"Danger", 0, (255, 0, 0)), (190, RENDER_HEIGHT - 80))

            for i in range(4):
                img = Image.fromarray(self.sight_senses[i]).convert('RGB')
                sense_img = pg.image.fromstring(img.tobytes("raw","RGB"), img.size, img.mode)                
                sense_img = pg.transform.scale(sense_img,(50,50))
                surface.blit(sense_img, self.sight_rects[i])
                drawGenericGrid(self,surface,self.sight_rects[i],5,5)

        draw_outline(self.sm_font, f"Food", 260, RENDER_HEIGHT-80, surface)
        surface.blit(self.sm_font.render(f"Food", 0, (255, 0, 0)), (260, RENDER_HEIGHT - 80))
        
        draw_outline(self.sm_font, f"Agent", 320, RENDER_HEIGHT-80, surface)
        surface.blit(self.sm_font.render(f"Agent", 0, (255, 0, 0)), (320, RENDER_HEIGHT - 80))

        for i in range(2):
            img = Image.fromarray(self.smell_senses[i]).convert('RGB')
            sense_img = pg.image.fromstring(img.tobytes("raw","RGB"), img.size, img.mode)                
            sense_img = pg.transform.scale(sense_img,(50,50))
            surface.blit(sense_img, self.smell_rects[i])
            drawGenericGrid(self,surface,self.smell_rects[i],3,3)


    def flip_matrices(self):
        for i in range(4):
            self.sight_senses[i] = np.rot90(self.sight_senses[i],2) 
            #self.sight_senses[i] = np.fliplr(self.sight_senses[i])
            #self.sight_senses[i] = np.flipud(self.sight_senses[i])
        
    def update(self,x,y,grid,agents,plants):
        if not SKIP_SIGHT:
            self.update_sight(x,y,grid,agents,plants)
        else:
            self.reset_sight()
        self.update_smell(x,y,grid,agents,plants)
        grid_loc_x = 0
        for x_offset in range(-self.smell_dist_from_agent, self.smell_dist_from_agent+1):
            grid_loc_y = 0
            for y_offset in range(-self.smell_dist_from_agent, self.smell_dist_from_agent+1):
                x_new = x + x_offset
                y_new = y + y_offset
                if grid.checkValidTile(x_new,y_new):
                    for agent in agents:
                        if agent.id != self.id:
                            if not (self.type == ObjectType.EVIL and agent.type == ObjectType.EVIL):
                                self.creature_smell[grid_loc_y,grid_loc_x] += (0.5/(fast_dist(x_new,y_new,agent.x,agent.y)+1))*255

                    for plant in plants:
                        self.food_smell[grid_loc_y,grid_loc_x] += (0.5/(fast_dist(x_new,y_new,plant.x,plant.y)+1))*(plant.energy/plant.max_energy)*255

                        
                else:
                    self.creature_smell[grid_loc_y,grid_loc_x] = 0
                    self.food_smell[grid_loc_y,grid_loc_x] = 0
                grid_loc_y += 1
            grid_loc_x += 1
        self.apply_smell_to_array()

    def update_sight(self,x,y,grid,agents,plants):
        self.reset_sight()
        self.reset_smell()

        grid_loc_x = 0
        for x_offset in range(-self.sight_dist_from_agent, self.sight_dist_from_agent+1):
            grid_loc_y = 0
            for y_offset in range(-self.sight_dist_from_agent, self.sight_dist_from_agent+1):
                x_new = x + x_offset
                y_new = y + y_offset
                if grid.checkValidTile(x_new,y_new):
                    self.elevation_sight[grid_loc_y,grid_loc_x] = grid.elevation_map[x_new,y_new]
                    self.creature_sight[grid_loc_y,grid_loc_x] = 128
                    self.danger_sight[grid_loc_y,grid_loc_x] = 128
                    self.food_sight[grid_loc_y,grid_loc_x] = 128

                    for agent in agents:
                        if agent.x == x_new and agent.y == y_new:
                            self.creature_sight[grid_loc_y,grid_loc_x] = 255
                            if agent.type == ObjectType.EVIL:
                                self.danger_sight[grid_loc_y,grid_loc_x] = 255

                    for plant in plants:
                        if plant.x == x_new and plant.y == y_new:
                            self.food_sight[grid_loc_y,grid_loc_x] = 255

                else:
                    self.elevation_sight[grid_loc_y,grid_loc_x] = 255
                    self.creature_sight[grid_loc_y,grid_loc_x] = 0
                    self.danger_sight[grid_loc_y,grid_loc_x] = 0
                    self.food_sight[grid_loc_y,grid_loc_x] = 0

                grid_loc_y += 1
            grid_loc_x += 1
        #TODO: Cleanup this math
        self.apply_sight_to_array()
        #self.flip_matrices()

    def update_smell(self,x,y,grid,agents,plants):
        self.apply_smell_to_array()

class AgentStats:
    def __init__(self,parent_1=None,parent_2=None):
        # All Stats range from 1 to 10
        
        self.gene_avg = 4
        self.gene_cap = 10
        self.gene_min = 1

        self.stats = {}
        self.stats["speed"] = self.gene_min
        self.stats["agility"] = self.gene_min
        self.stats["intelligence"] = self.gene_min
        self.stats["endurance"] = self.gene_min
        self.stats["strength"] = self.gene_min
        self.stats["fertility"] = self.gene_min
        self.stats["bite_size"] = self.gene_min
        self.stats["gene_stability"] = self.gene_min
        self.stats["health"] = self.gene_min
        self.stats["energy"] = self.gene_min
        
        # If GS == 10, only mod by gene_avg
        # If GS == 1, mod gene_avg * 5
        
        self.gene_limit = self.gene_avg*len(self.stats)*self.gene_min
        if parent_1 != None and parent_2 != None:
            self.assignFromParents(parent_1,parent_2)
        else:
            self.scramble_genetics()

        self.cleanGenes()
        self.shiftToCap()
        print(self.stats)

    def getNumMoves(self):
        speed = self.stats["speed"]
        if speed <= 3:
            return 1
        elif speed <= 6:
            return 2
        elif speed <= 9:
            return 3
        return 1

    def assignFromParents(self,parent_1, parent_2):
        for key in self.stats:
            self.stats[key] = (parent_1.stats.stats[key] + parent_2.stats.stats[key])/2
        # genes_to_mod = self.gene_cap/self.stats["gene_stability"]/2 + 1
        genes_to_mod = 10
        amount_to_mod = (self.gene_cap/self.stats["gene_stability"])/self.gene_avg

        for i in range(int(genes_to_mod)):
            self.addToRandGene(amount_to_mod)
            self.subFromRandGene(amount_to_mod)

    def addToRandGene(self,amount):
        key = random.choice(list(self.stats.keys()))
        self.stats[key] += amount

    def subFromRandGene(self,amount):
        key = random.choice(list(self.stats.keys()))
        self.stats[key] -= amount

    def cleanGenes(self):
        for key in self.stats:
            self.stats[key] = round(self.stats[key],3)
            if self.stats[key] < self.gene_min:
                self.stats[key] = self.gene_min
            if self.stats[key] > self.gene_cap:
                self.stats[key] = self.gene_cap

    def shiftToCap(self):
        total = sum(self.stats.values())
        while total > self.gene_limit:
            for key in self.stats:
                self.stats[key] -= 1/len(self.stats)
            total = sum(self.stats.values())
                    
        print(f"TOTAL:{total}")

    def scramble_genetics(self):
        for i in range(self.gene_limit - len(self.stats)):
            key = random.choice(list(self.stats.keys()))
            self.stats[key] += 1

class Grid:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.padding = 1
        self.square_size = int(RENDER_WIDTH/GAME_GRID_WIDTH*0.8)
        self.grid_padding = self.calcGridPadding()
        self.calcGridSize()

        self.occupied_grid = np.zeros((GAME_GRID_WIDTH,GAME_GRID_HEIGHT))
        
        self.default_color = pg.Color("#FFFFFF")
        self.line_color = pg.Color("#010101")
        self.calcHeightMap()

    def __getstate__(self):
        #print("Within getState of Grid")
        attributes = self.__dict__.copy()
        del attributes['default_color']
        del attributes['line_color']
        del attributes['elevation_map_img']
        return attributes
    
    def __setstate__(self, state):
        #print("Within setstate of Grid")
        self.__dict__ = state
        self.default_color = pg.Color("#FFFFFF")
        self.line_color = pg.Color("#010101")
        
        # Redraw elevation map image
        img_path = path.join(ABS_PATH,"height.png")
        elevation_map_img = pg.image.load(img_path)
        
        self.elevation_map_img = pg.transform.scale(elevation_map_img,(self.total_x,self.total_y))
        self.elevation_map_img = pg.transform.rotate(self.elevation_map_img,90)
        self.elevation_map_img = pg.transform.flip(self.elevation_map_img,0,1)

    def calcRandNearby(self,x,y,rand_range):
        rand_range = rand_range * 2
        found = False
        empty_range = self.checkEmptyInRange(x,y,rand_range)
        if empty_range == []:
            return None, None
        tuple = random.choice(empty_range)
        return tuple[0], tuple[1]

    def checkEmptyInRange(self,x,y,rand_range):
        empties = []
        for i in range(-rand_range, rand_range + 1):
            for j in range(-rand_range, rand_range + 1):
                if self.checkValidTile(x+i,y+j):
                    if self.occupied_grid[x+i][y+j] == 0:
                        empties.append([x+i,y+j])
        return empties

    # Check to make sure a given XY set is 
    def checkValidTile(self,x,y):
        if x >= 0 and y >= 0:
            if x < GAME_GRID_WIDTH and y < GAME_GRID_HEIGHT:
                return True
        return False

    def calcHeightMap(self):
        self.elevation_map = np.random.randint(0,high=250, size=(GAME_GRID_WIDTH,GAME_GRID_HEIGHT))
        img_path = path.join(ABS_PATH,"height.png")
        img = Image.fromarray(self.elevation_map).convert('L').filter(ImageFilter.GaussianBlur(1))
        img.save(img_path)
        self.elevation_map = np.asarray(Image.open(img_path)).copy()
        arr_max = self.elevation_map.max()
        arr_min = self.elevation_map.min()

        for x in range(GAME_GRID_WIDTH):
            for y in range(GAME_GRID_HEIGHT):
                val = np.interp(self.elevation_map[x][y],[arr_min,arr_max],[20,255])
                self.elevation_map[x,y] = val

        img = Image.fromarray(self.elevation_map).convert('L')
        img.save(img_path)
        
        elevation_map_img = pg.image.load(img_path)
        
        self.elevation_map_img = pg.transform.scale(elevation_map_img,(self.total_x,self.total_y))
        self.elevation_map_img = pg.transform.rotate(self.elevation_map_img,90)
        self.elevation_map_img = pg.transform.flip(self.elevation_map_img,0,1)

    # Get a random valid X coordinate.
    def randGridX(self):
        return random.randint(0,GAME_GRID_WIDTH-1)

    # Get a random valid Y coordinate.
    def randGridY(self):
        return random.randint(0,GAME_GRID_HEIGHT-1)

    # Get a random valid XY coordinate set.
    def randGridSpace(self):
        return self.randGridX(), self.randGridY()

    # Efficiently get a random XY pair that isn't already used. 
    def randEmptySpace(self):
        if np.count_nonzero(self.occupied_grid) < NUM_SPACES*0.5:
            found = False
            while found == False:
                x,y = self.randGridSpace()
                if self.occupied_grid[x][y] == 0:
                    found = True
            return x,y 
        else:
            empty_left = NUM_SPACES-len(occupied_spaces)
            choice = random.randint(0,empty_left)
            count = 0
            for i in range(self.height):
                for j in range(self.width):
                    if self.occupied_grid[i][j] == 0:
                        if count >= choice:
                            return i,j
                        count += 1
            for i in range(self.height):
                for j in range(self.width):
                    if self.occupied_grid[i][j] == 0:
                        if count >= choice:
                            return i,j
                        count += 1
            print("ERROR: No spaces available")
            sys.exit(9)

    # Calculate the amount of padding needed for the current grid.
    def calcGridPadding(self):
        self.total_grid_x = self.width*self.padding + self.width*self.square_size
        self.grid_padding = int((RENDER_WIDTH - self.total_grid_x)/2)
        return self.grid_padding

    # Calculate a XY location for a given tile location
    def calcTileLocation(self,tile):
        x = tile.x * self.padding + tile.x * self.square_size + self.grid_padding
        y = tile.y * self.padding + tile.y * self.square_size + self.grid_padding
        x += self.padding*2
        y += self.padding*2
        return x, y
    
    def calcXYLocation(self,x,y):
        world_x = x * self.padding + x * self.square_size + self.grid_padding
        world_y = y * self.padding + y * self.square_size + self.grid_padding
        world_x += self.padding*2
        world_y += self.padding*2
        return world_x, world_y
        
    def calcTileFromXY(self,x,y):

        if x <= self.grid_padding or y <= self.grid_padding:
            return None, None
        if x >= self.grid_padding + GAME_GRID_WIDTH * (self.padding + self.square_size):
            return None, None
        if y >= self.grid_padding + GAME_GRID_HEIGHT * (self.padding + self.square_size):
            return None, None

        tile_x = None
        tile_y = None

        for i in range(GAME_GRID_WIDTH):
            j = i + 1
            low = i * self.padding + i * self.square_size + self.grid_padding
            high = j * self.padding + j * self.square_size + self.grid_padding
            if low <= x <= high:
                tile_x = i 

        for i in range(GAME_GRID_HEIGHT):
            j = i + 1
            low = i * self.padding + i * self.square_size + self.grid_padding
            high = j * self.padding + j * self.square_size + self.grid_padding
            if low <= y <= high:
                tile_y = i

        return tile_x, tile_y
        

    # Get a tile by it's coordinates. If no tile matches, return None
    def getTile(self,x,y):
        if not self.checkValidTile(x,y):
            return None
        for tile in self.occupied_spaces:
            if tile.x == x and tile.y == y:
                return tile
        return None

    def calcGridSize(self):
        self.total_x = self.width * self.padding + self.width * self.square_size
        self.total_y = self.height * self.padding + self.height * self.square_size

    # Draw the grid without anything else.
    def drawGrid(self,surface):
        grid_pos_x = self.padding + self.grid_padding
        for i in range(self.height + 1):
            pg.draw.rect(
                        surface,
                        self.line_color,
                        pg.Rect(
                            grid_pos_x,
                            self.padding + self.grid_padding, 
                            self.padding, 
                            self.total_y)
                    )
            grid_pos_x += self.square_size + self.padding

        grid_pos_y = self.padding + self.grid_padding

        for i in range(self.width + 1):
            pg.draw.rect(
                        surface,
                        self.line_color,
                        pg.Rect(
                            self.padding + self.grid_padding,
                            grid_pos_y, 
                            self.total_x,
                            self.padding
                            )
                    )
            grid_pos_y += self.square_size + self.padding

    def draw(self, surface):
        x = self.padding + self.grid_padding
        y = self.padding + self.grid_padding
        
        rect = self.elevation_map_img.get_rect().move((x,y))
        surface.blit(self.elevation_map_img, rect)

        self.drawGrid(surface)

class GameManager:
    """ A class that controls the logic and graphics of the game. """
    def __init__(self,width,height):
        self.grid = Grid(height, width)
        self.agents = []
        self.dead_agents = []
        self.plants = []
        
        self.addAgent()
        self.font = Font(path.join(ABS_PATH,"Retron2000.ttf"), 16)
        self.stat_font = Font(path.join(ABS_PATH,"Retron2000.ttf"), 14)
        self.agents[0].select()
        self.main_agent = self.agents[0]
        for i in range(NUM_EVIL):
            self.addEvilAgent()
        for i in range(NUM_AGENTS-1):
            self.addAgent()
    
        for curr in self.agents:
            curr.age = AGE_OF_CONSENT
            
        #self.addAgent(ObjectType.PROCREATION, path.join(ABS_PATH, "art_assets","agent_faces","agent_faces_procreation"))
        
        for i in range(MAX_NUM_FOOD_ON_GRID):
            self.addPlant()
    
    def __getstate__(self):
        #print("Within getState of GameManager")
        attributes = self.__dict__.copy()
        del attributes['font']
        del attributes['stat_font']
        return attributes
    
    def __setstate__(self, state):
        #print("Within setstate of GameManager")
        self.__dict__ = state
        self.font = Font(path.join(ABS_PATH,"Retron2000.ttf"), 16)
        self.stat_font = Font(path.join(ABS_PATH,"Retron2000.ttf"), 14)
    
    def selectFromXY(self,x,y):
        calc_x, calc_y = self.grid.calcTileFromXY(x,y)
        selected_id = None
        if calc_x != None and calc_y != None:
            for agent in self.agents:
                if agent.x == calc_x and agent.y == calc_y:
                    selected_id = agent.id
        if selected_id != None:
            self.selectByID(selected_id)
        return selected_id

    def selectByID(self,sel_id):
        global SIMULATION_RUNNER_ALWAYS_HAVE_SELECTED_AGENT
        
        selected_agent = False
        decided_id = sel_id
        
        if decided_id is None and self.main_agent is not None:
            decided_id = self.main_agent.id
            
        for agent in self.agents:
            if ((not selected_agent) and (decided_id is None or (agent.id == decided_id))):
                selected_agent = True
                agent.select()
            else:
                agent.selected = False
                
        if selected_agent:
            return decided_id
        elif SIMULATION_RUNNER_ALWAYS_HAVE_SELECTED_AGENT:
            # Select the first available agent
            if self.agents:
                self.agents[0].select()
                return self.agents[0].id
            else:
                return None
        else:
            return None

    def draw(self,surface,simulation_runner_message=None):
        self.grid.draw(surface)
        
        # Draw plants
        for plant in self.plants:
            world_x, world_y = self.grid.calcXYLocation(plant.x,plant.y)
            plant.draw(world_x, world_y, surface)

        for agent in self.agents:
                world_x, world_y = self.grid.calcXYLocation(agent.x,agent.y)
                agent.draw(world_x, world_y, surface)
        
        for agent in self.agents:
            if agent.selected:
                self.main_agent = agent
                
        labels_y_start = 470
        
        draw_outline(self.font, f"ID: {self.main_agent.id}", self.grid.grid_padding-32, labels_y_start, surface)
        surface.blit(self.font.render(f"ID: {self.main_agent.id}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start))
        draw_outline(self.font, f"HEALTH: {self.main_agent.health:.2f}", self.grid.grid_padding-32, labels_y_start+20, surface)
        surface.blit(self.font.render(f"HEALTH: {self.main_agent.health:.2f}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start+20))
        draw_outline(self.font, f"ENERGY: {self.main_agent.energy:.2f}", self.grid.grid_padding-32, labels_y_start+40, surface)
        surface.blit(self.font.render(f"ENERGY: {self.main_agent.energy:.2f}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start+40))
        draw_outline(self.font, f"SCORE:   {self.main_agent.score:.2f}", self.grid.grid_padding-32, labels_y_start+60, surface)
        surface.blit(self.font.render(f"SCORE:   {self.main_agent.score:.2f}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start+60))
        
        stats1 = {}
        stats2 = {}
        stats3 = {}
        
        index = 0
        for key in self.main_agent.stats.stats:
            if index < 4:
                stats1[key] = round(self.main_agent.stats.stats[key], 2)
            elif index < 7:
                stats2[key] = round(self.main_agent.stats.stats[key], 2)
            else:
                stats3[key] = round(self.main_agent.stats.stats[key], 2)
            index += 1
        
        draw_outline(self.stat_font, f"{stats1}", self.grid.grid_padding-32, labels_y_start+80, surface)
        surface.blit(self.stat_font.render(f"{stats1}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start+80))
        draw_outline(self.stat_font, f"{stats2}", self.grid.grid_padding-32, labels_y_start+100, surface)
        surface.blit(self.stat_font.render(f"{stats2}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start+100))
        draw_outline(self.stat_font, f"{stats3}", self.grid.grid_padding-32, labels_y_start+120, surface)
        surface.blit(self.stat_font.render(f"{stats3}", 0, (255, 0, 0)), (self.grid.grid_padding-32, labels_y_start+120))

        if simulation_runner_message is not None:
            draw_outline(self.font, simulation_runner_message, self.grid.grid_padding, 15, surface)
            surface.blit(self.font.render(simulation_runner_message, 0, (255, 0, 0)), (self.grid.grid_padding, 15))
        
    def plantTick(self):
        for plant in self.plants:
            plant.tick()

    def agentTick(self,agent,move=None):
        global HANDLED_TICK
        if agent.alive == False:
            return
        
        agent.tick()
        if move == None:
            move = agent.choose_movement()

        offset_x, offset_y, difficulty = dir2offset(move)
        old_x = agent.x
        old_y = agent.y
        new_x = agent.x + offset_x
        new_y = agent.y + offset_y
        
        if self.grid.checkValidTile(new_x, new_y):
            curr_height = self.grid.elevation_map[agent.x][agent.y]
            new_height = self.grid.elevation_map[new_x][new_y]
            difficulty = 1
            diff_add = (int(new_height) - int(curr_height))/255

            difficulty = DEFAULT_TERRAIN_DIFFICULTY + diff_add
            #TODO Finish this

            agent.move(new_x,new_y,difficulty)

        if agent.type != ObjectType.EVIL:
            for plant in self.plants:
                if agent.x == plant.x and agent.y == plant.y:
                    if EAT_PLANT_INSTANT:
                        agent.consume(plant.energy)
                        self.plants.remove(plant)
                        self.addPlant()
                    else:
                        #if agent.pregnant >= 0:
                        #    agent.pregnant += 1
                        if plant.energy > agent.stats.stats['bite_size']:
                            agent.consume(agent.stats.stats['bite_size'])
                            plant.deplete(agent.stats.stats['bite_size'])
                        else:
                            agent.consume(plant.energy)
                            self.plants.remove(plant)
                            self.addPlant()

                for target_agent in self.agents:
                    if agent.id != target_agent.id and target_agent.alive and agent.x == target_agent.x and agent.y == target_agent.y:    
                        agent.attempt_mate(target_agent)
                        if not target_agent.alive:
                            if target_agent not in self.dead_agents:
                                self.dead_agents.append(target_agent)
                            self.agents.remove(target_agent)
                            
                # if agent.age >= AGE_OF_CONSENT and agent.pregnant == -1:
                #     for target_agent in self.agents:
                #         if target_agent.id != agent.id and target_agent.type == agent.type and target_agent.pregnant == -1 and target_agent.alive and target_agent.age >= AGE_OF_CONSENT and (target_agent.age - target_agent.last_pregnant_age >= PREGNANCY_COOLDOWN):
                #             if agent.x == target_agent.x and agent.y == target_agent.y:
                #                 target_agent.pregnant = 0
                                #if (target_agent.type == ObjectType.EVIL):
                                    #target_agent.img.fill(pg.Color("#AAAAFF"),special_flags=pg.BLEND_MIN)
        else:
            for target_agent in self.agents:
                if target_agent.type != ObjectType.EVIL or not target_agent.alive or agent.energy < 30:
                    if target_agent.alive:
                        if agent.id != target_agent.id and agent.x == target_agent.x and agent.y == target_agent.y:
                            hit_strength = agent.stats.stats["strength"]+agent.stats.stats["bite_size"]
                            damage = target_agent.take_damage(hit_strength)
                            agent.consume(damage)
                    else:
                        bite = agent.stats.stats["bite_size"]
                        if target_agent.energy > bite:
                            agent.consume(bite)
                            #if agent.pregnant >= 0:
                            #    agent.pregnant += 10
                            target_agent.deplete(bite)
                            
                        else:
                            agent.consume(target_agent.energy)
                            #if agent.pregnant >= 0:
                            #    agent.pregnant += target_agent.energy
                            target_agent.die()
                            if (target_agent.selected):
                                for candidate in self.agents:
                                    if (candidate.type != ObjectType.EVIL and candidate.alive):
                                        candidate.select()
                                        break
                            target_agent.selected = False
                            if target_agent not in self.dead_agents:
                                self.dead_agents.append(target_agent)
                            self.agents.remove(target_agent)
            
            for target_agent in self.agents:
                if agent.id != target_agent.id and target_agent.alive and agent.x == target_agent.x and agent.y == target_agent.y:    
                    agent.attempt_mate(target_agent)
            # if agent.age >= AGE_OF_CONSENT and agent.pregnant == -1:
            #     for target_agent in self.agents:
            #         if target_agent.id != agent.id and target_agent.type == agent.type and target_agent.is_pregnant == False and target_agent.alive and target_agent.age >= AGE_OF_CONSENT:
            #             #if (target_agent.age - target_agent.last_pregnant_age >= PREGNANCY_COOLDOWN):
            #             if agent.x == target_agent.x and agent.y == target_agent.y:
            #                 fertility_score = target_agent.stats.stats["fertility"] + agent.stats.stats["fertility"]  
            #                 needed = random.randint(0,agent.stats.gene_cap*2)
            #                 if fertility_score >= needed:
            #                     if VERBOSE:
            #                         print(f"{agent.id} has impregnated {target_agent.id}!")
            #                     target_agent.is_pregnant = True
            #                     target_agent.pregnant = 0
                            #target_agent.raw_img_path = path.join(ABS_PATH,"art_assets","agent_faces","agent_faces_procreation_evil")
                            #target_agent.calc_img_path(target_agent.raw_img_path)
                            #target_agent.loadImg(target_agent.img_path)
                            #target_agent.img.fill(pg.Color("#AAAAFF"),special_flags=pg.BLEND_MIN)

        if agent.alive and agent.is_pregnant and agent.pregnant >= sum(agent.baby_stats.stats.values()):
            baby_x, baby_y = self.grid.calcRandNearby(agent.x, agent.y, 1)
            baby = agent.give_birth(baby_x, baby_y, HANDLED_TICK)
            
            self.agents.append(baby)
            baby.sense.update(baby.x, baby.y, self.grid, self.agents,self.plants)
            if VERBOSE:
                print(f"{agent.id} has given birth to {baby.id}!")
        
        agent.sense.update(agent.x,agent.y,self.grid,self.agents,self.plants)
        #agent.age += 1


    def logicTick(self,tick_num=None,player_move=None,draw_func=None):
        global HANDLED_TICK
        HANDLED_TICK = tick_num
        random.shuffle(self.plants)
        self.plantTick()

        #TODO Prove this won't skip anyone if someone is killed or is born
        run_ids = []

        total_agent_ids = [agent.id for agent in self.agents if agent.alive]

        tickable_agent = True
        
        try:
            while ((len(run_ids) < len(total_agent_ids)) and tickable_agent):
                tickable_agent = False
                random.shuffle(self.agents)
                for agent in self.agents:
                    if ((agent.id not in run_ids) and agent.alive):
                        rand = random.randint(0,10)
                        if rand <= agent.stats.stats["agility"]:
                            for i in range(agent.stats.getNumMoves()):
                                self.agentTick(agent)
                                if draw_func != None:
                                    draw_func()
                            agent.age += 1
                            run_ids.append(agent.id)
                            # Greedy approach to ensure complete enumeration of agents; quadratic complexity
                            new_agents = [curr_agent.id for curr_agent in self.agents if ((curr_agent.id not in total_agent_ids) and curr_agent.alive)]
                            if (agent.alive or len(new_agents) > 0):
                                tickable_agent = True
                            elif ((not agent.alive) and (tick_num is not None)):
                                agent.death_tick = tick_num
                            total_agent_ids.extend(new_agents)

        except Exception as e:
            traceback.print_exc()
            print("ERROR IN LOGICTICK!")
            sys.exit(9)
                     
        # Returns the ID for bookkeeping from the simulation runner/driver program
        if self.main_agent:
            return self.main_agent.id     
        else:
            return None

    def addPlant(self):
        x, y = self.grid.randEmptySpace()
        plant = Plant(x,y)
        self.plants.append(plant)

    def addAgent(self,agent_type=None,image_path=None):
        x, y = self.grid.randEmptySpace()
        agent = Agent(x,y,image_path)
        if agent_type is not None:
            agent.type = agent_type
        self.agents.append(agent)

    def addEvilAgent(self):
        x, y = self.grid.randEmptySpace()
        agent = EvilAgent(x,y)
        self.agents.append(agent)

    def setOccupiedGrid(self):
        self.grid.occupied_grid = np.zeros((GAME_GRID_WIDTH,GAME_GRID_HEIGHT))
        for plant in self.plants:
            self.grid.occupied_grid[plant.x][plant.y] = ObjectType.PLANT
        for agent in self.agents:
            self.grid.occupied_grid[agent.x][agent.y] = agent.type

    def getAgents(self):
        return self.agents

    def getDeadAgents(self):
        return self.dead_agents

# All simple mouse does is pick a random direction, and moves there.
# Quite senseless, if you ask me.
def simple_mouse():
    return random.choice(range(0,4))

# The smart mouse uses its nose to find food. It does this by checking
# which path has the greatest amount of food smells, and going in that
# direction. 

def smart_mouse(scent_matrix):

    # If there are no scents, just pick a random direction.
    if not np.any(scent_matrix):
        return simple_mouse()
    
    # Get the maximum value, or values
    indexes = [i for i, x in enumerate(scent_matrix) if x == max(scent_matrix)]

    # Make a random choice from all the best options
    move_choice = random.choice(indexes)
    return move_choice
    # return movement_array.index(max(movement_array))
