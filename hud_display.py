import pygame
import platform
import time
import math

def run_hud(queue, stop_event):
    pygame.init()
    SCALE = 2
    WIDTH, HEIGHT = 463 * SCALE, 260 * SCALE
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Futuristic HUD")

    bg_image = pygame.image.load("car_pov.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    font = pygame.font.SysFont("Arial", 24 * SCALE // 2)
    command_font = pygame.font.SysFont("Arial", 36 * SCALE // 2)
    speed_font = pygame.font.SysFont("Arial", 18 * SCALE // 2)
    speed_unit_font = pygame.font.SysFont("Arial", 14 * SCALE // 2)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 128, 255)

    songs = ["Never Gonna Give You Up", "Blinding Lights", "Interstellar OST"]
    current_song = 0
    playing = True
    last_command_time = 0
    speed = 65

    command_display = None
    command_timestamp = 0
    cursor_pos = None

    # Circle interaction variables
    circle_center = (400, 200)
    circle_radius = 20
    hover_start_time = None
    loading_complete = False

    clock = pygame.time.Clock()

    def draw_music_hud():
        hud_width = 440 * SCALE // 2
        hud_height = 40 * SCALE // 2
        hud_x = 20
        hud_y = 10
        pygame.draw.rect(screen, (20, 20, 20), (hud_x, hud_y, hud_width, hud_height), border_radius=12)
        status = "▶" if playing else "⏸"
        title = f"{status} {songs[current_song]}"
        text = font.render(title, True, GREEN)
        screen.blit(text, (hud_x + 10, hud_y + 5))

    def draw_speedometer():
        center_x = (127 + (316 - 127) // 2) * SCALE
        center_y = 150 * SCALE
        radius = 25
        pygame.draw.circle(screen, (30, 30, 30), (center_x, center_y), radius)
        pygame.draw.circle(screen, GREEN, (center_x, center_y), radius, 2)
        speed_text = speed_font.render(str(speed), True, WHITE)
        unit_text = speed_unit_font.render("km/h", True, GREEN)
        screen.blit(speed_text, (center_x - speed_text.get_width() // 2, center_y - 12))
        screen.blit(unit_text, (center_x - unit_text.get_width() // 2, center_y + 5))

    def draw_command_overlay():
        nonlocal command_display, command_timestamp
        if not command_display:
            return
        elapsed = time.time() - command_timestamp
        if elapsed > 1.0:
            command_display = None
            return
        alpha = 255 * (1.0 - abs(elapsed - 0.5) * 2)
        alpha = max(0, min(255, int(alpha)))
        overlay_surface = command_font.render(command_display, True, WHITE)
        overlay_surface.set_alpha(alpha)
        overlay_rect = overlay_surface.get_rect(center=(WIDTH // 2, 190))
        screen.blit(overlay_surface, overlay_rect)

    def draw_cursor():
        if cursor_pos:
            pygame.draw.circle(screen, GREEN, cursor_pos, 8)

    def draw_interactive_circle():
        nonlocal hover_start_time, loading_complete

        mouse_hovering = cursor_pos and math.dist(cursor_pos, circle_center) <= circle_radius

        # State: not hovering
        if not mouse_hovering:
            if loading_complete:
                loading_complete = False
            hover_start_time = None
            pygame.draw.circle(screen, BLUE, circle_center, circle_radius)
            return

        # State: hovering
        if hover_start_time is None:
            hover_start_time = time.time()

        elapsed = time.time() - hover_start_time

        if elapsed >= 1.0:
            loading_complete = True
            pygame.draw.circle(screen, GREEN, circle_center, circle_radius)
        else:
            pygame.draw.circle(screen, BLUE, circle_center, circle_radius)
            draw_loading_arc(circle_center, circle_radius + 6, elapsed / 1.0)

    def draw_loading_arc(center, radius, progress):
        end_angle = int(progress * 360)
        for angle in range(0, end_angle, 3):
            radians = math.radians(angle - 90)
            x = int(center[0] + radius * math.cos(radians))
            y = int(center[1] + radius * math.sin(radians))
            pygame.draw.circle(screen, BLUE, (x, y), 2)

    def handle_command(command):
        nonlocal current_song, playing, last_command_time, command_display, command_timestamp, cursor_pos
        if isinstance(command, tuple) and command[0] == "cursor":
            _, x, y = command
            cursor_pos = (x * SCALE, y * SCALE)
            return

        cursor_pos = None  # Clear cursor when not pointing

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
            return
        command_timestamp = time.time()
        last_command_time = time.time()

    while not stop_event.is_set():
        screen.blit(bg_image, (0, 0))

        draw_music_hud()
        draw_speedometer()
        draw_command_overlay()
        draw_cursor()
        draw_interactive_circle()

        while not queue.empty():
            cmd = queue.get()
            handle_command(cmd)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
                return

        pygame.display.update()
        clock.tick(30)