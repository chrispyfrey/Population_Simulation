import pandas as pd
import os
from simulation_framework import *
from variable_config import *

ARR_GAME_STATES = []

GAME_STATE_INDEX = -1 # Needs to execute one logic tick to create a legitimate game state for the initial GameManager

GLOBAL_TICK = 0

ABS_PATH = path.dirname(path.realpath(__file__))

pg.init()
game_manager = None

game_window = pg.display.set_mode((RENDER_WIDTH, RENDER_HEIGHT))
render_window = game_window.copy()

game_window.fill(BACKGROUND_COLOR)
render_window.fill(BACKGROUND_COLOR)

game_window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
game_window.fill(BACKGROUND_COLOR)

pg.display.set_caption('Simulation')

run_game_loop = True
restore = True

def incFPS():
    global FPS_SELECTION
    global FPS_LIST
    
    FPS_SELECTION += 1
    if FPS_SELECTION >= len(FPS_LIST):
        FPS_SELECTION = 0


def incSkip():
    global SKIP_SELECTION
    global SKIP_LIST
    
    SKIP_SELECTION += 1
    if SKIP_SELECTION >= len(SKIP_LIST):
        SKIP_SELECTION = 0

def globalDraw():
    global game_window
    global render_window
    global game_manager
    global clock
    global SIMULATION_RUNNER_PAUSED
    global SIMULATION_RUNNER_PAUSE_LOCK
    global SIMULATION_RUNNER_SIGNAL_REDRAW
    global SIMULATION_RUNNER_TERMINATING
    global delta_time
    global selected_id 
    
    check_events()
    
    game_window.fill(BACKGROUND_COLOR)
    render_window.fill(BACKGROUND_COLOR)
    
    selected_id = game_manager.selectByID(selected_id)
   
    simulation_runner_message = None
    if SIMULATION_RUNNER_TERMINATING:
        simulation_runner_message = f"ENDING SIMULATION [waiting on end of tick]..."
    elif SIMULATION_RUNNER_PAUSED:
        if SIMULATION_RUNNER_PAUSE_LOCK:
            simulation_runner_message = f"PAUSING (waiting on end of tick)..."
        else:
            simulation_runner_message = f"PAUSED"
    
    game_manager.draw(render_window,simulation_runner_message=simulation_runner_message)
    game_window.blit(pg.transform.smoothscale(render_window, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
    pg.display.flip()
    
    diff = pg.time.get_ticks() - delta_time
    #print(f"Initial diff: {diff}")
    while (diff < 1000/FPS_LIST[FPS_SELECTION] and ((not SIMULATION_RUNNER_PAUSED) or SIMULATION_RUNNER_PAUSE_LOCK)):
        check_events()
        if SIMULATION_RUNNER_SIGNAL_REDRAW:
            SIMULATION_RUNNER_SIGNAL_REDRAW = False
            render_window.fill(BACKGROUND_COLOR)
            selected_id = game_manager.selectByID(selected_id)
            simulation_runner_message = None
            if SIMULATION_RUNNER_TERMINATING:
                simulation_runner_message = f"ENDING SIMULATION [waiting on end of tick]..."
            elif SIMULATION_RUNNER_PAUSED:
                if SIMULATION_RUNNER_PAUSE_LOCK:
                    simulation_runner_message = f"PAUSING (waiting on end of tick)..."
                else:
                    simulation_runner_message = f"PAUSED"
            game_manager.draw(render_window,simulation_runner_message=simulation_runner_message)
            game_window.blit(pg.transform.smoothscale(render_window, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
            pg.display.flip()

        diff = pg.time.get_ticks() - delta_time
        #print(f"Diff: {diff}")
        
    delta_time = pg.time.get_ticks()
        
def progressState():
    global ARR_GAME_STATES
    global GLOBAL_TICK
    global GAME_STATE_INDEX
    global SIMULATION_RUNNER_PAUSE_LOCK
    global game_manager
    global delta_time
    global selected_id
    
    delta_time = pg.time.get_ticks()
    
    if GLOBAL_TICK > 0 and TURN_VIEW:
        selected_id = game_manager.logicTick(GLOBAL_TICK, draw_func=globalDraw)
    else:
        selected_id = game_manager.logicTick(GLOBAL_TICK)
    
    GLOBAL_TICK += 1     
    
    if SAVE_STATES:
        if (len(ARR_GAME_STATES) < MAX_GAME_STATES):
            GAME_STATE_INDEX += 1
        
        if (len(ARR_GAME_STATES) == MAX_GAME_STATES):
            ARR_GAME_STATES.pop(0)
        ARR_GAME_STATES.append((GLOBAL_TICK, GameState(game_manager)))

def rewindState():
    global ARR_GAME_STATES
    global GAME_STATE_INDEX
    global game_manager
    if SAVE_STATES:
        restored_state = ARR_GAME_STATES[GAME_STATE_INDEX][1]
        game_manager = restored_state.restore()
        GAME_STATE_INDEX += 1

def check_events():
    global SIMULATION_RUNNER_PAUSED
    global SIMULATION_RUNNER_PAUSE_LOCK
    global restore
    global run_game_loop
    global GAME_STATE_INDEX
    global selected_id
    global SIMULATION_RUNNER_SIGNAL_REDRAW
    global clock
    global FPS_SELECTION
    global FPS_LIST
    global SIMULATION_RUNNER_TERMINATING
    global TURN_VIEW
    
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                run_game_loop = False
            if event.key == pg.K_f:
                incFPS()
            if event.key == pg.K_t:
                TURN_VIEW = not TURN_VIEW
            if event.key == pg.K_p and not SIMULATION_RUNNER_PAUSE_LOCK:
                if not SIMULATION_RUNNER_PAUSED:
                    SIMULATION_RUNNER_PAUSE_LOCK = True
                    SIMULATION_RUNNER_SIGNAL_REDRAW = True
                    print("Waiting for agents' actions to end before pausing...")
                if SAVE_STATES:
                    restore = True
                SIMULATION_RUNNER_PAUSED = not SIMULATION_RUNNER_PAUSED
            if event.key == pg.K_RIGHT and SIMULATION_RUNNER_PAUSED and not SIMULATION_RUNNER_PAUSE_LOCK:
                if SAVE_STATES:
                    if (GAME_STATE_INDEX < len(ARR_GAME_STATES)-1):
                        GAME_STATE_INDEX += 1
                        restore = True
                    elif (GAME_STATE_INDEX > len(ARR_GAME_STATES)):
                        print("ERROR: GAME_STATE_INDEX OOB WITH K_RIGHT")
                        exit(9)
                else:
                    progressState()
    
            if event.key == pg.K_LEFT and SIMULATION_RUNNER_PAUSED and not SIMULATION_RUNNER_PAUSE_LOCK:
                if (GAME_STATE_INDEX == len(ARR_GAME_STATES)):
                    GAME_STATE_INDEX -= 2
                    restore = True
                elif (GAME_STATE_INDEX > 0):
                    GAME_STATE_INDEX -= 1
                    restore = True

            if event.key == pg.K_s:
                incSkip()
        # Check to see if the user has requested that the game end.
        if event.type == pg.QUIT:
            run_game_loop = False
            SIMULATION_RUNNER_TERMINATING = True
            SIMULATION_RUNNER_SIGNAL_REDRAW = True
            print("Waiting for tick to finish before closing...")
        if event.type == pg.MOUSEBUTTONDOWN:
            #print("Received MBUTTONDOWN event!")
            mpos = pg.mouse.get_pos()
            selected_id = game_manager.selectFromXY(mpos[0]*(RENDER_WIDTH/WINDOW_WIDTH), mpos[1]*(RENDER_HEIGHT/WINDOW_HEIGHT))
            SIMULATION_RUNNER_SIGNAL_REDRAW = True

def writeSimData(game_manager):
    data_dict = {
        # Attributes
        'id' : [], 'type' : [], 'health' : [], 'energy' : [], 'score' : [], 'age' : [], 'alive' : [],
        'max_energy' : [], 'mate_id' : [], 'pregnant' : [], 'is_pregnant' : [], 'last_pregnant_age' : [],
        'mating_cooldown' : [], 'mating_cooldown_max' : [], 'good_choice_chance' : [], 'children' : [],
        'birth_tick' : [], 'death_tick' : [],
        # Sense
        'sight_range' : [], 'smell_range' : [],
        # Stats
        'gene_avg' : [], 'gene_cap' : [], 'gene_min' : [], 'gene_stability' : [], 'speed' : [], 'agility' : [], 
        'intelligence' : [], 'endurance' : [], 'strength' : [], 'fertility' : [], 'bite_size' : [], 'ticks' : GLOBAL_TICK
    }
    carn_data_dict = {
        'id' : [], 'gene_stability' : [], 'speed' : [], 'agility' : [], 
        'intelligence' : [], 'endurance' : [], 'strength' : [], 'fertility' : [], 'bite_size' : []
    }
    herb_data_dict = {
        'id' : [], 'gene_stability' : [], 'speed' : [], 'agility' : [], 
        'intelligence' : [], 'endurance' : [], 'strength' : [], 'fertility' : [], 'bite_size' : []
    }

    all_agents = game_manager.getAgents()
    dead_agents = game_manager.getDeadAgents()
    all_agents.extend(dead_agents)
    
    for agent in all_agents:
        if agent.type == ObjectType.EVIL :
            carn_data_dict['id'].append(agent.id)
            carn_data_dict['gene_stability'].append(agent.stats.stats['gene_stability'])
            carn_data_dict['speed'].append(agent.stats.stats['speed'])
            carn_data_dict['agility'].append(agent.stats.stats['agility'])
            carn_data_dict['intelligence'].append(agent.stats.stats['intelligence'])
            carn_data_dict['endurance'].append(agent.stats.stats['endurance'])
            carn_data_dict['strength'].append(agent.stats.stats['strength'])
            carn_data_dict['fertility'].append(agent.stats.stats['fertility'])
            carn_data_dict['bite_size'].append(agent.stats.stats['bite_size'])
        else:
            herb_data_dict['id'].append(agent.id)
            herb_data_dict['gene_stability'].append(agent.stats.stats['gene_stability'])
            herb_data_dict['speed'].append(agent.stats.stats['speed'])
            herb_data_dict['agility'].append(agent.stats.stats['agility'])
            herb_data_dict['intelligence'].append(agent.stats.stats['intelligence'])
            herb_data_dict['endurance'].append(agent.stats.stats['endurance'])
            herb_data_dict['strength'].append(agent.stats.stats['strength'])
            herb_data_dict['fertility'].append(agent.stats.stats['fertility'])
            herb_data_dict['bite_size'].append(agent.stats.stats['bite_size'])
        data_dict['id'].append(agent.id)
        data_dict['type'].append(agent.type)
        data_dict['health'].append(agent.health)
        data_dict['energy'].append(agent.energy)
        data_dict['score'].append(agent.score)
        # For initial agents age of consent offset
        if agent.id < NUM_AGENTS + NUM_EVIL:
            data_dict['age'].append(agent.age-100)
        else:
            data_dict['age'].append(agent.age)
        data_dict['alive'].append(agent.alive)
        data_dict['max_energy'].append(agent.max_energy)
        data_dict['mate_id'].append(agent.mate.id) if agent.mate else data_dict['mate_id'].append(-1)
        data_dict['pregnant'].append(agent.pregnant)
        data_dict['is_pregnant'].append(agent.is_pregnant)
        data_dict['last_pregnant_age'].append(agent.last_pregnant_age)
        data_dict['mating_cooldown'].append(agent.mating_cooldown)
        data_dict['mating_cooldown_max'].append(agent.mating_cooldown_max)
        data_dict['good_choice_chance'].append(agent.good_choice_chance)
        data_dict['children'].append(agent.children)
        data_dict['birth_tick'].append(agent.birth_tick)
        data_dict['death_tick'].append(agent.death_tick)
        # Sense
        data_dict['sight_range'].append(agent.sense.sight_range)
        data_dict['smell_range'].append(agent.sense.smell_range)
        # Stats
        data_dict['gene_avg'].append(agent.stats.gene_avg)
        data_dict['gene_cap'].append(agent.stats.gene_cap)
        data_dict['gene_min'].append(agent.stats.gene_min)
        data_dict['gene_stability'].append(agent.stats.stats['gene_stability'])
        data_dict['speed'].append(agent.stats.stats['speed'])
        data_dict['agility'].append(agent.stats.stats['agility'])
        data_dict['intelligence'].append(agent.stats.stats['intelligence'])
        data_dict['endurance'].append(agent.stats.stats['endurance'])
        data_dict['strength'].append(agent.stats.stats['strength'])
        data_dict['fertility'].append(agent.stats.stats['fertility'])
        data_dict['bite_size'].append(agent.stats.stats['bite_size'])
    
    write_path = path.join(ABS_PATH, 'stat_data', 'agent_data.csv')
    herb_write_path = path.join(ABS_PATH, 'stat_data', 'herb_agent_data.csv')
    carn_write_path = path.join(ABS_PATH, 'stat_data', 'carn_agent_data.csv')

    os.makedirs(os.path.dirname(write_path), exist_ok=True)
    
    successfully_wrote_file = False
    error_message_lock = False
    while (not successfully_wrote_file):            
        try:
            pd.DataFrame(data_dict).to_csv(write_path, index=False, mode="w+")
            pd.DataFrame(herb_data_dict).to_csv(herb_write_path, index=False, mode="w+")
            pd.DataFrame(carn_data_dict).to_csv(carn_write_path, index=False, mode="w+")
            successfully_wrote_file = True
        except Exception as e:
            if (not error_message_lock):
                error_message_lock = True
                print("ERROR: File currently open. Waiting for close...")
            game_window.fill(BACKGROUND_COLOR)
            render_window.fill(BACKGROUND_COLOR)
            game_manager.draw(render_window,simulation_runner_message=f"I/O lock: Close out of open stats file to finish!")
            game_window.blit(pg.transform.smoothscale(render_window, (WINDOW_WIDTH, WINDOW_HEIGHT)), (0, 0))
            pg.display.flip()

def GameLoop():
    global ARR_GAME_STATES
    global GLOBAL_TICK
    global GAME_STATE_INDEX
    global game_manager
    global run_game_loop
    global SIMULATION_RUNNER_PAUSED 
    global SIMULATION_RUNNER_PAUSE_LOCK
    global restore 

    game_manager = GameManager(GAME_GRID_WIDTH, GAME_GRID_HEIGHT)
    
    while run_game_loop:
        check_events()
        if not SIMULATION_RUNNER_PAUSED and not SIMULATION_RUNNER_EXCEPTION_CAUGHT:
            for i in range(SKIP_LIST[SKIP_SELECTION] + 1):
                if (GAME_STATE_INDEX >= 0 and GAME_STATE_INDEX <= len(ARR_GAME_STATES)-1):
                    rewindState()
                else:
                    progressState()
        else:
            if SAVE_STATES:
                if restore and GAME_STATE_INDEX >= 0 and GAME_STATE_INDEX <= len(ARR_GAME_STATES)-1:
                    restore = False
                    restored_state = ARR_GAME_STATES[GAME_STATE_INDEX][1]
                    game_manager = restored_state.restore()
            #print(f"Restoring state: {restored_state}")
            #print(f"Game manager: {game_manager}")
            
        # print(f"Index: {GAME_STATE_INDEX}")
        globalDraw()
        if SIMULATION_RUNNER_PAUSED and SIMULATION_RUNNER_PAUSE_LOCK:
            SIMULATION_RUNNER_PAUSE_LOCK = False
            print("Paused the simulation!")

        if GLOBAL_TICK == 300:
            break

    writeSimData(ARR_GAME_STATES[-1][1].restore())
    
    print("Simulation ending. Goodbye!")
    pg.display.quit()
    pg.quit()
    
GameLoop()
