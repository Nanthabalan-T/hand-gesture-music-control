import os
import numpy as np
import joblib
from sklearn import svm

# ---------------- DATASET PATH ----------------
dataset_path = "dataset"

X = []
y = []

# ---------------- LOAD DATA ----------------
for gesture in os.listdir(dataset_path):

    gesture_path = os.path.join(dataset_path, gesture)

    if not os.path.isdir(gesture_path):
        continue

    for file in os.listdir(gesture_path):

        file_path = os.path.join(gesture_path, file)

        # Read CSV
        data = np.loadtxt(file_path, delimiter=',')

        X.append(data)
        y.append(gesture)

# Convert to numpy
X = np.array(X)
y = np.array(y)

print("Dataset loaded successfully!")
print(f"Total samples: {len(X)}")

# ---------------- TRAIN MODEL ----------------
model = svm.SVC(kernel='linear', probability=True)

model.fit(X, y)

# ---------------- SAVE MODEL ----------------
joblib.dump(model, "gesture_model.pkl")

print("Model trained and saved as gesture_model.pkl")