import os
import joblib
from moviepy.editor import VideoFileClip

from scene_classification.extract_frames import extract_frames
from scene_classification.bovw_encoder import build_bovw_dictionary
from scene_classification.scene_classifier import train_scene_classifier
from audio_processing.audio_extractor import extract_audio_spikes
from event_detection.event_classifier import classify_scene_types, match_audio_and_scene, save_highlights
from highlight_generation.render_highlight_video import render_highlight_video

# === ROOT-RELATIVE PATHS ===
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))  # This is the project root if run from root

DATA_DIR = os.path.join(ROOT_DIR, "data")
FRAME_DIR = os.path.join(DATA_DIR, "frames")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
VIDEO_PATH = os.path.join(DATA_DIR, "real.mp4")
HIGHLIGHT_JSON = os.path.join(OUTPUT_DIR, "highlights.json")
FINAL_VIDEO_PATH = os.path.join(OUTPUT_DIR, "highlight-real.mp4")

# === Ensure Needed Dirs Exist ===
os.makedirs(FRAME_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Step 1: Extract Frames ===
extract_frames(VIDEO_PATH, FRAME_DIR, frame_skip=15)

# === Step 2: Load/Train BoVW ===
bovw_path = os.path.join(MODEL_DIR, "kmeans_bovw_100.pkl")
if os.path.exists(bovw_path):
    print("[INFO] ✅ Loading BoVW model...")
    kmeans_model = joblib.load(bovw_path)
else:
    print("[INFO] 🚀 Training BoVW model...")
    kmeans_model = build_bovw_dictionary(FRAME_DIR, n_clusters=100)
    joblib.dump(kmeans_model, bovw_path)

# === Step 3: Load/Train Scene Classifier ===
scene_clf_path = os.path.join(MODEL_DIR, "scene_classifier.pkl")
if os.path.exists(scene_clf_path):
    clf = joblib.load(scene_clf_path)
    print("[INFO] ✅ Loaded Scene Classifier.")
else:
    clf = train_scene_classifier(kmeans_model)
    joblib.dump(clf, scene_clf_path)
    print("[INFO] ✅ Trained Scene Classifier.")

# === Step 4: Audio Spikes ===
spikes = extract_audio_spikes(VIDEO_PATH)
print("[AUDIO SPIKES]", spikes[:5])

# === Step 5: Scene Classification ===
frame_scenes = classify_scene_types(FRAME_DIR, kmeans_model, clf)

# === Step 6: Match Events ===
highlights = match_audio_and_scene(spikes, frame_scenes)
save_highlights(highlights, HIGHLIGHT_JSON)

# === Step 7: Render Final Video ===
render_highlight_video(VIDEO_PATH, HIGHLIGHT_JSON, FINAL_VIDEO_PATH)
