import pygame
import time
import sys
import random
import numpy as np

black = (0,0,0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
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
types_to_sidelengths = [4, 6, 10]

# TODO:
"""
    1. Data sctructure for reactions
    2. Timed reactions. Add to Particle class.

    3. Save history
    4. Controls, step forward/back
    
"""

class Particle(pygame.Rect):
    def __init__(self, top, left, typ):
        s = types_to_sidelengths[typ]
        super().__init__(top, left, s, s)
        self.typ = typ

    # make a random nearby particle  
    def spawn(self, radius, typ):
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
        indices = []
        sidelength = types_to_sidelengths[particle.typ]
        for x in range(max(0, particle.x - sidelength), \
                min(particle.x + sidelength + 1, window_size[0]), stride):
            for y in range(max(0, particle.y - sidelength), \
                    min(particle.y + sidelength + 1, window_size[1]), stride):
                # get counts and indices for all nonzero counts
                if (self.matrix[x][y][:] > 0).any():
                    indices.append([x, y])
                    counts += self.matrix[x][y][:]
        if [particle.x, particle.y] not in indices:
            indicies.append([particle.x, particle.y])
        return counts, indices 
    
    def total_counts(self):
        counts = np.zeros(self.num_types, dtype="int64")
        for particle in self.particles:
            counts[particle.typ] += 1
        return counts

    def do_reactions(self, particle, counts, indices, reactions):
        for reaction in reactions:
            if np.array_equal(counts, reaction[0]):
                print(f'reaction {particle.x, particle.y, counts, indices}')
                # remove matrix entries
                for x, y in indices:
                    self.matrix[x][y][:] = 0
                # get final particles
                final = []
                for i in range(len(reaction[1])):
                    final += [particle.spawn(step, i) for _ in range(reaction[1][i])]
                return final
        # brownian
        self.matrix[particle.x][particle.y][particle.typ] -= 1
        return [particle.spawn(step, particle.typ)]

    def step(self):
        new_particles = []
        for particle in self.particles:
            if self.matrix[particle.x][particle.y][particle.typ] > 0:
                counts, indices = self.count_overlapping(particle, 1)
                new_particles += self.do_reactions(particle, counts, indices, reactions)
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
            [[1, 1, 0], [0, 0, 1]]
            ]

    simulation = Simulation(window_size[0], window_size[1], initial_particles, 3, reactions)

    screen = pygame.display.set_mode(window_size)

    while True:
        print(simulation.total_counts())
        screen.fill(gray)
        simulation.draw(screen)
        pygame.display.update()
        simulation.step()
        time.sleep(0.001)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

    
