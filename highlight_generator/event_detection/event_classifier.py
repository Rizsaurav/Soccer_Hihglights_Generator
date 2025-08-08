import os
import json
import joblib
import numpy as np
import cv2
from tqdm import tqdm

from scene_classification.bovw_encoder import encode_frame
from scene_classification.scene_classifier import predict_scene
from audio_processing.audio_extractor import extract_audio_spikes

def classify_scene_types(frame_dir, kmeans_model, clf):
    """Predicts scene type for each frame in the folder."""
    frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
    frame_scenes = []

    for fname in tqdm(frame_files[:], desc="[🖼️  Scene Classification]"):
        img = cv2.imread(os.path.join(frame_dir, fname))
        vector = encode_frame(img, kmeans_model)
        scene = predict_scene(vector, clf)

        timestamp = int(fname.split("_")[1].split(".")[0]) * 15 / 30.0  # frame_skip=15, fps=30
        frame_scenes.append({"time": timestamp, "label": scene})

    return frame_scenes

def match_audio_and_scene(spikes, frame_scenes, buffer=3.0, min_gap=2.0, max_duration=615):
    """
    Match audio spikes with interesting scenes to detect highlights.
    Adds buffer for context, merges intelligently, and avoids abrupt cuts.
    Ensures final total duration stays around 10 minutes ±15 seconds.
    """
    interesting_labels = {"goal_area", "celebration", "crowd", "replay", "closeup"}
    scene_lookup = {fs["time"]: fs["label"] for fs in frame_scenes if "time" in fs and "label" in fs}

    events = []
    for spike in spikes:
        center = spike["start_time"]
        rounded = round(center)
        scene = scene_lookup.get(rounded, None)

        if scene in interesting_labels:
            start = max(0, spike["start_time"] - buffer)
            end = spike["end_time"] + buffer
            duration = end - start

            events.append((start, end, duration))

    events.sort()
    merged = []
    for start, end, dur in events:
        if not merged:
            merged.append([start, end])
        else:
            prev_start, prev_end = merged[-1]
            if start <= prev_end + min_gap:
                merged[-1][1] = max(prev_end, end)
            else:
                merged.append([start, end])

    final = []
    total_time = 0
    for s, e in merged:
        seg_len = e - s
        if total_time + seg_len <= max_duration:
            final.append((s, e))
            total_time += seg_len

    final.sort()
    highlights = [{"type": "highlight", "start_time": round(s, 2), "end_time": round(e, 2)} for s, e in final]
    print(f"[🎬] Filtered down to {len(highlights)} merged highlights (≈{round(total_time)} seconds)")
    return highlights

def save_highlights(highlights, out_path="output/highlights.json"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(highlights, f, indent=2)
    print(f"[✅] Saved {len(highlights)} highlights to {out_path}")

if __name__ == "__main__":
    kmeans_model = joblib.load("models/kmeans_bovw_100.pkl")
    clf = joblib.load("models/scene_classifier.pkl")

    frame_scenes = classify_scene_types("data/frames", kmeans_model, clf)
    spikes = extract_audio_spikes("data/match.mp4")
    highlights = match_audio_and_scene(spikes, frame_scenes)
    save_highlights(highlights)
