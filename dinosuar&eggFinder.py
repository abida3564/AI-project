# Setup and Initialization
import pygame
import random
from heapq import heappush, heappop
from time import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600  # Window size
GRID_SIZE = 20  # Size of each cell
ROWS, COLS = 30, 40  # Grid dimensions
FPS = 10
TIME_LIMIT = 60  # Time limit in seconds
NUM_EGGS = 10  # Total eggs to find
OBSTACLE_COUNT = 70  # Number of obstacles

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dinosaur and Egg Finder")
clock = pygame.time.Clock()

# Directions for movement
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Grid and positions
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
dino_pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
eggs = set()
while len(eggs) < NUM_EGGS:
    egg_pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
    if egg_pos != dino_pos:
        eggs.add(egg_pos)
obstacles = set((random.randint(0, ROWS - 1), random.randint(0, COLS - 1)) for _ in range(OBSTACLE_COUNT))
obstacles.difference_update(eggs)
obstacles.discard(dino_pos)

# Initialize score
score = 0

# Drawing and Helper Functions
def draw_grid(offset_x, offset_y):
    """Draw the grid, dinosaur, eggs, and obstacles."""
    screen.fill(WHITE)

    # Draw grid lines
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * GRID_SIZE - offset_x, row * GRID_SIZE - offset_y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Draw obstacles
    for obstacle in obstacles:
        rect = pygame.Rect(obstacle[1] * GRID_SIZE - offset_x, obstacle[0] * GRID_SIZE - offset_y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, BLACK, rect)

    # Draw eggs
    for egg in eggs:
        rect = pygame.Rect(egg[1] * GRID_SIZE - offset_x, egg[0] * GRID_SIZE - offset_y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, YELLOW, rect)

    # Draw dinosaur
    rect = pygame.Rect(dino_pos[1] * GRID_SIZE - offset_x, dino_pos[0] * GRID_SIZE - offset_y, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, GREEN, rect)

    # Draw score
    font = pygame.font.SysFont(None, 30)
    score_text = font.render(f"Score: {score}", True, RED)
    screen.blit(score_text, (10, 10))

def heuristic(a, b):
    """Heuristic function for A* (Manhattan distance)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start, goal):
    """A* Algorithm for pathfinding."""
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for direction in DIRECTIONS:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if (
                0 <= neighbor[0] < ROWS
                and 0 <= neighbor[1] < COLS
                and neighbor not in obstacles
            ):
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))

    return []  # Return an empty path if no path exists

# Game Mechanics
def move_dino(path):
    """Move the dinosaur along the calculated path."""
    global dino_pos
    if path:
        dino_pos = path.pop(0)

def move_obstacles():
    """Move obstacles randomly."""
    for obstacle in list(obstacles):
        if random.random() < 0.3:  # 30% chance to move
            obstacles.remove(obstacle)
            new_obstacle = (
                obstacle[0] + random.choice([-1, 0, 1]),
                obstacle[1] + random.choice([-1, 0, 1]),
            )
            if (
                0 <= new_obstacle[0] < ROWS
                and 0 <= new_obstacle[1] < COLS
                and new_obstacle not in obstacles
                and new_obstacle not in eggs
                and new_obstacle != dino_pos
            ):
                obstacles.add(new_obstacle)

# Main game loop
start_time = time()
running = True
while running:
    elapsed_time = time() - start_time
    offset_x = max(0, dino_pos[1] * GRID_SIZE - WIDTH // 2)
    offset_y = max(0, dino_pos[0] * GRID_SIZE - HEIGHT // 2)

    draw_grid(offset_x, offset_y)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if elapsed_time > TIME_LIMIT:
        print(f"Time's up! Game Over! Final Score: {score}")
        running = False

    # Find the nearest egg
    if eggs:
        nearest_egg = min(eggs, key=lambda egg: heuristic(dino_pos, egg))
        path = a_star_search(dino_pos, nearest_egg)

        # Move dinosaur along the path
        move_dino(path)

        # Check if the dinosaur has reached the egg
        if dino_pos == nearest_egg:
            eggs.remove(nearest_egg)
            score += 1  # Increase score when egg is found
            if not eggs:
                print(f"All eggs found! You win! Final Score: {score}")
                running = False
    else:
        print(f"All eggs found! You win! Final Score: {score}")
        running = False

    # Move obstacles
    move_obstacles()

    clock.tick(FPS)

pygame.quit()
