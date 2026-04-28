import os
import sys
import subprocess
import time
import random
import math
from collections import deque
import threading

# ---------------- STARTUP MENU (Interactive Innovation) ----------------
def startup_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("AI GESTURE MUSIC CONTROLLER")
    print("=" * 60)
    print("SELECT YOUR OPERATIONAL MODE:")
    print("  [1] LOCAL MODE      - Play MP3 files from 'music/' folder")
    print("  [2] UNIVERSAL MODE  - Control Spotify, YouTube, VLC & System")
    print("-" * 60)
    
    choice = input("Enter Mode (1 or 2): ").strip()
    if choice == "2":
        print(">> UNIVERSAL MODE ACTIVATED")
        return True
    else:
        print(">> LOCAL MODE ACTIVATED")
        return False

# ---------------- AUTO-INSTALLER (Innovative Resilience) ----------------
def install_requirements():
    print("Detected missing dependencies. Initializing Auto-Installer...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Installation successful. Restarting...")
        return True
    except Exception as e:
        print(f"Auto-Install failed: {e}")
        return False

try:
    import cv2
    import mediapipe as mp
    import pygame
    import joblib
    import numpy as np
    import pyautogui
    import pyttsx3
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IAudioMeterInformation
    from mutagen.mp3 import MP3
except ImportError:
    if install_requirements():
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        print("CRITICAL: Dependencies could not be installed. Please run: pip install -r requirements.txt")
        sys.exit(1)

# ---------------- SYSTEM CONTROL SETUP ----------------
# Voice Engine (Accessibility)
engine = pyttsx3.init()
engine.setProperty('rate', 190) # Speed

def speak(text):
    def run_speech():
        try:
            temp_engine = pyttsx3.init()
            temp_engine.say(text)
            temp_engine.runAndWait()
        except: pass
    threading.Thread(target=run_speech, daemon=True).start()

# Run Startup Menu
universal_mode = startup_menu()
if universal_mode:
    speak("Global mode activated")
else:
    speak("Local mode activated")

# ---------------- MUSIC SETUP ----------------
songs = []
current_song = 0

if not universal_mode:
    pygame.mixer.init()
    music_folder = "music"
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
    songs = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
    if not songs:
        print("Warning: No MP3 files found in 'music/' folder.")
        # Fallback to Universal if no local songs
        universal_mode = True
        print("Falling back to UNIVERSAL MODE.")
    else:
        print(f"Loaded {len(songs)} songs from local treasury.")

# Master Volume Control (pycaw)

# Master Volume & Meter Control (pycaw)
volume_control = None
meter_control = None

def init_system_audio():
    global volume_control, meter_control
    try:
        # Most robust way across pycaw versions: use enumerator directly
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IAudioMeterInformation
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
        
        device_enumerator = AudioUtilities.GetDeviceEnumerator()
        device = device_enumerator.GetDefaultAudioEndpoint(0, 1) # eRender, eMultimedia
        
        # Activate Volume Interface
        try:
            interface_vol = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_control = cast(interface_vol, POINTER(IAudioEndpointVolume))
        except: pass
        
        # Activate Meter Interface (for audio activity detection)
        try:
            interface_meter = device.Activate(IAudioMeterInformation._iid_, CLSCTX_ALL, None)
            meter_control = cast(interface_meter, POINTER(IAudioMeterInformation))
            print("System Audio Meter: ENABLED")
        except: pass
        
    except Exception as e:
        print(f"System Audio setup refined failed: {e}")

init_system_audio()

volume = 0.5
if not universal_mode:
    pygame.mixer.music.set_volume(volume)

song_name = "Universal Controller" if universal_mode else "Initializing..."
song_duration = 0
elapsed_base = 0
last_play_time = 0
is_paused = False
progress = 0
elapsed_time = 0
elapsed_min, elapsed_sec = 0, 0
total_min, total_sec = 0, 0

# ---------------- SHOWCASE STATE (V6.0) ----------------
fps = 0
frame_count = 0
start_time_fps = time.time()
notification_text = "SYSTEM READY"
notification_time = 0
show_skeleton = True

# ---------------- MINI VISUALIZER STATE ----------------
spectrum_bars = 24
spectrum_data = [0.0] * spectrum_bars
visualizer_color = (0, 255, 255) # Cyan

if not universal_mode and songs:
    # Auto-play first song in local mode if desired
    # play_song() 
    pass


# ---------------- MUSIC FUNCTIONS ----------------
def play_song():
    global song_name, song_duration, elapsed_base, last_play_time, is_paused

    if not universal_mode:
        song_name = songs[current_song]
        pygame.mixer.music.load(os.path.join(music_folder, song_name))
        pygame.mixer.music.play()
        audio = MP3(os.path.join(music_folder, song_name))
        song_duration = audio.info.length
    else:
        pyautogui.press('playpause')
        song_name = "Global Media Unit"

    elapsed_base = 0
    last_play_time = time.time()
    is_paused = False
    speak("Playing Track")
    global notification_text, notification_time
    notification_text = "COMMAND: PLAYING TRACK"
    notification_time = time.time()


def pause_song():
    global elapsed_base, last_play_time, is_paused
    if not is_paused:
        if not universal_mode:
            pygame.mixer.music.pause()
        else:
            pyautogui.press('playpause')

        elapsed_base += (time.time() - last_play_time)
        is_paused = True
        speak("Paused")
        global notification_text, notification_time
        notification_text = "COMMAND: PAUSE"
        notification_time = time.time()


def resume_song():
    global last_play_time, is_paused
    if is_paused:
        if not universal_mode:
            pygame.mixer.music.unpause()
        else:
            pyautogui.press('playpause')

        last_play_time = time.time()
        is_paused = False
        speak("Resuming")
        global notification_text, notification_time
        notification_text = "COMMAND: RESUME"
        notification_time = time.time()


def next_song():
    global current_song, notification_text, notification_time
    if not universal_mode:
        current_song = (current_song + 1) % len(songs)
        play_song()
    else:
        pyautogui.press('nexttrack')
        speak("Next track")
    
    # Priority Notification (Overrides generic play_song notification)
    notification_text = "COMMAND: NEXT TRACK"
    notification_time = time.time()


def prev_song():
    global current_song, notification_text, notification_time
    if not universal_mode:
        current_song = (current_song - 1) % len(songs)
        play_song()
    else:
        pyautogui.press('prevtrack')
        speak("Previous track")
    
    # Priority Notification
    notification_text = "COMMAND: PREV TRACK"
    notification_time = time.time()


def shuffle_song():
    global current_song
    current_song = random.randint(0, len(songs) - 1)
    play_song()


def skip_youtube_ad():
    try:
        location = pyautogui.locateCenterOnScreen('skip_ad.png', confidence=0.7)
        if location:
            pyautogui.moveTo(location.x, location.y, duration=0.2)
            pyautogui.click()
            speak("Ad skipped")
            
            global notification_text, notification_time
            notification_text = "COMMAND: SKIP AD"
            notification_time = time.time()
    except Exception as e:
        pass


# ---------------- INNOVATIVE UI (NEON HUD) ----------------
hud_angle = 0
last_scrub_time = 0
last_scrub_x = 0


def draw_neon_hud(frame, wrist_pos, angle, song_name, vol, progress, is_universal):
    x, y = int(wrist_pos[0] * frame.shape[1]), int(wrist_pos[1] * frame.shape[0])

    # Orbiting Rings
    for i in range(3):
        r = 60 + i * 20
        # Draw arcs instead of full circles for tech look
        start_angle = (angle + i * 90) % 360
        cv2.ellipse(frame, (x, y), (r, r), 0, start_angle, start_angle + 120, (255, 0, 255), 2)
        cv2.ellipse(frame, (x, y), (r + 2, r + 2), 0, start_angle + 180, start_angle + 300, (0, 255, 255), 1)

    # Song Info floating near hand
    display_name = "System Unit" if is_universal else song_name[:15]
    cv2.putText(frame, f"{display_name}", (x + 80, y - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Progress Ring (Only in Local Mode)
    if not is_universal:
        cv2.ellipse(frame, (x, y), (50, 50), -90, 0, int(progress * 360), (0, 255, 0), 4)

    # Volume Pulse
    pulse_r = int(40 + math.sin(time.time() * 10) * 5 * vol)
    cv2.circle(frame, (x, y), pulse_r, (255, 255, 255), 1)

    return frame

def draw_help_guide(frame):
    guide = [
        "GESTURE GUIDE:",
        " Palm   -> Play",
        " Fist   -> Pause",
        " Right  -> Next",
        " Left   -> Prev",
        " Thm Up -> Vol Up",
        " Thm Dn -> Vol Down",
    ]
    y_offset = 150
    for i, line in enumerate(guide):
        # Header in Cyan (255, 255, 0), Entries in Green (0, 255, 0)
        color = (255, 255, 0) if i == 0 else (0, 255, 0)
        cv2.putText(frame, line, (frame.shape[1] - 180, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        y_offset += 20

def draw_mini_radar(frame, landmarks):
    """Draws a small technical radar view of the hand landmarks."""
    radar_size = 100
    radar_x = 20
    radar_y = frame.shape[0] - radar_size - 60 # Above notification bar
    
    # Transparency Box
    sub_rect = frame[radar_y:radar_y+radar_size, radar_x:radar_x+radar_size]
    black_rect = np.zeros_like(sub_rect)
    res = cv2.addWeighted(sub_rect, 0.5, black_rect, 0.5, 0)
    frame[radar_y:radar_y+radar_size, radar_x:radar_x+radar_size] = res
    cv2.rectangle(frame, (radar_x, radar_y), (radar_x + radar_size, radar_y + radar_size), (255, 255, 0), 1)
    
    if landmarks and len(landmarks) >= 42:
        # Mini landmarks
        for i in range(0, len(landmarks), 2):
            # Normalization scale
            lx = int(radar_x + radar_size/2 + landmarks[i] * 150)
            ly = int(radar_y + radar_size/2 + landmarks[i+1] * 150)
            # Clip within radar
            lx = np.clip(lx, radar_x+2, radar_x+radar_size-2)
            ly = np.clip(ly, radar_y+2, radar_y+radar_size-2)
            cv2.circle(frame, (lx, ly), 2, (0, 255, 255), -1)
            
    cv2.putText(frame, "MINI_RADAR", (radar_x, radar_y - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1)

def get_procedural_spectrum(is_paused, vol):
    """Generates a fake but attractive spectrum based on time and volume."""
    global spectrum_data
    
    # SYSTEM AUDIO DETECTION (Global Mode Reactivity)
    is_actually_playing = not is_paused
    if universal_mode and meter_control:
        try:
            peak = meter_control.GetPeakValue()
            # If peak is extremely low, assume silence/stop animation
            if peak < 0.0001:
                is_actually_playing = False
        except: pass

    if not is_actually_playing:
        # Gradually decay to flatline
        spectrum_data = [max(0, d * 0.9) for d in spectrum_data]
        return spectrum_data
    
    t = time.time()
    # Normalize peak for intensity (0.0 to 1.0)
    # We use a multiplier to ensure low volume music still looks good
    peak_level = meter_control.GetPeakValue() if (universal_mode and meter_control) else 1.0
    intensity = min(peak_level * 5, 1.0) # Boost for visual appeal
    
    for i in range(spectrum_bars):
        # Sine wave base + random noise + high frequency jitter
        base = math.sin(t * 5 + i * 0.5) * 0.3 + 0.5
        noise = random.uniform(0, 0.2)
        # Power peaks (simulating bass/beats)
        peak_procedural = 0
        if i < 8: # Low frequency (bass)
             peak_procedural = math.sin(t * 12) * 0.4 if math.sin(t * 12) > 0.8 else 0
        
        target = (base + noise + peak_procedural) * vol * intensity
        # Smoothing (Interpolation)
        spectrum_data[i] = spectrum_data[i] * 0.7 + target * 0.3
        
    return spectrum_data

def draw_mini_visualizer(frame, x, y, width, height, data):
    """Draws an attractive neon spectrum visualizer."""
    bar_w = width // len(data)
    spacing = 2
    
    # Draw Background Glow for the whole visualizer area
    sub_rect = frame[y-height:y, x:x+width]
    if sub_rect.size > 0:
        overlay = sub_rect.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (20, 20, 20), -1)
        res = cv2.addWeighted(sub_rect, 0.7, overlay, 0.3, 0)
        frame[y-height:y, x:x+width] = res

    # Always draw a subtle base line (Image 2 style)
    dash_len = 6
    for i in range(0, width, dash_len * 2):
        cv2.line(frame, (x + i, y), (min(x + i + dash_len, x + width), y), (120, 120, 120), 1)

    for i, val in enumerate(data):
        h = int(val * height)
        bx = x + i * bar_w
        by = y
        
        # Neon Gradient Effect
        # Main Bar
        color = (255, 0, 255) if i % 2 == 0 else (0, 255, 255)
        cv2.rectangle(frame, (bx + spacing, by - h), (bx + bar_w - spacing, by), color, -1)
        
        # Top Glow Cap
        cv2.rectangle(frame, (bx + spacing, by - h - 2), (bx + bar_w - spacing, by - h), (255, 255, 255), -1)
        
        # Subtle Bottom Reflection
        cv2.rectangle(frame, (bx + spacing, by), (bx + bar_w - spacing, by + int(h*0.3)), color, 1)

    cv2.putText(frame, "LIVE_SPECTRUM", (x, y - height - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (200, 200, 200), 1)


play_song()

# ---------------- LOAD MODEL ----------------
model = joblib.load("gesture_model.pkl")

# ---------------- MEDIAPIPE ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7, # Higher for stability
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# ---------------- STABILITY ----------------
prediction_queue = deque(maxlen=5)
stable_gesture = None

last_time = 0
action_delay = 2   # 🔥 2 sec delay

gesture_name = "WAITING"

# ---------------- MAIN LOOP ----------------
while True:
    stable_gesture = None  # 🔥 Reset every frame to prevent ghosting
    frame_count += 1
    ret, frame = cap.read()
    if not ret:
        break

    # Calculate FPS
    if frame_count % 30 == 0:
        end_time_fps = time.time()
        fps = 30 / (end_time_fps - start_time_fps)
        start_time_fps = end_time_fps

    # ---------------- SONG TIMER (Calculated at top for HUD) ----------------
    if not is_paused:
        elapsed_time = elapsed_base + (time.time() - last_play_time)
    else:
        elapsed_time = elapsed_base

    if song_duration > 0:
        progress = min(elapsed_time / song_duration, 1)
    else:
        progress = 0

    elapsed_min = int(elapsed_time // 60)
    elapsed_sec = int(elapsed_time % 60)

    total_min = int(song_duration // 60)
    total_sec = int(song_duration % 60)

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        for hand_landmarks in result.multi_hand_landmarks:
            # Draw Neon Skeleton (Showcase Feature)
            if show_skeleton:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                       mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2, circle_radius=2),
                                       mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2))

            lm = hand_landmarks.landmark

            landmarks = []

            # 🔥 NORMALIZATION
            base_x = lm[0].x
            base_y = lm[0].y

            for point in lm:
                landmarks.append(point.x - base_x)
                landmarks.append(point.y - base_y)

            # Predict
            prediction = model.predict([landmarks])[0]

            # Stability & Confidence Calculation
            prediction_queue.append(prediction)
            most_common = max(set(prediction_queue), key=prediction_queue.count)
            stability_score = (prediction_queue.count(most_common) / prediction_queue.maxlen) * 100

            if prediction_queue.count(most_common) >= 3:
                stable_gesture = most_common
                gesture_name = f"{stable_gesture.upper()} ({int(stability_score)}%)"
            else:
                gesture_name = "STABILIZING..."

            current_time = time.time()

            # ---------------- ACTION ----------------
            if stable_gesture and (current_time - last_time > action_delay):

                if stable_gesture == "play":
                    resume_song()

                elif stable_gesture == "pause":
                    pause_song()

                elif stable_gesture == "next":
                    next_song()

                elif stable_gesture == "previous":
                    prev_song()
                elif stable_gesture == "volume_up":
                    volume = min(volume + 0.1, 1.0)
                    if volume_control:
                        volume_control.SetMasterVolumeLevelScalar(volume, None)
                    if universal_mode:
                        pyautogui.press('volumeup', presses=2) # Double tap for better feel
                    else:
                        pygame.mixer.music.set_volume(volume)
                    speak(f"Volume up {int(volume*100)} percent")
                    notification_text = f"VOLUME: {int(volume*100)}%"
                    notification_time = time.time()

                elif stable_gesture == "volume_down":
                    volume = max(volume - 0.1, 0.0)
                    if volume_control:
                        volume_control.SetMasterVolumeLevelScalar(volume, None)
                    if universal_mode:
                        pyautogui.press('volumedown', presses=2)
                    else:
                        pygame.mixer.music.set_volume(volume)
                    speak(f"Volume down {int(volume*100)} percent")
                    notification_text = f"VOLUME: {int(volume*100)}%"
                    notification_time = time.time()

                last_time = current_time

            # ---------------- SPATIAL UI TRACKING ----------------
            wrist_pos = (lm[0].x, lm[0].y)
            hud_angle += 5

            # SCRUBBING LOGIC (Innovative Point-to-Seek)
            # Only active in Local Mode
            if not universal_mode and lm[8].y < lm[6].y and lm[12].y > lm[10].y:
                current_time = time.time()
                # Only scrub if enough time passed and finger moved enough
                if current_time - last_scrub_time > 0.3 and abs(lm[8].x - last_scrub_x) > 0.05:
                    try:
                        # Map X position (0.1 to 0.9) to song duration
                        new_progress = np.interp(lm[8].x, [0.1, 0.9], [0, 1])
                        target_time = new_progress * song_duration
                        pygame.mixer.music.play(start=target_time)

                        # Update Timer Base
                        elapsed_base = target_time
                        last_play_time = time.time()
                        is_paused = False

                        last_scrub_time = current_time
                        last_scrub_x = lm[8].x
                    except Exception:
                        pass

                # Visual Feedback for Scrubbing
                cv2.putText(frame, "SCRUBBING...", (int(lm[8].x * frame.shape[1]), int(lm[8].y * frame.shape[0]) - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Draw HUD
            frame = draw_neon_hud(frame, wrist_pos, hud_angle, song_name, volume, progress, universal_mode)

    else:
        gesture_name = "WAITING"
        prediction_queue.clear()  # 🔥 Clear memory when hand is gone

    # ---------------- DISPLAY ----------------

    # ---------------- INNOVATIVE HUD OVERLAY (V7.0 GLASS-TECH) ----------------
    # Subtle darkening for status with grid lines (Now 20% opacity for transparency)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
    # Add tech grid (Synchronized Black)
    for i in range(0, 100, 25):
        cv2.line(overlay, (0, i), (frame.shape[1], i), (0, 0, 0), 1)

    # Blend Glass Effect
    frame = cv2.addWeighted(overlay, 0.25, frame, 0.75, 0)

    cv2.putText(frame, "AI HAND GESTURE MUSIC CONTROLLER", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Mode Indicator
    mode_text = "UNIVERSAL (Spotify/YouTube/Any)" if universal_mode else "LOCAL_FILES"
    cv2.putText(frame, f"MODE: {mode_text}", (20, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    cv2.putText(frame, f"GESTURE_LOCK: {gesture_name}", (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

    if song_duration >= 0:
        cv2.putText(frame, f"SYS_VOL: {int(volume*100)}%", (frame.shape[1]-180, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # WAIT indicator
    if time.time() - last_time < action_delay:
        cv2.putText(frame, "WAIT...", (30, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    if not universal_mode:
        bar_x, bar_y = 30, 200
        bar_width, bar_height = 400, 10
        # Glass Border (Synchronized Black)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (0, 0, 0), 1)
        # Glow Effect Fill
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), (0, 255, 0), -1)
        cv2.putText(frame, f"{elapsed_min:02}:{elapsed_sec:02} / {total_min:02}:{total_sec:02}",
                    (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # ---------------- PRO SHOWCASE DASHBOARD (V6.0) ----------------
    # FPS Counter
    cv2.putText(frame, f"CORE_SPEED: {fps:.1f} FPS", (frame.shape[1] - 180, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # Action Notification Bar (Glass Blend)
    if time.time() - notification_time < 3: # Show for 3 seconds
        notif_overlay = frame.copy()
        cv2.rectangle(notif_overlay, (0, frame.shape[0] - 50), (frame.shape[1], frame.shape[0]), (0, 150, 0), -1)
        frame = cv2.addWeighted(notif_overlay, 0.4, frame, 0.6, 0)
        # Synchronized Black Line (V7.1)
        cv2.line(frame, (0, frame.shape[0] - 50), (frame.shape[1], frame.shape[0] - 50), (0, 0, 0), 1)
        cv2.putText(frame, notification_text, (frame.shape[1]//2 - 120, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Draw Mini Radar
    if 'landmarks' in locals():
        draw_mini_radar(frame, landmarks)

    # ---------------- MINI VISUALIZER ----------------
    spec_data = get_procedural_spectrum(is_paused, volume)
    # Bottom Right positioning (offset from right edge)
    vis_w, vis_h = 240, 50
    vis_x = frame.shape[1] - vis_w - 20
    vis_y = frame.shape[0] - 70 # Just above notification bar
    draw_mini_visualizer(frame, vis_x, vis_y, vis_w, vis_h, spec_data)

    # ---------------- AUTO YOUTUBE SKIP (User Method 1) ----------------
    if universal_mode:
        skip_youtube_ad()

    # Help Guide
    draw_help_guide(frame)

    cv2.imshow("AI Hand Gesture Music Player", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()