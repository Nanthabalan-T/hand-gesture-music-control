import cv2
import mediapipe as mp
import os
import csv

# ---------------- SETUP ----------------
dataset_path = "dataset"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Ask user for gesture label
gesture_name = input("Enter gesture name (play/pause/next/previous/volume_up/volume_down): ")

save_path = os.path.join(dataset_path, gesture_name)

# Create folder if not exists
os.makedirs(save_path, exist_ok=True)

# ✅ CONTINUE NUMBERING (IMPORTANT FIX)
existing_files = os.listdir(save_path)
sample_count = len(existing_files)

print(f"Collecting data for: {gesture_name}")
print("Press 's' to save sample | Press 'q' to quit")

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

            # 🔥 NORMALIZATION
            base_x = lm[0].x
            base_y = lm[0].y

            for point in lm:
                landmarks.append(point.x - base_x)
                landmarks.append(point.y - base_y)

            key = cv2.waitKey(1)

            # Press 's' to save
            if key == ord('s'):
                sample_count += 1

                file_path = os.path.join(save_path, f"{sample_count}.csv")

                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(landmarks)

                print(f"Saved sample {sample_count}")

            # Press 'q' to quit
            elif key == ord('q'):
                break

    # Display info
    cv2.putText(frame, f"Gesture: {gesture_name}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"Samples: {sample_count}", (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("Collect Data", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()