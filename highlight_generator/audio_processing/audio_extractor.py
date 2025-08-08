import os
import numpy as np
import librosa
from moviepy.editor import VideoFileClip


def extract_audio_from_video(video_path, output_audio_path="temp_audio.wav"):
    """
    Extracts the audio track from a video file using MoviePy.
    """
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio_path, verbose=False, logger=None)
    return output_audio_path


def extract_audio_spikes(video_path, rms_threshold=0.05, frame_duration=1.0):
    """
    Detects audio spikes from a video using librosa RMS energy.

    Returns a list of time segments with loud events:
    [
        {"start_time": 121.0, "end_time": 122.0},
        ...
    ]
    """
    audio_path = extract_audio_from_video(video_path)
    y, sr = librosa.load(audio_path)

    hop_length = int(sr * frame_duration)
    rms = librosa.feature.rms(y=y, frame_length=hop_length, hop_length=hop_length)[0]

    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    spikes = []
    for i, energy in enumerate(rms):
        if energy >= rms_threshold:
            start = float(times[i])
            end = start + frame_duration
            spikes.append({ "start_time": round(start, 2), "end_time": round(end, 2) })

    os.remove(audio_path)  # Clean up temp audio file
    print(f"[INFO] 🔊 Found {len(spikes)} audio spikes")
    return spikes
