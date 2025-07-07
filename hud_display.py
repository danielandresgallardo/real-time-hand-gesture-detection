import pygame
import platform
import os
import time

def run_hud(queue, stop_event):
    pygame.init()
    WIDTH, HEIGHT = 463, 260
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Futuristic HUD")

    # Load static image instead of video
    bg_image = pygame.image.load("car_pov.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    font = pygame.font.SysFont("Arial", 24)
    GREEN = (0, 255, 0)

    # Music state
    songs = ["Never Gonna Give You Up", "Blinding Lights", "Interstellar OST"]
    current_song = 0
    playing = True
    last_command_time = 0

    clock = pygame.time.Clock()

    def draw_hud():
        pygame.draw.rect(screen, (20, 20, 20), (10, HEIGHT - 60, 440, 40), border_radius=12)
        status = "\u25b6\ufe0f" if playing else "\u23f8\ufe0f"
        title = f"{status} {songs[current_song]}"
        text = font.render(title, True, GREEN)
        screen.blit(text, (20, HEIGHT - 50))

    def handle_command(command):
        nonlocal current_song, playing, last_command_time
        if time.time() - last_command_time < 0.8:
            return
        if command == 1:
            playing = not playing
        elif command == 2:
            current_song = (current_song + 1) % len(songs)
        elif command == 3:
            current_song = (current_song - 1) % len(songs)
        last_command_time = time.time()

    while not stop_event.is_set():
        screen.blit(bg_image, (0, 0))
        draw_hud()

        while not queue.empty():
            cmd = queue.get()
            handle_command(cmd)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
                return

        pygame.display.update()
        clock.tick(30)