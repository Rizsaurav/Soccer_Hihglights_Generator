from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def split_video_into_chunks(input_path, output_dir, chunk_duration_sec=360):
    os.makedirs(output_dir, exist_ok=True)

    video = VideoFileClip(input_path)
    total_duration = int(video.duration)
    chunk_count = (total_duration + chunk_duration_sec - 1) // chunk_duration_sec

    print(f"[INFO] Video duration: {total_duration}s")
    print(f"[INFO] Splitting into {chunk_count} chunks of {chunk_duration_sec}s each.")

    for i in range(chunk_count):
        start_time = i * chunk_duration_sec
        end_time = min((i + 1) * chunk_duration_sec, total_duration)
        chunk = video.subclip(start_time, end_time)
        chunk.write_videofile(f"{output_dir}/chunk_{i:03d}.mp4", codec="libx264", audio_codec="aac")
        print(f"[✓] Saved: chunk_{i:03d}.mp4")

    print("[DONE] All chunks saved.")


if __name__ == "__main__":
    input_video = "fullmatch.mp4"  # video placed in root folder
    output_folder = "data/cricket/samples"
    split_video_into_chunks(input_video, output_folder)
