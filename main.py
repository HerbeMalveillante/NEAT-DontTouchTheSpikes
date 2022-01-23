import pygame
import random
import neat
import os
import matplotlib.pyplot as plt

pygame.init()
font = pygame.font.SysFont(None, 24)

# for the stats
BEST_SCORES = []
AVG_SCORES = []

GEN = 0 # For the neat algorithm
BEST_SCORE = 0
BEST_GEN = 0

WIDTH = 400
HEIGHT = 700
FPS = 60

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GRAY1 = (200, 200, 200)
GRAY2 = (100, 100, 100)

RED = (255, 0, 0)
BLUE = (0, 0, 255)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Don't touch the spikes - NEAT")
clock = pygame.time.Clock()     ## For syncing the FPS


def collides(x1, y1, w1, h1, x2, y2, w2, h2):
    if x1 + w1 > x2 and x1 < x2 + w2 and y1 + h1 > y2 and y1 < y2 + h2:
        return True
    else:
        return False

def increase_stat_counters(totalscores):
    global BEST_SCORES
    global AVG_SCORES

    BEST_SCORES.append(max(totalscores))
    AVG_SCORES.append(sum(totalscores)/len(totalscores))


def draw_environment():
    pygame.draw.rect(screen, GRAY2, [0, 0, WIDTH, 20])
    triangleBase = WIDTH/10
    for i in range(10):
        pygame.draw.polygon(screen, GRAY2, [(i*triangleBase, 20), (i*triangleBase+triangleBase, 20), (i*triangleBase+triangleBase/2, 50)])
    pygame.draw.rect(screen, GRAY2, [0, HEIGHT-20, WIDTH, 20])
    for i in range(10):
        pygame.draw.polygon(screen, GRAY2, [(i*triangleBase, HEIGHT-20), (i*triangleBase+triangleBase, HEIGHT-20), (i*triangleBase+triangleBase/2, HEIGHT-50)])


class Triangle():

    def __init__(self, side, y):
        self.side = side
        self.y = y
        self.collisions = [(0 if side == "left" else WIDTH-5, self.y+3, 5, 36), (5 if side == "left" else WIDTH-5-5, self.y+3+5, 5, 26), (10 if side == "left" else WIDTH-5-10, self.y+3+10, 5, 16), (15 if side == "left" else WIDTH-5-20, self.y+3+15, 10, 6)]
    
    def __repr__(self):
        return (f"side: {self.side}, y: {self.y}")

    def draw(self):
        # img = font.render(str(self.y), True, BLACK)
        if self.side == "left":
            pygame.draw.polygon(screen, GRAY2, [(0, self.y), (0, self.y+40), (30, self.y+20)])
        else :
            pygame.draw.polygon(screen, GRAY2, [(WIDTH, self.y), (WIDTH, self.y+40), (WIDTH-30, self.y+20)])
        # screen.blit(img, (0, self.y))

        # for i in self.collisions:
        #    pygame.draw.rect(screen, BLUE, i)



TRIANGLES = [Triangle("right", random.choice([i for i in range(50, HEIGHT-50-30, 40)])) for i in range(4)]
def reset_triangles(side, score):
    global TRIANGLES
    yRange = [i for i in range(50, HEIGHT-50-30, 40)]
    TRIANGLES = [Triangle(side, random.choice(yRange)) for i in range(4)]
    additional_triangles = score//10
    if additional_triangles >= 6:
        additional_triangles = 6
    for i in range(additional_triangles): 
        TRIANGLES.append(Triangle(side, random.choice(yRange)))


class BirdCollection():
    def __init__(self):
        self.x = WIDTH / 2
        self.side = "left"
        self.score = 0
        self.birds = []
        self.speed = 5

    def addBird(self):
        self.birds.append(Bird(self))
    
    def update(self):

        global BEST_SCORE
        global BEST_GEN

        if self.score > BEST_SCORE:
            BEST_SCORE = self.score
            BEST_GEN = GEN


        for i in self.birds:
            i.update()
        
        if self.x <= 0:
            self.side = "left"
            self.score += 1
            print("score = ", self.score )
            reset_triangles("right", self.score)
        elif self.x >= WIDTH-30:
            self.side = "right"
            self.score += 1
            print("score = ", self.score)
            reset_triangles("left", self.score)
        
        # self.speed = 5 + self.score/30

        if self.side == "left":
            self.x += self.speed
        else:
            self.x -= self.speed

        # for i in self.birds :
        #     if i.is_dead():
        #         self.birds.remove(i)
        
    def jump(self):
        for i in self.birds:
            i.jump()
        
    def draw(self):
        # draw the score in the middle of the screen
        img = font.render(str(self.score), True, BLACK)
        screen.blit(img, (WIDTH/2-10, HEIGHT/2-10))
        # display the number of birds alive just below
        img = font.render(str(len(self.birds)) + " birds alive", True, BLACK)
        screen.blit(img, (WIDTH/2-50, HEIGHT/2+10))
        # display the GEN number just below
        img = font.render(f"GEN: {GEN}", True, BLACK)
        screen.blit(img, (WIDTH/2-30, HEIGHT/2+30))
        # display the BEST_SCORE just below
        img = font.render(f"BEST SCORE: {BEST_SCORE} at gen {BEST_GEN}", True, BLACK)
        screen.blit(img, (WIDTH/2-90, HEIGHT/2+50))

        for b in self.birds:
            pygame.draw.rect(screen, b.color, [self.x, b.y, 30, 30])
class Bird():
    VEL = 5
    GRAVITY = .5
    JUMP_FORCE = 7.5

    def __repr__(self):
        return "I am a Bird !"

    def __init__(self, parent):
        # position it on the middle of the screen
        self.y = HEIGHT / 2
        self.vel = 0
        self.height = self.y
        self.speed = 5
        # give the bird a random RGB color
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.parent = parent
    
    def jump(self):
        self.vel = self.JUMP_FORCE
        self.height = self.y

    def is_dead(self):
        if self.y <= 50 or self.y >= HEIGHT-50-30:
            return True
        # collisions with the spikes
        # I can improve the performance later by firstly checking if the bird collides with a big unprecise square then the more precise ones.
        for i in TRIANGLES:
            for c in i.collisions:
                if collides(self.parent.x, self.y, 30, 30, c[0], c[1], c[2], c[3]):
                    return True
        return False

    def update(self):

        self.vel -= self.GRAVITY
        self.y -= self.vel
        
        
def main(genomes, config):
    global GEN
    global TRIANGLES
    GEN += 1

    TOTALSCORES = []

    nets = []
    ge = []
    BIRDS = BirdCollection()

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        BIRDS.addBird()
        g.fitness = 0
        ge.append(g)


    run = True

    while run :
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    BIRDS.jump()

        if len (BIRDS.birds) == 0:
            increase_stat_counters(TOTALSCORES)
            run = False
            break
        
        BIRDS.update()
        for x in range(len(BIRDS.birds)):

            if x >= len(BIRDS.birds):
                break
        
            try :
                ge[x].fitness += 0.1
            except : 
                print(f"genome could not have been found (index missing) (ge : {len(ge)}, nets : {len(nets)}, birds : {len(BIRDS.birds)}), x : {x}")

            FULL_TRIANGLES = TRIANGLES.copy()
            while len(FULL_TRIANGLES) < 10: # filling the triangles list so it's 10 elements long. The network needs a static number of elements to work.
                FULL_TRIANGLES.append(Triangle("right", -10000))

            # we feed to the network :
            # - the bird's position (x and y)
            # - the bird's velocity
            # - the y position of the ten triangles
            # - the current direction of the bird (0 for left, 1 for right)
            # - for a total of 14 inputs.
            output = nets[x].activate((BIRDS.x,
            BIRDS.birds[x].y,
            BIRDS.birds[x].vel,
            FULL_TRIANGLES[0].y,
            FULL_TRIANGLES[1].y,
            FULL_TRIANGLES[2].y,
            FULL_TRIANGLES[3].y,
            FULL_TRIANGLES[4].y,
            FULL_TRIANGLES[5].y,
            FULL_TRIANGLES[6].y,
            FULL_TRIANGLES[7].y,
            FULL_TRIANGLES[8].y,
            FULL_TRIANGLES[9].y,
            0 if BIRDS.side == "left" else 1))

            # we have one output : should we jump ? yes or no ?
            if output[0] > 0.5:
                BIRDS.birds[x].jump()
            
            if BIRDS.birds[x].is_dead():
                ge[x].fitness -= 1
                BIRDS.birds.remove(BIRDS.birds[x])
                nets.remove(nets[x])
                ge.remove(ge[x])
                TOTALSCORES.append(BIRDS.score)


        # we draw the screen
        screen.fill(GRAY1)
        draw_environment()
        BIRDS.draw()
        for i in TRIANGLES:
            i.draw()

        pygame.display.flip()

    
    # generates a plot of the BEST_SCORES and the AVG_SCORES and saves it to a file
    plt.plot(BEST_SCORES, label="best scores")
    plt.plot(AVG_SCORES, label="average scores")
    plt.xlabel("Generation")
    plt.legend()
    plt.savefig("plot.png")

    # resets the figure
    plt.clf()
    

    print(BEST_SCORES)
    print(AVG_SCORES)      

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 5000)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)