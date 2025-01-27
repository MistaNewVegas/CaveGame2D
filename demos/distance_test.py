import pygame
import random
import math

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

WIDTH = 700
HEIGHT = 500
BALL_SIZE = 25

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, change_x, change_y, color, size):
        super().__init__()
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        self.color = color  # Set the color attribute
        pygame.draw.circle(self.image, self.color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.change_x = change_x
        self.change_y = change_y

    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y


def rand_color():
    """Generate a random color."""
    return [random.randrange(0, 255) for _ in range(3)]


def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def make_ball():
    """Create a new, random ball."""
    x = random.randrange(BALL_SIZE, WIDTH - BALL_SIZE)
    y = random.randrange(BALL_SIZE, HEIGHT - BALL_SIZE)
    color = rand_color()
    change_x = 1
    change_y = 1
    return Ball(x, y, change_x, change_y, color, BALL_SIZE)


def collision(x, y):
    """Check if a ball collides with the wall."""
    if x - BALL_SIZE < 0 or x + BALL_SIZE > WIDTH:
        return 1  # X-axis collision
    if y - BALL_SIZE < 0 or y + BALL_SIZE > HEIGHT:
        return 0  # Y-axis collision


def main(collision_range):
    """Run the main program loop."""
    pygame.init()
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.display.set_caption("Bouncing Balls")

    done = False
    clock = pygame.time.Clock()
    ball_list = [make_ball()]

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                ball_list.append(make_ball())
                print("Ball Added! There are ", len(ball_list), " total!")

        for ball in ball_list:
            hit = collision(ball.rect.x, ball.rect.y)
            if hit == 1:
                ball.change_x *= -1
            elif hit == 0:
                ball.change_y *= -1
            ball.rect.x += ball.change_x
            ball.rect.y += ball.change_y

        screen.fill(BLACK)
        #pygame.draw.circle(screen, WHITE, (350, 250), collision_range)

        center_x, center_y = pygame.mouse.get_pos()

        for ball in ball_list:
            if distance(ball.rect.x, ball.rect.y, center_x, center_y) < collision_range:
                pygame.draw.line(screen, WHITE, (center_x, center_y), (ball.rect.x, ball.rect.y))

        for ball in ball_list:
            pygame.draw.circle(screen, ball.color, [ball.rect.x, ball.rect.y], BALL_SIZE)

        clock.tick(60)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    collision_range = int(input("Enter a collision range: "))
    main(collision_range)
