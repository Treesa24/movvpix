import cv2
import pygame
import time
import numpy as np
from audio_engine import get_beat_times
from hand_tracking import FingerTracker

# --- CONFIGURATION ---
SONG_PATH = "assets/songs/song.mp3"
HIT_PATH = "assets/sounds/hit.wav"
TILE_COLOR = (20, 20, 20)      # Sleek Black
BORDER_COLOR = (0, 255, 255)   # Cyan border for AR look
TEXT_COLOR = (255, 255, 255)

def reset_game():
    global spawn_times, tiles, score, start_time, game_active
    try:
        pygame.mixer.music.load(SONG_PATH)
        print("Music loaded successfully.")
    except pygame.error as e:
        print(f"Error loading music: {e}")
        return 
        
    spawn_times = get_beat_times(SONG_PATH)
    tiles = []
    score = 0
    start_time = time.time()
    game_active = True
    
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.1) # Music stays quiet until hit

# --- INITIALIZATION ---
pygame.mixer.init()
tracker = FingerTracker()
hit_sound = pygame.mixer.Sound(HIT_PATH)
cap = cv2.VideoCapture(0)

reset_game()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    overlay = frame.copy()
    
    if game_active:
        elapsed = time.time() - start_time
        
        # 1. Spawn Tiles
        if spawn_times and elapsed >= spawn_times[0]:
            lane = np.random.randint(0, 4)
            tiles.append({'x': lane * (w//4), 'y': -150, 'w': w//4, 'h': 180, 'active': True})
            spawn_times.pop(0)

        # 2. Track Finger
        finger_pos = tracker.get_position(frame)

        # 3. Update & Draw Tiles
        for tile in tiles[:]:
            tile['y'] += 15 # Faster speed for more fun
            
            # Draw Transparent Body
            cv2.rectangle(overlay, (tile['x'], tile['y']), 
                         (tile['x'] + tile['w'], tile['y'] + tile['h']), TILE_COLOR, -1)
            # Draw Neon Border
            cv2.rectangle(overlay, (tile['x'], tile['y']), 
                         (tile['x'] + tile['w'], tile['y'] + tile['h']), BORDER_COLOR, 3)

            if finger_pos and tile['active']:
                tx, ty, tw, th = tile['x'], tile['y'], tile['w'], tile['h']
                if tx < finger_pos[0] < tx + tw and ty < finger_pos[1] < ty + th:
                    # --- REACTIVE MUSIC LOGIC ---
                    hit_sound.play()
                    pygame.mixer.music.set_volume(1.0) # Boost song volume on hit
                    score += 1
                    tile['active'] = False
                    tiles.remove(tile)
            
            elif tile['y'] > h:
                game_active = False 
                pygame.mixer.music.stop()

        # Fade music back down if no tile is being hit
        current_vol = pygame.mixer.music.get_volume()
        if current_vol > 0.1:
            pygame.mixer.music.set_volume(current_vol - 0.05)

        # Apply Transparency
        frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
        
        # Improved UI Text
        cv2.putText(frame, f"SCORE: {score}", (40, 70), 
                    cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 0, 0), 5) # Shadow
        cv2.putText(frame, f"SCORE: {score}", (40, 70), 
                    cv2.FONT_HERSHEY_TRIPLEX, 1.5, (0, 255, 255), 2) # Cyan text

    else:
        # --- REDO / GAME OVER UI ---
        cv2.rectangle(frame, (w//4, h//3), (3*w//4, 2*h//3), (20, 20, 20), -1)
        cv2.putText(frame, "REDO?", (w//2-60, h//2-10), 
                    cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 255, 255), 2)
        cv2.putText(frame, "Press 'R' to Restart", (w//2-120, h//2+40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    cv2.imshow("AR Magic Tiles - MEC Project", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('r'): reset_game()

cap.release()
cv2.destroyAllWindows()