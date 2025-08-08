import numpy as np
import joblib
import os

# Dummy model — 1 descriptor
dummy_model = np.array([[0.1, 0.2, 0.3, 0.4]])

# Create models folder if missing
os.makedirs("models", exist_ok=True)

# Path to test save
model_path = "models/test_dummy_model.pkl"

# Save
joblib.dump(dummy_model, model_path)
print(f"[TEST] Saved dummy model to {model_path}")

# Load
loaded_model = joblib.load(model_path)
print(f"[TEST] Loaded model: {loaded_model}")
