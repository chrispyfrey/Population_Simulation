# FinalProject

Our team’s project aims to simulate natural selection through independent agents competing and procreating in a finite grid with finite resources. This will be developed in Python 3.x, leveraging the PyGame library for visualization & user control of the simulation environment & parameters. We will also be using Tensorflow as the underlying framework for the agents’ neural networks.

-------------------

### General requirements:

1.	Agents behave independently within a simulation for resource competition. From our currently developed underlying grid-based framework, our simulation will likely be event-driven until some end condition (e.g. some boundary runtime value or an extinction/total dominance criteria) is met.

2.	Each agent has a neural network that dictates its actions based on the sensory inputs of its surroundings. The underlying actions will be rule-based, and the decisions for those actions will be chosen based on a deep learning neural network. The simulation aims to cull poor performing agents & generate successful agents in the long-term based on inherent refinement of the neural network’s parameters (i.e. successful agents progress into subsequent simulations, and/or their parameters are selected for subsequent generations).

3.	If two agents are similar enough, they can combine to produce offspring (i.e. some new agent[s] with their own individual models & neural networks that act as a random combination of the weights of the parent neural networks).

### Design approach:

1.	Will each agent ‘learn’ while it’s alive, or will network mutations only occur during reproduction?

1a.	If they learn during life, we will use a reinforcement learning model.

2.	How many different types of food will there be? What will dictate if a food poisons an agent or gives it energy?

2a.	This would likely be a modulated value for each type of food. A possible implementation is that each agent has a set of values that dictate how much energy (Positive or negative) that it can receive from a given food, with a limited total value that it can choose how to distribute.

2b.	Another more complicated option for nourishment is to use plant-life as a source of food, but make agents also act as a source of food. When an agent eats a plant, it could defecate seeds which will grow into other plants. This would encourage specialization of herbivores and carnivores and give the simulation more control over where food spawns.

3.	How many resource dimensions should the agents have? Energy, intelligence, strength, teamwork, etc, etc. Specialization of food for each? Linear scaling of benefit, or otherwise?

3a.	How should the attributes of the agents be parameterized in equation(s) to determine either adversarial or procreative behavior between two agents which happen to meet on the same tile? Consequently, how many parameters are necessary for agents to have consistent, meaningful behavior wrt agent interaction (i.e. will the results & runtime of the simulation be dependent upon complexity of the agents)?

4.	How should food be distributed on the game grid?

4a.	A possible way to distribute food on the game grid would be to randomize both    locations and amounts of food and run multiple simulations. This way we can find out how food availability affects the agents’ evolution and interaction with one another.

5.	Should there be multiple types of terrain that agents can specialize to? (Ex: Water and land)

5a.	This could use a similar system as the food implementation, but it would be a stretch goal that might be too difficult to implement in the time given.

6.	Should agents have a set lifespan, random chance of death per tick increase over time, make them weaker to attacks the older they are, or simply have them die when they reproduce? Maybe a combination? Would something similar to genetic diseases be possible, or perhaps emergent with large enough neural networks? 

7.	Should agents belong to various groups (and if so, how successful are they relative to solo agents), and must they be complementary to reproduce? If so, how similar do they need to be? Should agents that reproduce be paired in some way for their lifespan?

Overall, our ultimate goal is to try to create the conditions that lead to evolution and see if we can identify emergent properties of evolution (e.g. species specialization). This will give some insights on how fundamental certain concepts we’ve noticed regarding life on earth are to competing entities, be they lifeforms or simulated structures. It will also provide information regarding the minimum environmental complexity necessary for these emergent properties.

# Team leader: 

Matt Michaelis (email: matthew.michaelis@ucdenver.edu)

# Team members:

Joshua McAllister (email: joshua.mcallister@ucdenver.edu)

Christopher Frey (email: christopher.frey@ucdenver.edu)

Kyle VanSteelandt (email: kyle.vansteelandt@ucdenver.edu)

Jacob Parrott (email: jacob.parrott@ucdenver.edu)

