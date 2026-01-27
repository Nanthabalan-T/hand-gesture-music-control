import cv2
import mediapipe as mp
import pygame
import os

# ---------------- MUSIC SETUP ----------------
pygame.mixer.init()

music_folder = "music"
songs = os.listdir(music_folder)
current_song = 0

def play_song():
    pygame.mixer.music.load(os.path.join(music_folder, songs[current_song]))
    pygame.mixer.music.play()

def pause_song():
    pygame.mixer.music.pause()

def stop_song():
    pygame.mixer.music.stop()

def next_song():
    global current_song
    current_song = (current_song + 1) % len(songs)
    play_song()

# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Finger tip landmark IDs
finger_tips = [4, 8, 12, 16, 20]

last_action = -1

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_count = -1

    if result.multi_hand_landmarks:
        # -------- HAND PRESENT --------
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

            lm = hand_landmarks.landmark
            finger_count = 0

            # Thumb
            if lm[4].x > lm[3].x:
                finger_count += 1

            # Other fingers
            for tip in finger_tips[1:]:
                if lm[tip].y < lm[tip - 2].y:
                    finger_count += 1

        # -------- MUSIC CONTROL --------
        if finger_count != last_action:
            if finger_count == 1:
                play_song()
            elif finger_count == 2:
                pause_song()
            elif finger_count == 3:
                next_song()
            elif finger_count == 0:
                stop_song()

            last_action = finger_count

    else:
        # -------- HAND NOT PRESENT --------
        stop_song()
        last_action = -1

    # ---------------- DISPLAY (ONLY FINGER COUNT) ----------------
    if finger_count != -1:
        cv2.putText(frame, f"Fingers: {finger_count}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Hand Gesture Music Player - Press Q to Exit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()