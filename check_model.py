import joblib

model = joblib.load("gesture_model.pkl")

print("Model loaded successfully!")
print(model)