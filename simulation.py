import pygame
import time
import sys
import random
import numpy as np

black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0,100,255)
gray = (47,79,79)

window_size = (500, 500)

nRed = 100
nGreen = 100 

particle_size = 5
step = 5

RED = 0
GREEN = 1
BLUE = 2
    
types_to_colors = [red, green, blue]
types_to_sidelengths = [4, 6, 8]

# TODO:
"""
    Save history
    Controls, step forward/back
    Time/probability in reactions?
    
"""

class Particle(pygame.Rect):
    def __init__(self, top, left, typ):
        self.length = types_to_sidelengths[typ]
        super().__init__(top, left, self.length, self.length)
        self.typ = typ

    # make a random nearby particle  
    def spawn(self, typ, radius=None):
        if radius is None:
            radius = self.length
        x = random.randint(self.x - radius, self.x + radius)
        y = random.randint(self.y - radius, self.y + radius)
        if x > window_size[0] - 1 or x < 0:
            x = self.x
        if y > window_size[1] - 1 or y < 0:
            y = self.y
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
    
    # count overlapping particles, including particle itself
    def count_overlapping(self, particle, stride = 1):
        counts = np.zeros(self.num_types, dtype="int16")
        sidelength = types_to_sidelengths[particle.typ]
        for x in range(max(0, particle.x - sidelength), \
                min(particle.x + sidelength + 1, window_size[0]), stride):
            for y in range(max(0, particle.y - sidelength), \
                    min(particle.y + sidelength + 1, window_size[1]), stride):
                # add matrix entry to counts
                # remove entry from matrix
                counts += self.matrix[x][y][:]
                self.matrix[x][y][:] = 0
        return counts 
    
    def total_counts(self):
        counts = np.zeros(self.num_types, dtype="int64")
        for particle in self.particles:
            counts[particle.typ] += 1
        return counts

    def do_reactions(self, particle, counts, reactions):
        # reactions must include brownian motion for each type of particle!
        reaction_set = set(reactions)
        new_particles = []
        while (counts > 0).any():
            random_reaction = random.sample(reaction_set, 1)[0]
            if (random_reaction[0] <= counts).all():
                # do reaction
                for i in range(len(random_reaction[1])):
                    for j in range(random_reaction[1][i]):
                        new_particles.append(particle.spawn(i, radius=max(types_to_sidelengths)))
                # decrement counts
                counts -= random_reaction[0]
            else:
                reaction_set.remove(random_reaction)
        return new_particles 

    def step(self):
        new_particles = []
        for particle in self.particles:
            if self.matrix[particle.x][particle.y][particle.typ] > 0:
                counts = self.count_overlapping(particle, 1)
                new_particles += self.do_reactions(particle, counts, reactions)
        self.particles = new_particles
        # make sure matrix is empty
        assert (self.matrix == 0).all(), str(np.sum(self.matrix != 0))
        self.populate_matrix()
    
    def draw(self, screen):
        for particle in self.particles:
            pygame.draw.rect(screen, types_to_colors[particle.typ], particle)

if __name__ == '__main__':
    reds = [Particle(random.randint(0, window_size[0] - 1), \
            random.randint(0, window_size[1] - 1), RED) for _ in range(nRed)]
    greens = [Particle(random.randint(0, window_size[0] - 1), \
            random.randint(0, window_size[1] - 1,), GREEN) for _ in range(nGreen)]
    initial_particles = reds + greens

    reactions = [
            ((1, 0, 0), (1, 0, 0)),
            ((0, 1, 0), (0, 1, 0)),
            ((0, 0, 1), (0, 0, 1)),
            ((1, 1, 0), (0, 0, 1))
            ]

    simulation = Simulation(window_size[0], window_size[1], initial_particles, 3, reactions)

    screen = pygame.display.set_mode(window_size)

    while True:
        print(simulation.total_counts())
        screen.fill(black)
        simulation.draw(screen)
        pygame.display.update()
        simulation.step()
        time.sleep(0.001)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

    
