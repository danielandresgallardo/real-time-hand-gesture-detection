import pygame
import cv2
import platform
import os
import time

def run_hud(queue, stop_event):
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    pygame.display.set_caption("Futuristic HUD")

    # Load blurred driving video
    cap = cv2.VideoCapture("assets/video.mp4")
    if not cap.isOpened():
        print("\u274c Failed to open video. Exiting.")
        return

    font = pygame.font.SysFont("Arial", 36)
    GREEN = (0, 255, 0)

    # Music state
    songs = ["Never Gonna Give You Up", "Blinding Lights", "Interstellar OST"]
    current_song = 0
    playing = True
    last_command_time = 0

    clock = pygame.time.Clock()

    def draw_hud():
        pygame.draw.rect(screen, (20, 20, 20), (50, HEIGHT - 150, 500, 80), border_radius=12)
        status = "▶️" if playing else "⏸️"
        title = f"{status} {songs[current_song]}"
        text = font.render(title, True, GREEN)
        screen.blit(text, (60, HEIGHT - 130))

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
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))

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

        # Bring window to front (optional)
        if platform.system() == "Darwin":
            os.system("osascript -e 'tell application \"System Events\" to set frontmost of process \"Python\" to true'")
        elif platform.system() == "Windows":
            import ctypes
            hwnd = pygame.display.get_wm_info()["window"]
            ctypes.windll.user32.SetForegroundWindow(hwnd)