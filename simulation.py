import pygame
import time
import sys
import random
import pickle
import numpy as np

black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0,100,255)
gray = (47,79,79)

window_size = (500, 500)

nRed = 10000
nGreen = 1000 

particle_size = 5
step = 5

WHITE = 0
GRAY = 1
RED = 2
    
types_to_colors = [white, gray, red]
types_to_sidelengths = [4, 6, 8]

# TODO:
"""
    Implement sorting algorithm
        sort particles by x coordinate
        get clumps of overlapping particles
        for each clump,
            sort particles by y coordinate
            get clumps of overlapping particles, store in component_list 
        we have component_list 

        for component in component_list:
            cycle reactions until particles are used up.
            



    Save history
    Controls, step forward/back
    Time/probability in reactions?
    
"""

class Particle(pygame.Rect):
    def __init__(self, left, top, typ):
        self.length = types_to_sidelengths[typ]
        super().__init__(left, top, self.length, self.length)
        self.typ = typ
        self.pos = [left, top]

    def spawn(xi, yi, typ, radius=None):
        if radius is None:
            radius = types_to_sidelengths[typ]
        x = random.randint(xi - radius, xi + radius)
        y = random.randint(yi - radius, yi + radius)
        if x > window_size[0] - 1 or x < 0:
            x = xi
        if y > window_size[1] - 1 or y < 0:
            y = yi
        return Particle(x, y, typ)
       
        
class Simulation:
    def __init__(self, xsize, ysize, initial_particles, num_types, reactions=[]):
        self.particles = initial_particles
        self.matrix = np.zeros((window_size[0], window_size[1], num_types), dtype="int16")   
        self.populate_matrix()
        self.reactions = reactions
        self.num_types = num_types
        
    def populate_matrix(self):
        for particle in self.particles:
            self.matrix[particle.x][particle.y][particle.typ] += 1

    def total_counts(self):
        counts = np.zeros(self.num_types, dtype="int64")
        for particle in self.particles:
            counts[particle.typ] += 1
        return counts


    #TODO: new do_reactions
    def do_reactions(self, clump, reactions):
        reaction_set = set(reactions)
        new_particles = []

        counts = np.array([0] * self.num_types)
        for particle in clump:
            counts[particle.typ] += 1

        positions = [[] for _ in range(self.num_types)]
        for particle in clump:
            positions[particle.typ] += [particle.pos]

        while (counts > 0).any():
            reactants, products, p = random.sample(reaction_set, 1)[0]
            # if reaction is possible
            if (reactants <= counts).all():
                reactant_positions = set()

                # get positions of reactants and add to set
                for i in range(len(positions)):
                    slice_i = positions[i][len(positions[i]) - reactants[i]:]
                    positions[i] = positions[i][:len(positions[i]) - reactants[i]]
                    for (x, y) in slice_i:
                        reactant_positions.add((x, y))

                assert len(reactant_positions) > 0, 'reactant_positions is empty!'

                # rng for reaction success
                if random.random() < p:
                    output = products
                else:
                    output = reactants

                # create reaction product particles 
                for i in range(len(output)):
                    for j in range(output[i]):
                        # get a random position from the set
                        x, y = random.sample(reactant_positions, 1)[0]
                        new_particles.append(Particle.spawn(x, y, i, radius=max(types_to_sidelengths)))
                counts -= reactants 
            else:
                reaction_set.remove((reactants, products, p))
        return new_particles 

    
    # clump replaces count_overlapping
    def clump(particles, dim = 0):
        '''
        clump(particles: list[Particle]) -> clumps: list[list[Particle]]

        sort particles by given dimension and seperate them into lists
        containing only overlapping particles

        '''

        #TODO: put limit on upper - lower to avoid giant components

        component_list = []
        component = []
        upper = 0
        lower = 1 
        sorted_particles = sorted(particles, key=lambda x : x.pos[dim])

        for particle in sorted_particles:
            if lower <= particle.pos[dim] <= upper and not upper - lower > particle.length*2:
                component.append(particle)
                upper = max(upper, particle.pos[dim] + particle.length - 1)
                lower = min(lower, particle.pos[dim] - particle.length + 1)
            else:
                if len(component) > 0 :
                    component_list.append(component)
                component = [particle]
                upper = particle.pos[dim] + particle.length - 1
                lower = particle.pos[dim] - particle.length + 1

        component_list.append(component)

        return component_list


    def step(self):
        tick = time.time()
        new_particles = []

        for xclump in Simulation.clump(self.particles, 0):
            for component in Simulation.clump(xclump, 1):
                new_particles += self.do_reactions(component, self.reactions)
            

        self.particles = new_particles
        self.populate_matrix()
        tock = time.time()
        print(f'step time: {round(tock - tick, 3)}')
    
    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.rect(screen, types_to_colors[particle.typ], particle)

def main():
    reds = [Particle(random.randint(0, window_size[0] - 1), \
            random.randint(0, window_size[1] - 1), RED) for _ in range(nRed)]
    initial_particles = reds


    # reaction: ((reactants), (products), probability)
    reactions = [
            ((1, 0, 0), (1, 0, 0), 1),
            ((0, 1, 0), (0, 1, 0), 1),
            ((0, 0, 1), (0, 0, 1), 1),
            ((1, 1, 0), (0, 0, 1), 1),
            ((0, 0, 1), (1, 1, 0), 0.01)
            ]

    simulation = Simulation(window_size[0], window_size[1], initial_particles, 3, reactions)


    screen = pygame.display.set_mode(window_size)

    # TODO: save history
    # TODO: playback function to animate history
    #           history can just be a list of particles, because that's all we need to do animations!

    history = []

    def animate(save_history=True):
        running = True
        while running:
            print(simulation.total_counts())
            screen.fill(black)
            simulation.draw(screen)
            pygame.display.update()

            if save_history:
                history.append(simulation.particles)

            simulation.step()
            time.sleep(0.001)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
        if save_history:
            with open('history.pickle', 'wb') as f:
                pickle.dump(history, f)

    def playback(history):
        '''
        play/pause: ENTER
        forward/back: j/k
        forward/backx10: h/l
        '''
        # state variables
        index = 0
        paused = True
        running = True

        # game loop
            # user input
            # change state
            # render

        # game loop
        while running:
            # user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False
                if event.type == pygame.KEYDOWN:
                    # change state 
                    # play/pause
                    if event.key == pygame.K_RETURN:
                        paused = not paused
                    # forward/back
                    if event.key == pygame.K_j:
                        index = min(len(history) - 1, index + 1)
                    if event.key == pygame.K_k:
                        index = max(0, index - 1)
                    # forward/back x10
                    if event.key == pygame.K_h:
                        index = min(len(history) - 1, index + 10)
                    if event.key == pygame.K_l:
                        index = max(0, index - 10)
                    # jump around
                    if event.key in range(pygame.K_0, pygame.K_9):
                        index = (len(history) - 1) * (event.key - pygame.K_0) // 10
            if running:
                if not paused:
                    index = min(len(history) - 1, index + 1)
                # render
                screen.fill(black)
                for particle in history[index]:
                    pygame.draw.rect(screen, types_to_colors[particle.typ], particle)
                pygame.display.update()

    # --------------------- Run ---------------------- 
    animate()

    screen = pygame.display.set_mode(window_size)

    # Trying to load the pickled history, but it's giving me:
    #   TypeError: __init__() takes 4 positional arguments but 5 were given 
    #
    # with open('history.pickle', 'rb') as f:
    #     history = pickle.load(f)

    playback(history)

if __name__ == '__main__':
    main()
