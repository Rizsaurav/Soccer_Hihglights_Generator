import os
import joblib
from concurrent.futures import ThreadPoolExecutor
from moviepy.editor import VideoFileClip

from scene_classification.extract_frames import extract_frames
from scene_classification.bovw_encoder import build_bovw_dictionary
from scene_classification.scene_classifier import train_scene_classifier
from audio_processing.audio_extractor import extract_audio_spikes
from event_detection.event_classifier import classify_scene_types, match_audio_and_scene, save_highlights
from highlight_generation.render_highlight_video import render_highlight_video

# === Get absolute path to project root ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def run_pipeline(video_path, output_dir=os.path.join(BASE_DIR, "static/output")):
    frame_dir = os.path.join(BASE_DIR, "data/frames")
    model_dir = os.path.join(BASE_DIR, "models")
    highlights_path = os.path.join(BASE_DIR, "output/highlights.json")
    output_video_path = os.path.join(output_dir, f"highlight_{os.path.basename(video_path)}")

    os.makedirs(frame_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(highlights_path), exist_ok=True)

    # Step 1: Extract visual frames from video
    extract_frames(video_path, frame_dir, frame_skip=15)

    # Step 2: Load or build BoVW model for visual features
    bovw_path = os.path.join(model_dir, "kmeans_bovw_100.pkl")
    if os.path.exists(bovw_path):
        print("[INFO] ✅ Loading BoVW model...")
        kmeans_model = joblib.load(bovw_path)
    else:
        print("[INFO] 🚀 Training BoVW model...")
        kmeans_model = build_bovw_dictionary(frame_dir, n_clusters=100)
        joblib.dump(kmeans_model, bovw_path)

    # Step 3: Load or train the visual scene classifier
    clf_path = os.path.join(model_dir, "scene_classifier.pkl")
    if os.path.exists(clf_path):
        clf = joblib.load(clf_path)
        print("[INFO] ✅ Loaded Scene Classifier.")
    else:
        clf = train_scene_classifier(kmeans_model)
        joblib.dump(clf, clf_path)
        print("[INFO] ✅ Trained Scene Classifier.")

    # Step 4: Run audio analysis and visual scene classification in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_audio = executor.submit(extract_audio_spikes, video_path)
        future_scene = executor.submit(classify_scene_types, frame_dir, kmeans_model, clf)

        spikes = future_audio.result()
        frame_scenes = future_scene.result()

    print("[AUDIO SPIKES]", spikes[:5])

    # Step 5: Match detected events and save highlights JSON
    highlights = match_audio_and_scene(spikes, frame_scenes)
    save_highlights(highlights, highlights_path)

    # Step 6: Render the final highlight video
    render_highlight_video(video_path, highlights_path, output_video_path)

    return output_video_path
