import os
import librosa
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings

# Suppress library warnings for a cleaner output
warnings.filterwarnings('ignore')

def extract_features(file_path):
    """Loads audio and extracts MFCC features for similarity comparison."""
    try:
        # Load audio (limited to 30s to keep it fast)
        # librosa.load handles different formats if ffmpeg is available
        y, sr = librosa.load(file_path, duration=30, sr=None)
        
        if len(y) == 0:
            return None

        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Average the features across time so we have one 'fingerprint'
        mfccs_processed = np.mean(mfccs.T, axis=0)
        return mfccs_processed
    except Exception as e:
        print(f"   [!] Error processing {os.path.basename(file_path)}: {e}")
        return None

def main():
    # --- CONFIGURATION (Use 'r' for Windows paths) ---
    # Update these paths to match your folder exactly
    user_audio_path = r"audio4.mpeg"
    database_folder = r"Audio_DB"

    print("--- Audio Similarity Detector ---")
    
    # 1. Check if the files/folders actually exist
    if not os.path.exists(user_audio_path):
        print(f"Error: User file not found at {user_audio_path}")
        return
    if not os.path.isdir(database_folder):
        print(f"Error: Database folder not found at {database_folder}")
        return

    # 2. Extract features for the uploaded file
    print(f"Extracting fingerprint for: {os.path.basename(user_audio_path)}...")
    query_features = extract_features(user_audio_path)
    
    if query_features is None:
        print("Failed to process the input audio.")
        return

    # 3. Compare against the folder
    print(f"Searching for matches in: {database_folder}...")
    results = []
    
    # List all files in the database folder
    all_files = os.listdir(database_folder)
    valid_extensions = ('.mp3', '.wav', '.mpeg', '.m4a', '.flac')

    for filename in all_files:
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(database_folder, filename)
            
            # Skip if it's the same file as the query
            if file_path == user_audio_path:
                continue
                
            db_features = extract_features(file_path)
            
            if db_features is not None:
                # Calculate Cosine Similarity
                # Reshaping to (1, -1) is required by sklearn
                similarity = cosine_similarity(
                    query_features.reshape(1, -1), 
                    db_features.reshape(1, -1)
                )[0][0]
                
                results.append((filename, similarity))

    # 4. Display Results
    print("\n" + "="*30)
    print("RESULTS (Sorted by Similarity)")
    print("="*30)
    
    if not results:
        print("No audio files found in the database folder to compare.")
    else:
        # Sort results: highest similarity first
        results.sort(key=lambda x: x[1], reverse=True)
        
        for name, score in results:
            # 1.0 = Identical, 0.0 = Completely different
            percentage = score * 100
            print(f"{percentage:6.2f}% | {name}")
    print("="*30)

if __name__ == "__main__":
    main()