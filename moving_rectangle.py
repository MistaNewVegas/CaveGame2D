'''
 Pygame base template for opening a window
 Sample Python/Pygame Programs
 
'''
import pygame
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
pygame.init()
 
# Set the width and height of the screen [width, height]
size = (700, 500)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("My First Pygame Game")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Starting position of rectangle
rect_x = 50 
rect_y = 50

# Speed of rectangle in X and Y axis
speed_x = 5
speed_y = 5

# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
 
    # --- Game logic should go here
 
    # --- Screen-clearing code goes here
 
    # Here, we clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
 
    # If you want a background image, replace this clear with blit'ing the
    # background image.
    screen.fill(BLACK)
 
    # --- Drawing code should go here

    pygame.draw.rect(screen, WHITE, [rect_x, rect_y, 50,50])
    rect_x += speed_x
    rect_y += speed_y
    print ("rect_x =", rect_x, "rect_y =", rect_y)
    
    #pygame.draw.circle(screen, RED, [200, 140], 30, 5)
    
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()