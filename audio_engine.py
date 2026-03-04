import librosa
import numpy as np

def get_beat_times(song_path):
    print(f"Analyzing {song_path}...")
    y, sr = librosa.load(song_path)
    
    # Try to find beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Fallback: If no beats are found, create a tile every 1.5 seconds
    if len(beat_times) == 0:
        print("No rhythmic beats detected. Using timed intervals instead.")
        duration = librosa.get_duration(y=y, sr=sr)
        beat_times = np.arange(1.0, duration, 1.5) 
        
    return [t - 1.5 for t in beat_times if t > 1.5]