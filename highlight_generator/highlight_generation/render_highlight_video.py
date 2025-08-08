from moviepy.editor import VideoFileClip, concatenate_videoclips
import json
import os

def render_highlight_video(video_path="data/match.mp4", highlights_path="output/highlights.json", output_path="output/highlights.mp4"):
    # Load highlights
    if not os.path.exists(highlights_path):
        print(f"[ERROR] Highlight JSON not found at: {highlights_path}")
        return

    with open(highlights_path) as f:
        highlights = json.load(f)

    if not highlights:
        print("[⚠️] No highlights found in JSON.")
        return

    # Load video
    if not os.path.exists(video_path):
        print(f"[ERROR] Video file not found: {video_path}")
        return

    print(f"[🎥] Loading video from {video_path}")
    clip = VideoFileClip(video_path)
    segments = []

    for h in highlights:
        start = h["start_time"]
        end = h["end_time"]
        if end > clip.duration:
            print(f"[⚠️] Skipping highlight [{start}, {end}] beyond video length {clip.duration}")
            continue
        try:
            segment = clip.subclip(start, end)
            segments.append(segment)
        except Exception as e:
            print(f"[❌] Failed to create subclip from {start} to {end}: {e}")

    if segments:
        final_clip = concatenate_videoclips(segments)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"[✅] Saved highlight video to {output_path}")
    else:
        print("[⚠️] No valid video segments created.")

if __name__ == "__main__":
    render_highlight_video()
