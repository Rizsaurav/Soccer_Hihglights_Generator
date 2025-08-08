import os
import cv2
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from scene_classification.bovw_encoder import encode_frame

# Constants
MODEL_PATH = "models/scene_classifier.pkl"
LABELS_CSV = "data/labeled_scenes.csv"
FRAME_DIR = "data/frames"

def train_scene_classifier(kmeans_model, labels_csv=LABELS_CSV):
    """
    Train a decision tree classifier using manually labeled frame vectors.
    """
    df = pd.read_csv(labels_csv)
    print(f"[INFO] 📄 Loaded {len(df)} labeled frames")

    X = []
    y = []

    for _, row in df.iterrows():
        frame_path = os.path.join(FRAME_DIR, row['frame'])
        img = cv2.imread(frame_path)
        if img is None:
            print(f"[WARN] Could not read {frame_path}, skipping.")
            continue

        vector = encode_frame(img, kmeans_model)
        X.append(vector)
        y.append(row['label'])

    clf = DecisionTreeClassifier(max_depth=10, random_state=42)
    clf.fit(X, y)

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"[INFO] ✅ Trained & saved scene classifier to {MODEL_PATH}")
    return clf


def predict_scene(frame_vector, clf):
    """
    Predict the scene label using a given trained classifier.
    """
    label = clf.predict([frame_vector])[0]
    return label



def batch_predict_scenes(frame_dir, kmeans_model, output_path="output/scene_predictions.json"):
    """
    Run scene predictions on all frames and save results to JSON.
    """
    from tqdm import tqdm
    import json

    results = {}
    clf = joblib.load(MODEL_PATH)

    os.makedirs("output", exist_ok=True)

    for fname in tqdm(sorted(os.listdir(frame_dir))):
        if not fname.endswith(".jpg"):
            continue
        fpath = os.path.join(frame_dir, fname)
        img = cv2.imread(fpath)
        if img is None:
            continue

        vector = encode_frame(img, kmeans_model)
        label = clf.predict([vector])[0]
        results[fname] = label

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[INFO] 🧠 Scene predictions saved to {output_path}")
