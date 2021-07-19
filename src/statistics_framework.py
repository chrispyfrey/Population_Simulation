import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from os import path

ABS_PATH = path.dirname(path.realpath(__file__))

def read_data(choosenFile):
    frame = None
    read_path = path.join(ABS_PATH, 'stat_data', choosenFile)
    if path.exists(read_path):
        frame = pd.read_csv(read_path)
    return frame

#DrawHist- Draws a Histogram that includes more labels along the x-axis such as the values at the edge of each bar, the percentage of buddies in the bar
#and the value at the center of each bar
#The bars will also be coloured depending upon the side of the graph 
#data_set is the data the graph will use *****Buddies are currently always on the Y axis****** The Ylabel is the label for the Y axis

def DrawHist(data_set, title, yLabel):	
    fig, ax = plt.subplots()
    counts, bins, patches = ax.hist(data_set, facecolor='yellow', edgecolor='gray')
    plt.title(title)
    plt.ylabel(yLabel)
    # Set the ticks to be at the edges of the bins. 
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

    # Change the colors of bars at the edges...
    twentyfifth, seventyfifth = np.percentile(data_set, [25, 75])
    for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
        if rightside < twentyfifth:
            patch.set_facecolor('green')
        elif leftside > seventyfifth:
            patch.set_facecolor('red')

    # Label the raw counts and the percentages below the x-axis...
    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    for count, x in zip(counts, bin_centers):
        # Label the raw counts
        ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
            xytext=(0, -18), textcoords='offset points', va='top', ha='center')

        # Label the percentages
        percent = '%0.0f%%' % (100 * float(count) / counts.sum())
        ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
        xytext=(0, -32), textcoords='offset points', va='top', ha='center')


    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.show()


def total_population_time(frame):
    x = np.zeros(frame['ticks'][0])
    y = np.zeros(frame['ticks'][0])
    for i in range(x.size):
        x[i] = i
        for j in range(len(frame.index)):
            age = frame['age'][j]
            birth = frame['birth_tick'][j]
            # If alive at time tick
            if birth <= i and age + birth+1 >= i: 
                y[i] += 1
    fig, ax = plt.subplots()
    ax.plot(x, y, label='Total Population')
    ax.grid()
    ax.legend()
    ax.set(xlabel='Time Ticks', ylabel='Population', title='Total Population/Time')
    plt.show()

def species_population_time(frame):
    x = np.zeros(frame['ticks'][0])
    y_tot = np.zeros(frame['ticks'][0])
    y_evil = np.zeros(frame['ticks'][0])
    y_neutral = np.zeros(frame['ticks'][0])
    for i in range(x.size):
        x[i] = i
        for j in range(len(frame.index)):
            age = frame['age'][j]
            birth = frame['birth_tick'][j]
            # If alive at time tick
            if birth <= i and age + birth+1 >= i: 
                y_tot[i] += 1
                if frame['type'][j] == 'ObjectType.NEUTRAL':
                    y_neutral[i] += 1
                else:
                    y_evil[i] += 1
    fig, ax = plt.subplots()
    ax.plot(x, y_tot, label='Total')
    ax.plot(x, y_evil, label='Carnivore')
    ax.plot(x, y_neutral, label='Herbivore')
    ax.grid()
    ax.set(xlabel='Time Ticks', ylabel='Population', title='Population/Time')
    ax.legend()
    plt.show()

def total_stats_time(frame):
    x = np.zeros(frame['ticks'][0])
    speed = np.zeros(frame['ticks'][0])
    agility = np.zeros(frame['ticks'][0])
    intelligence = np.zeros(frame['ticks'][0])
    endurance = np.zeros(frame['ticks'][0])
    strength = np.zeros(frame['ticks'][0])
    fertility = np.zeros(frame['ticks'][0])
    bite_size = np.zeros(frame['ticks'][0])

    for i in range(x.size):
        x[i] = i
        num_alive = 0
        for j in range(len(frame.index)):
            age = frame['age'][j]
            birth = frame['birth_tick'][j]
            # If alive at time tick
            if birth <= i and age + birth+1 >= i:
                num_alive += 1
                speed[i] += frame['speed'][j]
                agility[i] += frame['agility'][j]
                intelligence[i] += frame['intelligence'][j]
                endurance[i] += frame['endurance'][j]
                strength[i] += frame['strength'][j]
                fertility[i] += frame['fertility'][j]
                bite_size[i] += frame['bite_size'][j]
        if num_alive != 0:
            speed[i] /= num_alive
            agility[i] /= num_alive
            intelligence[i] /= num_alive
            endurance[i] /= num_alive
            strength[i] /= num_alive
            fertility[i] /= num_alive
            bite_size[i] /= num_alive

    fig, ax = plt.subplots()
    ax.plot(x, speed, label='Speed Average')
    ax.plot(x, agility, label='Agility Average')
    ax.plot(x, intelligence, label='Intelligence Average')
    ax.plot(x, endurance, label='Endurance Average')
    ax.plot(x, strength, label='Strength Average')
    ax.plot(x, fertility, label='Fertility Average')
    ax.plot(x, bite_size, label='Bite Size Average')
    ax.grid()
    ax.set(xlabel='Time Ticks', ylabel='Average Stat Totals', title='Total Stats Average/Time')
    ax.legend(loc="right", bbox_to_anchor=(1.6,.5))
    plt.show()

def species_stats_time(frame):
    x = np.zeros(frame['ticks'][0])
    evil_speed = np.zeros(frame['ticks'][0])
    evil_agility = np.zeros(frame['ticks'][0])
    evil_intelligence = np.zeros(frame['ticks'][0])
    evil_endurance = np.zeros(frame['ticks'][0])
    evil_strength = np.zeros(frame['ticks'][0])
    evil_fertility = np.zeros(frame['ticks'][0])
    evil_bite_size = np.zeros(frame['ticks'][0])

    neutral_speed = np.zeros(frame['ticks'][0])
    neutral_agility = np.zeros(frame['ticks'][0])
    neutral_intelligence = np.zeros(frame['ticks'][0])
    neutral_endurance = np.zeros(frame['ticks'][0])
    neutral_strength = np.zeros(frame['ticks'][0])
    neutral_fertility = np.zeros(frame['ticks'][0])
    neutral_bite_size = np.zeros(frame['ticks'][0])

    for i in range(x.size):
        x[i] = i
        evil_alive = 0
        neutral_alive = 0
        for j in range(len(frame.index)):
            age = frame['age'][j]
            birth = frame['birth_tick'][j]
            # If alive at time tick
            if birth <= i and age + birth+1 >= i:
                if frame['type'][j] == 'ObjectType.NEUTRAL':
                    neutral_alive += 1
                    neutral_speed[i] += frame['speed'][j]
                    neutral_agility[i] += frame['agility'][j]
                    neutral_intelligence[i] += frame['intelligence'][j]
                    neutral_endurance[i] += frame['endurance'][j]
                    neutral_strength[i] += frame['strength'][j]
                    neutral_fertility[i] += frame['fertility'][j]
                    neutral_bite_size[i] += frame['bite_size'][j]
                else:
                    evil_alive += 1
                    evil_speed[i] += frame['speed'][j]
                    evil_agility[i] += frame['agility'][j]
                    evil_intelligence[i] += frame['intelligence'][j]
                    evil_endurance[i] += frame['endurance'][j]
                    evil_strength[i] += frame['strength'][j]
                    evil_fertility[i] += frame['fertility'][j]
                    evil_bite_size[i] += frame['bite_size'][j]
        if neutral_alive != 0:
            neutral_speed[i] /= neutral_alive
            neutral_agility[i] /= neutral_alive
            neutral_intelligence[i] /= neutral_alive
            neutral_endurance[i] /= neutral_alive
            neutral_strength[i] /= neutral_alive
            neutral_fertility[i] /= neutral_alive
            neutral_bite_size[i] /= neutral_alive
        if evil_alive != 0:
            evil_speed[i] /= evil_alive
            evil_agility[i] /= evil_alive
            evil_intelligence[i] /= evil_alive
            evil_endurance[i] /= evil_alive
            evil_strength[i] /= evil_alive
            evil_fertility[i] /= evil_alive
            evil_bite_size[i] /= evil_alive
    
    fig, ax = plt.subplots()
    ax.plot(x, evil_speed, 'b-', label='Average Carnivore Speed')
    ax.plot(x, evil_agility, 'g-', label='Average Carnivore Agility')
    ax.plot(x, evil_intelligence, 'r-', label='Average Carnivore Intelligence')
    ax.plot(x, evil_endurance, 'c-', label='Average Carnivore Endurance')
    ax.plot(x, evil_strength, 'm-', label='Average Carnivore Strength')
    ax.plot(x, evil_fertility, 'y-', label='Average Carnivore Fertility')
    ax.plot(x, evil_bite_size, 'k-', label='Average Carnivore Bite Size')

    ax.plot(x, neutral_speed, 'b--', label='Average Herbivore Speed')
    ax.plot(x, neutral_agility, 'g--', label='Average Herbivore Agility')
    ax.plot(x, neutral_intelligence, 'r--', label='Average Herbivore Intelligence')
    ax.plot(x, neutral_endurance, 'c--', label='Average Herbivore Endurance')
    ax.plot(x, neutral_strength, 'm--', label='Average Herbivore Strength')
    ax.plot(x, neutral_fertility, 'y--', label='Average Herbivore Fertility')
    ax.plot(x, neutral_bite_size, 'k--', label='Average Herbivore Bite Size')
    ax.grid()
    ax.legend(loc="right", bbox_to_anchor=(1.6,.5))
    ax.set(xlabel='Time Ticks', ylabel='Average Species Stat Totals', title='Average Species Stats/Time')
    plt.show()

def species_strength_intel_time(frame):
    x = np.zeros(frame['ticks'][0])
    evil_intelligence = np.zeros(frame['ticks'][0])
    evil_strength = np.zeros(frame['ticks'][0])

    neutral_intelligence = np.zeros(frame['ticks'][0])
    neutral_strength = np.zeros(frame['ticks'][0])

    for i in range(x.size):
        x[i] = i
        evil_alive = 0
        neutral_alive = 0
        for j in range(len(frame.index)):
            age = frame['age'][j]
            birth = frame['birth_tick'][j]
            # If alive at time tick
            if birth <= i and age + birth+1 >= i:
                if frame['type'][j] == 'ObjectType.NEUTRAL':
                    neutral_intelligence[i] += frame['intelligence'][j]
                    neutral_strength[i] += frame['strength'][j]
                else:
                    evil_intelligence[i] += frame['intelligence'][j]
                    evil_strength[i] += frame['strength'][j]
        if neutral_alive != 0:
            neutral_intelligence[i] /= neutral_alive
            neutral_strength[i] /= neutral_alive
        if evil_alive != 0:
            evil_intelligence[i] /= evil_alive
            evil_strength[i] /= evil_alive
    
    fig, ax = plt.subplots()
    ax.plot(x, evil_intelligence, 'b-', label='Carnivore Average Intelligence')
    ax.plot(x, evil_strength, 'g-', label='Carnivore Average Strength')

    ax.plot(x, neutral_intelligence, 'b--', label='Herbivore Average Intelligence')
    ax.plot(x, neutral_strength, 'g--', label='Herbivore Average Strength')
    ax.grid()
    ax.legend()
    ax.set(xlabel='Time Ticks', ylabel='Average Strength & Intelligence', title='Average Strength & Intelligence/Time')
    plt.show()

def run_analysis():
    frame = read_data('agent_data.csv')
    herb_frame = read_data('herb_agent_data.csv')
    carn_frame = read_data('carn_agent_data.csv')
    #total_population_time(frame)
    species_population_time(frame)
    # total_stats_time(frame)
    # species_stats_time(frame)
    # species_strength_intel_time(frame)

    """
    if frame is not None:
        DrawHist(frame.loc[:, 'health'], "Health of Buddies", "Number of Buddies")
        DrawHist(frame.loc[:, 'score'], "Buddy Scores", "Number of Buddies")
        DrawHist(frame.loc[:, 'energy'], "Remaining Buddy Energy", "Number of Buddies")
        DrawHist(frame.loc[:, 'age'], "Buddy Age", "Number of Buddies")
        DrawHist(frame.loc[:, 'children'], "Number of Children", "Number of Buddies")
        DrawHist(frame.loc[:, 'speed'], "Buddy Speed", "Number of Buddies")
        DrawHist(frame.loc[:, 'agility'], "Buddy Agility", "Number of Buddies")
        DrawHist(frame.loc[:, 'intelligence'], "Buddy Intelligence", "Number of Buddies")
        DrawHist(frame.loc[:, 'strength'], "Buddy Strength", "Number of Buddies")
        DrawHist(frame.loc[:, 'fertility'], "Buddy Fetility", "Number of Buddies")
        
    if carn_frame is not None:
       
        DrawHist(carn_frame.loc[:, 'speed'], "Carnivore Speed", "Number of Carnivores")
        DrawHist(carn_frame.loc[:, 'agility'], "Carnivore Agility", "Number of Carnivores")
        DrawHist(carn_frame.loc[:, 'intelligence'], "Carnivore Intelligence", "Number of Carnivores")
        DrawHist(carn_frame.loc[:, 'strength'], "Carnivore Strength", "Number of Carnivores")
        DrawHist(carn_frame.loc[:, 'fertility'], "Carnivore Fetility", "Number of Carnivores")
        DrawHist(carn_frame.loc[:, 'gene_stability'], "Carnivore Gene Stablitiy", "Number of Carnivores")
        DrawHist(carn_frame.loc[:, 'bite_size'], "Carnivore Bite Size", "Number of Carnivores")
        
    if herb_frame is not None:
        DrawHist(herb_frame.loc[:, 'speed'], "Herbivore Speed", "Number of Herbivores")
        DrawHist(herb_frame.loc[:, 'agility'], "Herbivore Agility", "Number of Herbivores")
        DrawHist(herb_frame.loc[:,'intelligence'], "Herbivore Intelligence", "Number of Herbivores")
        DrawHist(herb_frame.loc[:, 'strength'], "Herbivore Strength", "Number of Herbivores")
        DrawHist(herb_frame.loc[:, 'fertility'],"Herbivore Fertility", "Number of Herbivores")
        DrawHist(herb_frame.loc[:, 'gene_stability'], "Herbivore Gene Stablitiy", "Number of Herbivores")
        DrawHist(herb_frame.loc[:, 'bite_size'], "Herbivore Bite Size", "Number of Herbivores")
    """
run_analysis()
