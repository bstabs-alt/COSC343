# Reuben Sweetman-Gough
# ID: 8271161

import numpy as np
import random
import matplotlib.pyplot as plt
playerName = "myAgent"
nPercepts = 75  #This is the number of percepts
nActions = 5    #This is the number of actionss

current_gen = 0 # current generation
generation = 200 # total generations
fitness_arr = np.zeros(generation) # array to hold each generations fitness average
gen_arr = np.zeros(generation) # holds each generation number

# Train against random for x generations
trainingSchedule = [("random", generation))]


# This is the class for the creature/agent.
# maps chromosomes to actions, and contains the genetic algorithm.
class MyCreature:

    # initialises self.chromosome member variable with some random values
    def __init__(self):

        # 1 eat food
        # 2-5 towards berry
        # 6-9  towards enemy
        # 10-13 towards friendly
        # 14-17 towards walls
        size = 17
        self.chromosome = []
        for i in range(size):
            self.chromosome.append(random.randint(-9, 9))

    # attributes self.chromosome to actions for the agent
    def AgentFunction(self, percepts):

        actions = np.zeros(nActions) # 5-dimension vector of zeros for applicable actions

        creature_map = percepts[:, :, 0]  # 5x5 map with information about creatures and their size
        food_map = percepts[:, :, 1]  # 5x5 map with information about strawberries
        wall_map = percepts[:, :, 2]  # 5x5 map with information about walls

        my_size = creature_map[2, 2] # holds size if current creature

        # The index of the largest numbers in the 'actions' vector/list is the action taken
        # with the following interpretation:
        # 0 - move left
        # 1 - move up
        # 2 - move right
        # 3 - move down
        # 4 - eat

        # determines value for eating food
        if food_map[2, 2] == 1:
            actions[4] = self.chromosome[0]

        # determines values for the four directions based on food
        for i in range(-2, 3):
            for j in range(-2, 3):
                if food_map[2 + i, 2 + j] > 0:
                    if i < 0:
                        actions[0] += self.chromosome[1]
                    elif j < 0:
                        actions[3] += self.chromosome[2]
                    elif i > 0:
                        actions[2] += self.chromosome[3]
                    elif j > 0:
                        actions[1] += self.chromosome[4]

        # determines values for the four directions based on creatures
        for i in range(-2, 3):
            for j in range(-2, 3):
                if creature_map[2 + i, 2 + j] > 0:
                    if np.abs(creature_map[2 + i, 2 + j]) < my_size:
                        if i < 0:
                            actions[0] += self.chromosome[5]
                        elif j < 0:
                            actions[3] += self.chromosome[6]
                        elif i > 0:
                            actions[2] += self.chromosome[7]
                        elif j > 0:
                            actions[1] += self.chromosome[8]
                    else:
                        if i < 0:
                            actions[0] += self.chromosome[9]
                        elif j < 0:
                            actions[3] += self.chromosome[10]
                        elif i > 0:
                            actions[2] += self.chromosome[11]
                        elif j > 0:
                            actions[1] += self.chromosome[12]

        # determines values for the four directions based on walls
        for i in range(-2, 3):
            for j in range(-2, 3):
                if wall_map[2 + i, 2 + j] == 1:
                    if i < 0:
                        actions[0] += self.chromosome[13]
                    elif j < 0:
                        actions[3] += self.chromosome[14]
                    elif i > 0:
                        actions[2] += self.chromosome[15]
                    elif j > 0:
                        actions[1] += self.chromosome[16]

        return actions


# creates and returns the next generation as well as
# the current generations average fitness
def newGeneration(old_population):
    global current_gen
    chance = 0.1 - ((current_gen / generation) / 20) # chance for mutation for new generation
    N = len(old_population)

    # Fitness for all agents
    fitness = np.zeros((N))

    # Iterates over the agents in the old population and attributes them a fitness
    for n, creature in enumerate(old_population):

        # creature.alive - boolean, true if creature is alive at the end of the game
        # creature.turn - turn that the creature lived to (last turn if creature survived the entire game)
        # creature.size - size of the creature
        # creature.strawb_eats - how many strawberries the creature ate
        # creature.enemy_eats - how much energy creature gained from eating enemies
        # creature.squares_visited - how many different squares the creature visited
        # creature.bounces - how many times the creature bounced

        # This calls the fitness functions
        fitness[n] = fitness_function(creature, n)

    # sorts the agents according to fitness with a temporary copy
    # of the old_population and their fitness
    ordered_population = order(list(fitness.copy()), old_population.copy())
    fitness = -np.sort(-fitness)

    # picks the top 10% of the population to be elites based on fitness
    elites = ordered_population[0:int(len(ordered_population)/10)]

    # list to be filled with next generation
    new_population = list()

    # goes through the length of the population and populates
    # the new population with children, elites, and may mutate
    for n in range(N):

        # Create new creature
        new_creature = MyCreature()

        # Uses tournament selection to find two suitable parents
        parent1 = old_population[tournament_selection(fitness, 8)]
        parent2 = old_population[tournament_selection(fitness, 8)]
        while parent1 == parent2: # makes sure the parents are not the same creature
            parent2 = old_population[tournament_selection(fitness, 8)]
        # single-point crossover
        splice = random.randint(0, 17)
        new_creature.chromosome = parent1.chromosome[0:splice] + parent2.chromosome[splice:17]
        # chance to call the mutate method on the child after each generation
        if random.random() < chance:
            new_creature.chromosome = mutate(new_creature.chromosome)
        # adds an elite to the new population if no mutation occurs
        elif len(elites):
            new_creature = elites.pop()
        # Add the new agent to the new population
        new_population.append(new_creature)

    # At the end you neet to compute average fitness and return it along with your new population
    avg_fitness = np.mean(fitness)

    gen_arr[current_gen] = current_gen #adds generation number
    fitness_arr[current_gen] = avg_fitness # adds current generations average fitness
    # calls a function to plot the average fitness
    if current_gen == generation - 1:
        plot_fitness(avg_fitness)
    current_gen = current_gen + 1

    return new_population, avg_fitness


# determines fitness based on being alive or how many turns they survived
# as well as how many enemies they ate
def fitness_function(creature, n):
    if creature.alive:
        n = 20
    else:
        n += int(creature.turn/10)
    n += creature.enemy_eats * 5
    n += creature.strawb_eats
    return n


# goes through a set of k individuals ands selects the best individual
def tournament_selection(fitness, k):
    best_fitness = None
    winner = 0
    for i in range(k):
        potential_winner = random.randint(0, len(fitness)-1)
        if best_fitness is None or best_fitness < fitness[potential_winner]:
            best_fitness = fitness[potential_winner]
            winner = potential_winner
    return winner


# mutates 1 random chromosome in the child
def mutate(creature_mutate):
    change = random.randint(0, 16)
    new_value = random.randint(-9, 9)
    creature_mutate[change] = new_value
    return creature_mutate


# orders the population based on fitness
def order(fitness, old_pop):
    ordered_pop = list()
    elite = 0
    for i in range(int(len(old_pop))):
        best_fitness = None
        for j in range(len(old_pop)):
            if best_fitness is None or best_fitness < fitness[j]:
                best_fitness = fitness[j]
                elite = j
        ordered_pop.append(old_pop.pop(elite))
        fitness.pop(elite)
    return ordered_pop


# plots the average fitness over generations
def plot_fitness(avg_fitness):
    plt.title("Average Fitness Over Generations")
    plt.xlabel("Generations")
    plt.ylabel("Fitness Average")
    b = np.polyfit(gen_arr, fitness_arr, 1)
    p = np.poly1d(b)
    plt.plot(gen_arr, p(gen_arr), "r--")
    plt.plot(gen_arr, fitness_arr)
    plt.show()
