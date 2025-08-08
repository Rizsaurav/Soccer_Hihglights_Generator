

# Test video
TEST_CLIP = "data/cricket/samples/chunk_000.mp4"

from cricket.pipeline.audio_loudness import extract_audio_spikes_dynamic

extract_audio_spikes_dynamic(TEST_CLIP)

