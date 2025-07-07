import pygame
import platform
import os
import time

def run_hud(queue, stop_event):
    pygame.init()
    SCALE = 2
    WIDTH, HEIGHT = 463 * SCALE, 260 * SCALE
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Futuristic HUD")

    # Load and scale static image
    bg_image = pygame.image.load("car_pov.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    font = pygame.font.SysFont("Arial", 24 * SCALE // 2)
    command_font = pygame.font.SysFont("Arial", 36 * SCALE // 2)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)

    # Music state
    songs = ["Never Gonna Give You Up", "Blinding Lights", "Interstellar OST"]
    current_song = 0
    playing = True
    last_command_time = 0

    command_display = None
    command_timestamp = 0

    clock = pygame.time.Clock()

    def draw_music_hud():
        hud_width = 440 * SCALE // 2
        hud_height = 40 * SCALE // 2
        hud_x = 20  # Top left of windshield
        hud_y = 10
        pygame.draw.rect(screen, (20, 20, 20), (hud_x, hud_y, hud_width, hud_height), border_radius=12)
        status = "\u25b6\ufe0f" if playing else "\u23f8\ufe0f"
        title = f"{status} {songs[current_song]}"
        text = font.render(title, True, GREEN)
        screen.blit(text, (hud_x + 10, hud_y + 5))

    def draw_command_overlay():
        nonlocal command_display, command_timestamp
        if not command_display:
            return
        elapsed = time.time() - command_timestamp
        if elapsed > 1.0:
            command_display = None
            return
        alpha = 255 * (1.0 - abs(elapsed - 0.5) * 2)  # Fade in/out over 1 second
        alpha = max(0, min(255, int(alpha)))
        overlay_surface = command_font.render(command_display, True, WHITE)
        overlay_surface.set_alpha(alpha)
        overlay_rect = overlay_surface.get_rect(center=(WIDTH // 2, 190))
        screen.blit(overlay_surface, overlay_rect)

    def handle_command(command):
        nonlocal current_song, playing, last_command_time, command_display, command_timestamp
        if time.time() - last_command_time < 0.8:
            return
        if command == 1:
            playing = not playing
            command_display = "Play/Pause"
        elif command == 2:
            current_song = (current_song + 1) % len(songs)
            command_display = "Next Song"
        elif command == 3:
            current_song = (current_song - 1) % len(songs)
            command_display = "Previous Song"
        else:
            command_display = "Unknown Command"
        command_timestamp = time.time()
        last_command_time = time.time()

    while not stop_event.is_set():
        screen.blit(bg_image, (0, 0))

        draw_music_hud()
        draw_command_overlay()

        while not queue.empty():
            cmd = queue.get()
            handle_command(cmd)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
                return

        pygame.display.update()
        clock.tick(30)