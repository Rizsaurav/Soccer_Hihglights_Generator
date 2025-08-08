import cv2
import os

def extract_anchor_frames(video_path, output_dir="data/cricket/frames", threshold=30, skip_frames=5):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    prev_gray = None
    frame_idx = 0
    saved_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % skip_frames != 0:
            frame_idx += 1
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            non_zero_count = cv2.countNonZero(diff)

            height, width = gray.shape
            pixel_count = height * width
            change_percent = (non_zero_count / pixel_count) * 100

            if change_percent >= threshold:
                frame_path = os.path.join(output_dir, f"frame_{saved_idx:03d}.jpg")
                cv2.imwrite(frame_path, frame)
                print(f"[FRAME] Saved frame_{saved_idx:03d} at frame {frame_idx}, Δ={change_percent:.2f}%")
                saved_idx += 1

        prev_gray = gray
        frame_idx += 1

    cap.release()
    print(f"[DONE] {saved_idx} anchor frames saved to {output_dir}")
