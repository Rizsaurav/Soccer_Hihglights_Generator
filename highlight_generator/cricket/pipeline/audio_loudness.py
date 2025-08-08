import os
import numpy as np
import librosa
import subprocess
import tempfile
import json

def extract_audio_spikes_dynamic(video_path, window_sec=0.75, mad_threshold=2.5, merge_window_sec=2.0):
    """
    Extract loud audio spikes from a video using dynamic thresholding.
    Saves the result as a JSON file and returns list of spike times (in seconds).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    print(f"[🔊] Analyzing audio in: {video_path}")
    
    # Step 1: Extract audio as .wav using ffmpeg with temporary file
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            wav_path = tmp_file.name
        
        cmd = [
            "ffmpeg", "-y", "-i", video_path, 
            "-vn", "-ac", "1", "-ar", "16000", 
            "-loglevel", "error",
            wav_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[❌] FFmpeg failed: {result.stderr}")
            return []
    except Exception as e:
        print(f"[❌] Failed to extract audio with ffmpeg: {e}")
        return []
    
    # Step 2: Load audio
    try:
        samples, sr = librosa.load(wav_path, sr=None)
        print(f"[📊] Audio loaded: {len(samples)} samples at {sr} Hz")
        if len(samples) == 0:
            print("[❌] No audio samples loaded")
            return []
    except Exception as e:
        print(f"[❌] Error loading audio: {e}")
        return []
    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except OSError:
                pass

    # Step 3: Normalize
    max_abs = np.max(np.abs(samples))
    if max_abs > 0:
        samples = samples / max_abs
    else:
        print("[❌] Audio contains only silence")
        return []

    # Step 4: RMS Loudness
    window_size = int(window_sec * sr)
    if window_size <= 0:
        print(f"[❌] Invalid window size: {window_size}")
        return []
    
    step_size = max(1, window_size // 2)
    loudness = []
    for i in range(0, len(samples) - window_size + 1, step_size):
        window = samples[i:i + window_size]
        if len(window) == window_size:
            rms = np.sqrt(np.mean(window**2))
            loudness.append(rms)
    if not loudness:
        print("[❌] No loudness values calculated")
        return []

    loudness = np.array(loudness)

    # Step 5: MAD Thresholding
    median_loudness = np.median(loudness)
    mad_loudness = np.median(np.abs(loudness - median_loudness))
    if mad_loudness == 0:
        std_loudness = np.std(loudness)
        threshold = median_loudness + 2.0 * std_loudness
        print("[⚠️] MAD is zero, using standard deviation fallback")
    else:
        threshold = median_loudness + mad_threshold * mad_loudness

    # Step 6: Detect spikes
    spike_indices = np.where(loudness > threshold)[0]
    spike_times = [float(idx * step_size) / float(sr) for idx in spike_indices]

    # Step 7: Merge nearby spikes
    merged_spikes = []
    if spike_times:
        current_group = [spike_times[0]]
        for t in spike_times[1:]:
            if t - current_group[-1] <= merge_window_sec:
                current_group.append(t)
            else:
                merged_spikes.append(float(np.median(current_group)))
                current_group = [t]
        merged_spikes.append(float(np.median(current_group)))

    # Step 8: Save spikes to JSON
    spike_dir = "data/cricket/spikes"
    os.makedirs(spike_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]
    json_path = os.path.join(spike_dir, f"{base}.json")
    with open(json_path, "w") as f:
        json.dump(merged_spikes, f, indent=2)
    print(f"[💾] Saved {len(merged_spikes)} spikes to {json_path}")

    # Step 9: Print and return
    print(f"📊 Median: {median_loudness:.5f}, MAD: {mad_loudness:.5f}, Threshold: {threshold:.5f}")
    print(f"🔊 {len(merged_spikes)} loud spikes detected at:")
    for t in merged_spikes:
        minutes = int(t // 60)
        seconds = int(t % 60)
        print(f"  ⏱️ {minutes:02d}:{seconds:02d} — {t:.2f}s")
    
    return merged_spikes
