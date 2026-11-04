import os
import re
import cv2
import pygame
import math


pygame.init()
pygame.mixer.init()

WIDTH = 1100
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Spotify Lyrics Player - Clean")

clock = pygame.time.Clock()


BG_BLACK = (12, 12, 12)
SPOTIFY_GREEN = (29, 185, 84)
PURE_WHITE = (255, 255, 255)
DIM_GRAY = (160, 160, 160)


FONT_DIR = "assets/fonts"

def get_font(font_name, size):
    path = os.path.join(FONT_DIR, font_name)
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("arial", size)

font_title  = get_font("Poppins-Bold.ttf", 24)       
font_artist = get_font("Poppins-medium.ttf", 16)     
font_active = get_font("Poppins-Bold.ttf", 30)       
font_normal = get_font("Poppins-medium.ttf", 20)     
font_small  = get_font("Poppins-medium.ttf", 14)     
font_time   = get_font("Poppins-medium.ttf", 12)     

# --- 
MUSIC_PATH = "assets/music/imissyou.mp3"
LYRICS_PATH = "lyrics/lyrics.lrc"
VIDEO_BG_PATH = "assets/video/tes.mov"


# LOAD LYRICS

def load_lyrics(path):
    lyrics = []
    if not os.path.exists(path):
        print("File lirik tidak ditemukan!")
        return lyrics

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            match = re.match(r"\[(\d{2}):(\d{2})(?:\.(\d{1,3}))?\](.*)", line)
            if match:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                fraction = match.group(3) or "0"
                milliseconds = int(fraction.ljust(3, "0"))
                timestamp = minutes * 60 + seconds + milliseconds / 1000
                text = match.group(4).strip()
                if text:
                    lyrics.append((timestamp, text))
    return sorted(lyrics, key=lambda item: item[0])

lyrics = load_lyrics(LYRICS_PATH)


# MUSIC & VIDEO SETUP

if not os.path.exists(MUSIC_PATH):
    raise FileNotFoundError(f"File musik tidak ditemukan: {MUSIC_PATH}")

pygame.mixer.music.load(MUSIC_PATH)
try:
    music_duration = pygame.mixer.Sound(MUSIC_PATH).get_length()
except:
    music_duration = 180.0  # Fallback default 

video_cap = None
video_fps = 30.0

if os.path.exists(VIDEO_BG_PATH):
    video_cap = cv2.VideoCapture(VIDEO_BG_PATH)
    fps_read = video_cap.get(cv2.CAP_PROP_FPS)
    if fps_read > 0:
        video_fps = fps_read

frame_delay = 1.0 / video_fps
last_frame_time = 0.0
current_video_surface = None


# 1. Vignette Effect (Gelap di tepi, transparan di tengah)
vignette_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for radius in range(440, 0, -10):
    alpha = int(200 * (1 - (radius / 440))) 
    pygame.draw.circle(vignette_surface, (0, 0, 0, alpha), (WIDTH//2, HEIGHT//2), radius)

# Status 
playing = False
is_delaying = False
delay_start_time = 0
DELAY_SECONDS = 0.13

start_time = 0
paused_at = 0
current_time = 0

scroll_y = 0.0
time_offset = 0.0


# HELPER FUNCTIONS
def draw_text_with_shadow(text, font, color, x, y, center=True, alpha=255, shadow_color=(0, 0, 0, 180)):
    """Render teks """
    # Render shadow
    shadow_surf = font.render(text, True, (shadow_color[0], shadow_color[1], shadow_color[2]))
    shadow_surf.set_alpha(min(255, alpha))
    shadow_rect = shadow_surf.get_rect()
    if center:
        shadow_rect.center = (x + 2, y + 3)
    else:
        shadow_rect.topleft = (x + 2, y + 3)
    screen.blit(shadow_surf, shadow_rect)
    
    # Render main 
    main_surf = font.render(text, True, color)
    main_surf.set_alpha(min(255, alpha))
    main_rect = main_surf.get_rect()
    if center:
        main_rect.center = (x, y)
    else:
        main_rect.topleft = (x, y)
    screen.blit(main_surf, main_rect)

def draw_glow_text(text, font, color, x, y, alpha=255):
    """Render teks dengan efek glow (cahaya) untuk lirik aktif"""
    # Glow layers
    for offset in [(0, -3), (0, 3), (-3, 0), (3, 0), (-2, -2), (2, 2)]:
        glow_surf = font.render(text, True, color)
        glow_surf.set_alpha(int(alpha * 0.15))
        glow_rect = glow_surf.get_rect(center=(x + offset[0], y + offset[1]))
        screen.blit(glow_surf, glow_rect)
    
    # Main text
    draw_text_with_shadow(text, font, PURE_WHITE, x, y, center=True, alpha=alpha)

def format_time(seconds):
    """Format detik ke MM:SS"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def get_current_lyric(current_time):
    index = -1
    for i, (timestamp, text) in enumerate(lyrics):
        if current_time >= timestamp:
            index = i
        else:
            break
    return index


# MAIN LOOP
running = True

while running:
    now_time = pygame.time.get_ticks() / 1000.0

    # 1. RENDER VIDEO BACKGROUND (Dengan Blur Aesthetic)
    if video_cap and video_cap.isOpened():
        if now_time - last_frame_time >= frame_delay:
            last_frame_time = now_time
            ret, frame = video_cap.read()

            if not ret:
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = video_cap.read()

            if ret:
                # Teknik blur cepat: downscale lalu upscale
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                small = cv2.resize(frame, (WIDTH // 4, HEIGHT // 4), interpolation=cv2.INTER_LINEAR)
                blurred = cv2.resize(small, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
                
                current_video_surface = pygame.image.frombuffer(
                    blurred.tobytes(), (WIDTH, HEIGHT), "RGB"
                )

        if current_video_surface:
            screen.blit(current_video_surface, (0, 0))
        else:
            screen.fill(BG_BLACK)
    else:
        screen.fill(BG_BLACK)

    # 2. RENDER OVERLAYS (Vignette & Dark Base)
    # Base gelap transparan (sedikit lebih gelap karena tidak ada panel kaca)
    dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dark_overlay.fill((8, 8, 8, 200)) 
    screen.blit(dark_overlay, (0, 0))
    screen.blit(vignette_surface, (0, 0)) 

    # 3. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if is_delaying:
                    is_delaying = False
                    playing = False
                elif not playing:
                    if paused_at > 0:
                        pygame.mixer.music.unpause()
                        start_time = pygame.time.get_ticks() - int(paused_at * 1000)
                        playing = True
                    else:
                        is_delaying = True
                        delay_start_time = pygame.time.get_ticks()
                else:
                    pygame.mixer.music.pause()
                    paused_at = current_time
                    playing = False
            elif event.key == pygame.K_r:
                pygame.mixer.music.stop()
                is_delaying = True
                delay_start_time = pygame.time.get_ticks()
                paused_at = 0
                current_time = 0
                playing = False
            elif event.key == pygame.K_LEFT:
                time_offset -= 0.5
            elif event.key == pygame.K_RIGHT:
                time_offset += 0.5
            elif event.key == pygame.K_ESCAPE:
                running = False

    # 4. LOGIKA JEDA & WAKTU
    countdown_val = 0
    if is_delaying:
        elapsed_delay = (pygame.time.get_ticks() - delay_start_time) / 1000
        if elapsed_delay >= DELAY_SECONDS:
            is_delaying = False
            playing = True
            pygame.mixer.music.play()
            start_time = pygame.time.get_ticks()
        else:
            countdown_val = int(DELAY_SECONDS - elapsed_delay) + 1

    if playing:
        raw_time = (pygame.time.get_ticks() - start_time) / 1000
        current_time = max(0, raw_time + time_offset)

    # 5. RENDER HEADER (Informasi Lagu)
    draw_text_with_shadow("NOW PLAYING", font_small, SPOTIFY_GREEN, WIDTH // 2, 45, alpha=200)
    draw_text_with_shadow("Merry Christmas I Miss You", font_title, PURE_WHITE, WIDTH // 2, 80)
    draw_text_with_shadow("Alex Crichton", font_artist, DIM_GRAY, WIDTH // 2, 112)

    # 6. RENDER LIRIK (Tanpa Panel Kaca, Spasi Diperkecil)
    current_index = get_current_lyric(current_time)
    LINE_HEIGHT = 50  # Diperkecil dari 70
    CENTER_Y = 350    # Disesuaikan agar lebih tengah

    # Smooth scrolling dengan easing
    if current_index >= 0:
        target_scroll = current_index * LINE_HEIGHT
    else:
        target_scroll = 0
    
    scroll_y += (target_scroll - scroll_y) * 0.12  # Easing sedikit lebih responsif

    if lyrics:
        for i, (timestamp, text) in enumerate(lyrics):
            y_pos = CENTER_Y + (i * LINE_HEIGHT - scroll_y)

            # Hanya render jika berada di area yang terlihat
            if 180 <= y_pos <= 550:
                dist_from_center = abs(y_pos - CENTER_Y)
                fade_factor = max(0.0, 1.0 - (dist_from_center / 180.0))
                
                if i == current_index:
                    # Efek pulse halus untuk lirik aktif
                    pulse = (math.sin(now_time * 3) * 0.1) + 0.9
                    alpha = int(255 * pulse)
                    draw_glow_text(text, font_active, SPOTIFY_GREEN, WIDTH // 2, int(y_pos), alpha=alpha)
                else:
                    color_val = int(180 * fade_factor)
                    color = (color_val, color_val, color_val)
                    alpha = int(160 * fade_factor)
                    draw_text_with_shadow(text, font_normal, color, WIDTH // 2, int(y_pos), alpha=alpha)
    else:
        draw_text_with_shadow("Lyrics will appear here...", font_normal, DIM_GRAY, WIDTH // 2, CENTER_Y)

    # 7. RENDER PROGRESS BAR (Spotify Style)
    bar_width = 500  # Sedikit diperkecil agar proporsional
    bar_x = (WIDTH - bar_width) // 2
    bar_y = 580
    bar_height = 4

    # Background bar
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
    
    # Progress bar
    progress = min(current_time / music_duration, 1.0) if music_duration > 0 else 0
    filled_width = int(bar_width * progress)
    
    if filled_width > 0:
        pygame.draw.rect(screen, SPOTIFY_GREEN, (bar_x, bar_y, filled_width, bar_height), border_radius=10)
        # Glowing dot di ujung progress
        dot_x = bar_x + filled_width
        dot_y = bar_y + (bar_height // 2)
        
        # Outer glow
        pygame.draw.circle(screen, (29, 185, 84, 100), (dot_x, dot_y), 7)
        # Inner dot
        pygame.draw.circle(screen, PURE_WHITE, (dot_x, dot_y), 4)

    # Time labels
    time_current = format_time(current_time)
    time_total = format_time(music_duration)
    
    draw_text_with_shadow(time_current, font_time, DIM_GRAY, bar_x, bar_y + 18, center=False, alpha=180)
    draw_text_with_shadow(time_total, font_time, DIM_GRAY, bar_x + bar_width, bar_y + 18, center=True, alpha=180)

    # 8. STATUS & PETUNJUK
    if is_delaying:
        status = f"STARTING IN {countdown_val}s"
        status_color = PURE_WHITE
    elif playing:
        status = "PLAYING"
        status_color = SPOTIFY_GREEN
    else:
        status = "PAUSED"
        status_color = DIM_GRAY

    draw_text_with_shadow(status, font_small, status_color, WIDTH // 2, 625, alpha=200)
    draw_text_with_shadow("revaldi", font_small, DIM_GRAY, WIDTH // 2, 650, alpha=120)

    pygame.display.flip()
    clock.tick(60)

if video_cap:
    video_cap.release()
pygame.quit()
