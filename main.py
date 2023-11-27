import pygame
import sys
import os
import random
from helper.aspect_scale import aspect_scale

# Initialize Pygame
pygame.init()

# Set up display
window_size = (900, 700)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("player Movement")

#constants
HEALTH_DECREASE_RATE = 0.05
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Initial health value
health = 1.0

# Get the current script's directory
current_dir = os.path.dirname(os.path.realpath(__file__))

image_dir = current_dir + "/assets/images/"
# Load background image
background = pygame.image.load(os.path.join(image_dir,  "galaxy.jpg"))
background = pygame.transform.scale(background, window_size)

# Load original player image facing right
player_left = pygame.image.load(os.path.join(image_dir, "player.png"))
#player_left = pygame.transform.scale(player_left, (150, 150))  # Adjust size as needed
player_left = aspect_scale(player_left, 230, 230)


print(player_left)
# Flip player image to face left
player_right = pygame.transform.flip(player_left, True, False)

# Load oxygen_tank image
oxygen_tank_image = pygame.image.load(os.path.join(image_dir, "oxygen_tank.png"))
oxygen_tank_image = aspect_scale(oxygen_tank_image, 60, 60)

# Initial position of player
player_rect = player_left.get_rect()
player_rect.center = window_size[0] // 2, window_size[1] // 2

# Create a smaller rect for collision detection
player_collision_rect = pygame.Rect(player_rect.x, player_rect.y, 80, 70)

# Set the speed of player
speed = 7

asteroid_speed=9

# Initial direction
direction = "right"

# List to store treat positions
treat_positions = []

# Load font for displaying points
font = pygame.font.Font(None, 36)

points = 0

# Function to render text
def render_text(text, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Create sprite class for the player collision rectangle
class NyanCatCollisionRect(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect

# Create sprite for the player collision rectangle
player_collision_sprite = NyanCatCollisionRect(player_collision_rect)

# Function to spawn asteroid
def spawn_asteroid():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, window_size[0] - asteroid_image.get_width())
        y = -asteroid_image.get_height()
    elif side == "bottom":
        x = random.randint(0, window_size[0] - asteroid_image.get_width())
        y = window_size[1]
    elif side == "left":
        x = -asteroid_image.get_width()
        y = random.randint(0, window_size[1] - asteroid_image.get_height())
    elif side == "right":
        x = window_size[0]
        y = random.randint(0, window_size[1] - asteroid_image.get_height())

    asteroid_rect = pygame.Rect(x, y, asteroid_image.get_width(), asteroid_image.get_height())
    asteroid_positions.append(asteroid_rect)
    asteroid_timers.append(random.randint(200, 500))

# Load asteroid image
asteroid_image = pygame.image.load(os.path.join(image_dir, "asteroid.png"))
asteroid_image = aspect_scale(asteroid_image, 70, 70)

# List to store asteroid positions
asteroid_positions = []
asteroid_timers = []

# Create a sprite group for asteroids
asteroids_group = pygame.sprite.Group()

# Main game loop
clock = pygame.time.Clock()
spawn_timer = 0
spawn_interval = 200
spawn_timer_asteroid = 0
spawn_interval_asteroid = 200
last_time=0

treat_timers = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= speed
        direction = "left"
        # Ensure player stays within the left boundary
        player_rect.x = max(player_rect.x, 0)
    elif keys[pygame.K_RIGHT]:
        player_rect.x += speed
        direction = "right"
        # Ensure player stays within the right boundary
        player_rect.x = min(player_rect.x, window_size[0] - player_rect.width)
    elif keys[pygame.K_UP]:
        player_rect.y -= speed
        # Ensure player stays within the top boundary
        player_rect.y = max(player_rect.y, 0)
    elif keys[pygame.K_DOWN]:
        player_rect.y += speed
        # Ensure player stays within the bottom boundary
        player_rect.y = min(player_rect.y, window_size[1] - player_rect.height)

    # Update the smaller collision rect's position
    player_collision_rect.topleft = (player_rect.x + 40, player_rect.y + 20)

    # Randomly spawn oxygen_tank
    spawn_timer += clock.get_rawtime()
    if spawn_timer >= spawn_interval:
        spawn_timer = 0
        treat_x = random.randint(0, window_size[0] - oxygen_tank_image.get_width())
        treat_y = random.randint(0, window_size[1] - oxygen_tank_image.get_height())
        treat_rect = pygame.Rect(treat_x, treat_y, oxygen_tank_image.get_width(), oxygen_tank_image.get_height())

        # Check if player is not at the treat location and there are no other oxygen_tank there
        if (
            not player_rect.colliderect(treat_rect)
            and not any(treat_rect.colliderect(existing_treat) for existing_treat in treat_positions)
        ):
            treat_positions.append(treat_rect)
            # Add a timer for the treat (5 to 7 seconds)
            treat_timers.append(random.randint(300, 700))

    # Draw background and player
    screen.blit(background, (0, 0))

    # Draw oxygen_tank and update timers
    for i in range(len(treat_positions)):
        screen.blit(oxygen_tank_image, treat_positions[i])
        treat_timers[i] -= clock.get_rawtime()
        if player_collision_rect.colliderect(treat_positions[i]):
            # Increment points and remove oxygen_tank
            health += 0.1
            treat_positions.pop(i)
            treat_timers.pop(i)
            break
        if treat_timers[i] <= 0:
            # Remove oxygen_tank and its timer when the time is up
            treat_positions.pop(i)
            treat_timers.pop(i)
            break

    # Spawn asteroid
    spawn_timer_asteroid += clock.get_rawtime()
    if spawn_timer_asteroid >= spawn_interval_asteroid:
        spawn_timer_asteroid = 0
        spawn_asteroid()

    # Move asteroids and update timers
    for i in range(len(asteroid_positions)):
        asteroid_positions[i].x += asteroid_speed * 2  # Adjust the speed as needed
        screen.blit(asteroid_image, asteroid_positions[i])
        asteroid_timers[i] -= clock.get_rawtime()
        if asteroid_timers[i] <= 0:
            # Remove asteroid and its timer when the time is up
            asteroid_positions.pop(i)
            asteroid_timers.pop(i)
            break

    # Update sprite group with asteroid positions
    asteroids_group.empty()
    for asteroid_rect in asteroid_positions:
        asteroid_sprite = pygame.sprite.Sprite()
        asteroid_sprite.rect = asteroid_rect
        asteroids_group.add(asteroid_sprite)

    # Check for collision with asteroids
    if pygame.sprite.spritecollide(player_collision_sprite, asteroids_group, False):
        # Display game over text
        game_over_text = pygame.font.Font(None, 72).render("Game Over", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(window_size[0] // 2, window_size[1] // 2))
        screen.blit(game_over_text, game_over_rect)
        pygame.display.flip()

        # Wait for a few seconds before quitting
        pygame.time.delay(3000)  # 3000 milliseconds (3 seconds)
        pygame.quit()
        sys.exit()

    # Draw player
    if direction == "right":
        player = player_right
    else:
        player = player_left

    screen.blit(player, player_rect)

    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - last_time
    last_time = current_time
    health -= HEALTH_DECREASE_RATE * (elapsed_time / 1000.0)

    # Cap the health value
    health = max(health, 0.0)

    # Draw health bar background
    pygame.draw.rect(screen, WHITE, (10, 10, 200, 30))

    # Draw health bar fill
    pygame.draw.rect(screen, RED, (10, 10, 200 * health, 30))

    # Draw health percentage
    text = font.render(f"{int(health * 100)}%", True, WHITE)

    screen.blit(text, (220, 15))

    # Update display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)
