import pygame
import time
import sys
from player import player
from enemy import enemy as e
import random

pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mixer.music.load("tet.mp3")
pygame.mixer.music.play(-1)
# Screen size
size = width, height = 900, 900
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
l_font = pygame.font.Font(None, 60)
n = 15
# Colors
running = True
obstacles = set()
blacklisted_locations = set()
score = 0
black = (0, 0, 0)
white = (255, 255, 255)
enemy_turn = False
screen = pygame.display.set_mode(size)
board_size = 41
board = [[None] * board_size] * board_size
user = player((20, 0), None)
enemy = e((20, 40))
dt = 0
playing = False
button_color = "orange"
game_over = False

while True:
    screen.fill(white)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    if not playing and not game_over:
        # Draw title

        title = l_font.render("TAG", True, "orange")
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 95)
        screen.blit(title, titleRect)

        # Draw buttons
        playButton = pygame.Rect((width / 4), (height / 2), width / 2, 50)
        play = font.render("Play", True, white)
        mouse = pygame.mouse.get_pos()
        if playButton.collidepoint(mouse):
            button_color = "yellow"
        else:
            button_color = "orange"
        playRect = play.get_rect()
        playRect.center = playButton.center
        pygame.draw.rect(screen, button_color, playButton)
        screen.blit(play, playRect)

        # Check if button is clicked
        click = pygame.mouse.get_pressed()
        if playButton.collidepoint(mouse):
            if click[0]:
                time.sleep(0.2)
                playing = True
    elif playing:
        # Draw game board
        tile_size = width / board_size
        tile_origin = (0, 0)
        tiles = []
        for i in range(board_size):
            row = []
            for j in range(board_size):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size,
                    tile_size,
                )
                if (i, j) == user.location:
                    # Draw Player character
                    pygame.draw.rect(screen, "green", rect)
                elif (i, j) == enemy.location:
                    # Draw Enemy
                    pygame.draw.rect(screen, "red", rect)
                elif (i, j) in obstacles:
                    # Draw Obstacle
                    pygame.draw.rect(screen, "black", rect)
                else:
                    pygame.draw.rect(screen, "orange", rect, 1)
                row.append(rect)
            tiles.append(row)
        # Movement keys for player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            user.direction = "Up"
        if keys[pygame.K_s]:
            user.direction = "Down"
        if keys[pygame.K_a]:
            user.direction = "Left"
        if keys[pygame.K_d]:
            user.direction = "Right"
        moving = user.move_player(obstacles)
        enemy.move(user.location, user.direction, obstacles, moving)

        score += 10
        # Framerate
        dt = clock.tick(30) / 1000
        if user.location == enemy.location:
            game_over = True
        if score > 0 and score % 100 == 0:
            # Generates obstacles on board
            obstacles.add((random.randint(0, 40), random.randint(0, 40)))
    if game_over:
        playing = False
        againButton = pygame.Rect(width / 4, height / 2, width / 2, 50)
        mouse = pygame.mouse.get_pos()
        score_text = l_font.render(f"Score: {score}", True, "orange")
        text_rect = score_text.get_rect(center=(width / 2, 60))
        screen.blit(score_text, text_rect)
        if againButton.collidepoint(mouse):
            a_color = "yellow"
        else:
            a_color = "orange"
        again = font.render("Play Again", True, white)
        againRect = again.get_rect()
        againRect.center = againButton.center
        pygame.draw.rect(screen, a_color, againButton)
        screen.blit(again, againRect)
        quitButton = pygame.Rect(width / 4, (height / 2 + 80), width / 2, 50)
        mouse = pygame.mouse.get_pos()
        if quitButton.collidepoint(mouse):
            q_color = "yellow"
        else:
            q_color = "orange"
        quit = font.render("Quit", True, white)
        quitRect = quit.get_rect()
        quitRect.center = quitButton.center
        pygame.draw.rect(screen, q_color, quitButton)
        screen.blit(quit, quitRect)
        click = pygame.mouse.get_pressed()
        if click[0]:
            mouse = pygame.mouse.get_pos()
            if againButton.collidepoint(mouse):
                time.sleep(0.2)
                obstacles.clear()
                user.location = (20, 0)
                enemy.location = (20, 40)
                user.direction = None
                playing = True
                game_over = False
                score = 0
            mouse = pygame.mouse.get_pos()
            if quitButton.collidepoint(mouse):
                break

    pygame.display.flip()
pygame.quit()
