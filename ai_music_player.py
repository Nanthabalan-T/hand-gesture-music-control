import cv2
import mediapipe as mp
import pygame
import os
import joblib
import time
import random
from mutagen.mp3 import MP3

# ---------------- MUSIC SETUP ----------------
pygame.mixer.init()

music_folder = "music"
songs = os.listdir(music_folder)
current_song = 0

song_name = "No Song"
song_start_time = 0
song_duration = 0


# ---------------- MUSIC FUNCTIONS ----------------
def play_song():
    global song_name, song_start_time, song_duration

    song_name = songs[current_song]

    pygame.mixer.music.load(os.path.join(music_folder, song_name))
    pygame.mixer.music.play()

    song_start_time = time.time()

    audio = MP3(os.path.join(music_folder, song_name))
    song_duration = audio.info.length


def pause_song():
    pygame.mixer.music.pause()


def stop_song():
    pygame.mixer.music.stop()


def next_song():
    global current_song
    current_song = (current_song + 1) % len(songs)
    play_song()


def prev_song():
    global current_song
    current_song = (current_song - 1) % len(songs)
    play_song()


def shuffle_song():
    global current_song
    current_song = random.randint(0, len(songs) - 1)
    play_song()


play_song()


# ---------------- LOAD AI MODEL ----------------
model = joblib.load("gesture_model.pkl")


# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

mp_draw = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


last_action = ""
last_time = 0
cooldown = 1.5

gesture_name = "WAITING"


# ---------------- MAIN LOOP ----------------
while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            lm = hand_landmarks.landmark

            landmarks = []

            for point in lm:
                landmarks.append(point.x)
                landmarks.append(point.y)

            prediction = model.predict([landmarks])[0]

            gesture_name = prediction

            current_time = time.time()

            if prediction != last_action and (current_time - last_time > cooldown):

                if prediction == "play":
                    pygame.mixer.music.unpause()

                elif prediction == "pause":
                    pause_song()

                elif prediction == "next":
                    next_song()

                elif prediction == "previous":
                    prev_song()

                elif prediction == "stop":
                    stop_song()

                elif prediction == "shuffle":
                    shuffle_song()

                last_action = prediction
                last_time = current_time

    else:
        gesture_name = "WAITING"


    # ---------------- SONG TIMER ----------------
    if pygame.mixer.music.get_busy():
        elapsed_time = time.time() - song_start_time
    else:
        elapsed_time = 0

    if song_duration > 0:
        progress = min(elapsed_time / song_duration, 1)
    else:
        progress = 0


    elapsed_min = int(elapsed_time // 60)
    elapsed_sec = int(elapsed_time % 60)

    total_min = int(song_duration // 60)
    total_sec = int(song_duration % 60)


    # ---------------- DISPLAY ----------------

    cv2.putText(frame, f"Gesture: {gesture_name}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.putText(frame, f"Now Playing: {song_name}", (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)


    # ---------------- PROGRESS BAR ----------------

    bar_x = 30
    bar_y = 150
    bar_width = 400
    bar_height = 20

    cv2.rectangle(frame, (bar_x, bar_y),
                  (bar_x + bar_width, bar_y + bar_height),
                  (200, 200, 200), -1)

    cv2.rectangle(frame, (bar_x, bar_y),
                  (bar_x + int(bar_width * progress), bar_y + bar_height),
                  (0, 255, 0), -1)


    cv2.putText(frame,
                f"{elapsed_min:02}:{elapsed_sec:02} / {total_min:02}:{total_sec:02}",
                (bar_x, bar_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2)


    cv2.imshow("AI Hand Gesture Music Player", frame)


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()