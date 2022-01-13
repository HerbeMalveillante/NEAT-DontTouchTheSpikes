import pygame
import random

pygame.init()
font = pygame.font.SysFont(None, 24)

WIDTH = 400
HEIGHT = 700
FPS = 60

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GRAY1 = (200, 200, 200)
GRAY2 = (100, 100, 100)

RED = (255, 0, 0)

## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Don't touch the spikes - NEAT")
clock = pygame.time.Clock()     ## For syncing the FPS


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
    
    def draw(self):
        # img = font.render(str(self.y), True, BLACK)
        if self.side == "left":
            pygame.draw.polygon(screen, GRAY2, [(0, self.y), (0, self.y+40), (30, self.y+20)])
        else :
            pygame.draw.polygon(screen, GRAY2, [(WIDTH, self.y), (WIDTH, self.y+40), (WIDTH-30, self.y+20)])
        # screen.blit(img, (0, self.y))


class Bird(pygame.sprite.Sprite):
    VEL = 5
    GRAVITY = .5
    JUMP_FORCE = 7.5

    def __init__(self):
        # position it on the middle of the screen
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.vel = 0
        self.tick_count = 0
        self.height = self.y
        self.side = "left"
        self.speed = 5
        self.score = 0
        self.triangles=[]
    
    def jump(self):
        self.vel = self.JUMP_FORCE
        self.height = self.y

    def update(self):

        self.speed = 5 + self.score/10

        self.vel -= self.GRAVITY
        self.y -= self.vel
        if self.y <= 50 or self.y >= HEIGHT-50-30:
            self.score = 0
            self.y = HEIGHT/2
            self.x = WIDTH/2 + 30/2
            self.vel = 0
            self.tick_count = 0
            self.side = "left"

        yRange = [i for i in range(50, HEIGHT-50-30, 40)]
        print(yRange)
        
        if self.x <= 0:
            self.side = "left"
            self.score += 1
            print("score = ", self.score)
            self.triangles = [Triangle("right", random.choice(yRange)) for i in range(4)]
        elif self.x >= WIDTH-30:
            self.side = "right"
            self.score += 1
            print("score = ", self.score)
            self.triangles = [Triangle("left", random.choice(yRange)) for i in range(4)]
        
        if self.side == "left":
            self.x += self.speed
        else:
            self.x -= self.speed


    def draw(self):
        pygame.draw.rect(screen, RED, [self.x, self.y, 30, 30])

bird = Bird()
triangle = Triangle("right", 80)


## Game loop
running = True
while running:

    #1 Process input/events
    clock.tick(FPS)     ## will make the loop run at the same speed all the time
    for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False
        # if player pressed the space key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()
    bird.update()


    #3 Draw/render
    screen.fill(GRAY1)
    draw_environment()
    bird.draw()
    for i in bird.triangles :
        i.draw()

    ########################

    ### Your code comes here

    ########################

    ## Done after drawing everything to the screen
    pygame.display.flip()       

pygame.quit()