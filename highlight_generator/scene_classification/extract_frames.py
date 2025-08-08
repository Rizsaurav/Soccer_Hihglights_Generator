import cv2
import os

def extract_frames(video_path, output_dir, frame_skip=15):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    frame_idx = 0
    saved_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            filename = os.path.join(output_dir, f"frame_{saved_idx:04d}.jpg")
            cv2.imwrite(filename, frame)
            saved_idx += 1

        frame_idx += 1

    cap.release()
    print(f"[INFO] Saved {saved_idx} frames to {output_dir}")
