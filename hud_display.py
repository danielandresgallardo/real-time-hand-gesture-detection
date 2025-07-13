import pygame
import platform
import time

class KalmanFilter2D:
    def __init__(self, process_noise=1e-3, measurement_noise=1e-2):
        self.x = 0
        self.y = 0
        self.estimate_error_x = 1
        self.estimate_error_y = 1
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

    def update(self, measured_x, measured_y):
        kalman_gain_x = self.estimate_error_x / (self.estimate_error_x + self.measurement_noise)
        kalman_gain_y = self.estimate_error_y / (self.estimate_error_y + self.measurement_noise)

        self.x += kalman_gain_x * (measured_x - self.x)
        self.y += kalman_gain_y * (measured_y - self.y)

        self.estimate_error_x = (1 - kalman_gain_x) * self.estimate_error_x + abs(self.x) * self.process_noise
        self.estimate_error_y = (1 - kalman_gain_y) * self.estimate_error_y + abs(self.y) * self.process_noise

        return int(self.x), int(self.y)

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
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 120, 255)
    RED = (255, 60, 60)

    songs = ["Never Gonna Give You Up", "Blinding Lights", "Interstellar OST"]
    current_song = 0
    playing = True
    last_command_time = 0
    speed = 65

    command_display = None
    command_timestamp = 0
    cursor_pos = None
    kf = KalmanFilter2D()

    toggle_circle_pos = (WIDTH - 100, 80)
    toggle_radius = 20
    toggle_hover_start = None
    toggle_ready = True
    hover_duration = 1.0
    hover_completed = False
    modes = ["Eco", "Normal", "Sport"]
    colors = [GREEN, BLUE, RED]
    current_mode = 0

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

    def draw_toggle_button():
        nonlocal toggle_hover_start, toggle_ready, current_mode, hover_completed
        cursor_over = False
        if cursor_pos:
            dx = cursor_pos[0] - toggle_circle_pos[0]
            dy = cursor_pos[1] - toggle_circle_pos[1]
            dist = (dx**2 + dy**2) ** 0.5
            if dist <= toggle_radius:
                cursor_over = True

        if cursor_over:
            if toggle_ready:
                if not toggle_hover_start:
                    toggle_hover_start = time.time()
                    hover_completed = False
                elif not hover_completed:
                    elapsed = time.time() - toggle_hover_start
                    if elapsed >= hover_duration:
                        current_mode = (current_mode + 1) % len(modes)
                        hover_completed = True
                        toggle_ready = False
                        toggle_hover_start = None
                        print(f"Mode switched to {modes[current_mode]}")
            else:
                toggle_hover_start = None
        else:
            toggle_hover_start = None
            toggle_ready = True
            hover_completed = False

        color = colors[current_mode]
        pygame.draw.circle(screen, color, toggle_circle_pos, toggle_radius)

        if toggle_hover_start and not hover_completed:
            elapsed = time.time() - toggle_hover_start
            progress = min(elapsed / hover_duration, 1.0)
            pygame.draw.arc(
                screen,
                WHITE,
                (
                    toggle_circle_pos[0] - toggle_radius,
                    toggle_circle_pos[1] - toggle_radius,
                    toggle_radius * 2,
                    toggle_radius * 2
                ),
                -0.5 * 3.14,
                (-0.5 + 2 * progress) * 3.14,
                4
            )

        label = font.render(modes[current_mode], True, WHITE)
        screen.blit(label, (toggle_circle_pos[0] - label.get_width() // 2, toggle_circle_pos[1] + toggle_radius + 5))

    def handle_command(command):
        nonlocal current_song, playing, last_command_time, command_display, command_timestamp, cursor_pos
        if isinstance(command, tuple) and command[0] == "cursor":
            _, x, y = command
            smooth_x, smooth_y = kf.update(x * SCALE, y * SCALE)
            cursor_pos = (smooth_x, smooth_y)
            return

        cursor_pos = None

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
        draw_toggle_button()
        draw_cursor()

        while not queue.empty():
            cmd = queue.get()
            handle_command(cmd)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
                return

        pygame.display.update()
        clock.tick(30)