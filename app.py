import os
import sys
import subprocess
import tempfile

# Check if required packages are installed
try:
    import whisper
except ImportError:
    print("❌ Error: whisper is not installed. Please install it with: pip install openai-whisper")
    sys.exit(1)

# Check if FFmpeg is available
def check_ffmpeg():
    """Check if FFmpeg is available in the system"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False

# ---------- Step 1: ভিডিও থেকে অডিও বের করা (FFmpeg দিয়ে) ----------
def extract_audio(video_path, audio_path="temp_audio.wav"):
    """Extract audio from video using FFmpeg with optimized settings for speech recognition"""
    try:
        # FFmpeg command for high-quality audio extraction optimized for speech
        cmd = [
            'ffmpeg',
            '-i', video_path,           # Input video
            '-vn',                      # No video
            '-acodec', 'pcm_s16le',     # PCM 16-bit audio codec
            '-ar', '44100',             # Higher sample rate for better quality
            '-ac', '1',                 # Mono audio
            '-af', 'highpass=f=200,lowpass=f=3000,volume=1.5',  # Audio filters for speech
            '-y',                       # Overwrite output file
            audio_path
        ]
        
        # Run FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            return audio_path
        else:
            print(f"❌ Error: Audio extraction failed - output file is empty or missing")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error extracting audio with FFmpeg: {e}")
        if e.stderr:
            print(f"FFmpeg error: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Error extracting audio: {e}")
        return None

# ---------- Step 2: Whisper দিয়ে ট্রান্সক্রিপশন (উন্নত) ----------
def transcribe_audio(audio_path, model_size="medium", language=None):
    """Enhanced transcription with better Whisper settings"""
    try:
        print(f"🤖 Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        # Enhanced transcription options (using only supported parameters)
        options = {
            "language": language,  # Auto-detect if None
            "task": "transcribe",
            "fp16": False,  # Use FP32 for better accuracy on CPU
            "verbose": False,
            "temperature": 0.0,  # Deterministic output
        }
        
        print("🔤 Transcribing with enhanced settings...")
        result = model.transcribe(audio_path, **options)
        
        # Post-process the transcription for better quality
        text = result["text"].strip()
        
        # Basic text cleaning
        if text:
            # Remove excessive whitespace
            text = ' '.join(text.split())
            # Fix common transcription errors
            text = text.replace('  ', ' ')
            # Ensure proper sentence endings
            if not text.endswith(('.', '!', '?')):
                text += '.'
        
        return text
        
    except Exception as e:
        print(f"❌ Error transcribing audio: {e}")
        return None

# ---------- Step 3: একক ভিডিও প্রসেসিং ----------
def process_single_video(video_path, output_file, model_size="base", language=None):
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file '{video_path}' not found!")
        return False
    
    print(f"🎬 Processing video: {video_path}")
    
    # Extract audio
    audio_path = extract_audio(video_path)
    if not audio_path:
        return False
    
    print("🎵 Audio extracted successfully")
    
    # Transcribe audio
    print("🔤 Transcribing audio...")
    captions = transcribe_audio(audio_path, model_size, language)
    if not captions:
        return False
    
    # Save to text file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(captions)
        print(f"✅ Captions saved in {output_file}")
    except Exception as e:
        print(f"❌ Error saving captions: {e}")
        return False
    
    # Clean temp file
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print("🧹 Temporary audio file cleaned up")
    except Exception as e:
        print(f"⚠️ Warning: Could not remove temporary file {audio_path}: {e}")
    
    return True

# ---------- Step 4: ব্যাচ প্রসেসিং ----------
def batch_process_videos(video_files, output_folder="captions", model_size="base", language=None):
    """Process multiple video files and save captions in organized folders"""
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output folder: {output_folder}")
    
    # Create a summary file
    summary_file = os.path.join(output_folder, "processing_summary.txt")
    summary_content = []
    
    successful_count = 0
    failed_count = 0
    
    print(f"🚀 Starting batch processing of {len(video_files)} video(s)...")
    print(f"📁 Output folder: {output_folder}")
    print(f"🤖 Model: {model_size}")
    if language:
        print(f"🌍 Language: {language}")
    else:
        print(f"🌍 Language: Auto-detect")
    print("-" * 50)
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n📹 [{i}/{len(video_files)}] Processing: {video_file}")
        
        # Create output filename based on video filename
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        output_file = os.path.join(output_folder, f"{video_name}_captions.txt")
        
        # Process the video
        success = process_single_video(video_file, output_file, model_size, language)
        
        if success:
            successful_count += 1
            summary_content.append(f"✅ {video_file} -> {output_file}")
            print(f"✅ Successfully processed: {video_file}")
        else:
            failed_count += 1
            summary_content.append(f"❌ {video_file} -> FAILED")
            print(f"❌ Failed to process: {video_file}")
        
        print("-" * 30)
    
    # Save summary
    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("Caption Generation Summary\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"Total videos: {len(video_files)}\n")
            f.write(f"Successful: {successful_count}\n")
            f.write(f"Failed: {failed_count}\n")
            f.write(f"Model used: {model_size}\n")
            if language:
                f.write(f"Language: {language}\n")
            else:
                f.write("Language: Auto-detect\n")
            f.write("\nDetails:\n")
            f.write("-" * 20 + "\n")
            for line in summary_content:
                f.write(line + "\n")
        
        print(f"\n📊 Summary saved in: {summary_file}")
    except Exception as e:
        print(f"⚠️ Warning: Could not save summary: {e}")
    
    # Final summary
    print(f"\n🎉 Batch processing completed!")
    print(f"✅ Successful: {successful_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Check the '{output_folder}' folder for results")

# ---------- Step 5: ফোল্ডার থেকে ভিডিও ডিটেক্ট করা ----------
def detect_videos_in_folder(folder_path):
    """Detect all video files in a specified folder"""
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' not found!")
        return []
    
    if not os.path.isdir(folder_path):
        print(f"❌ Error: '{folder_path}' is not a folder!")
        return []
    
    # Supported video extensions
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp')
    
    video_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(video_extensions):
            full_path = os.path.join(folder_path, file)
            video_files.append(full_path)
    
    # Sort files alphabetically for consistent processing order
    video_files.sort()
    
    return video_files

# ---------- Step 6: সবকিছু চালানো ----------
def video_to_captions(video_path, output_file="captions.txt"):
    """Legacy function for single video processing"""
    return process_single_video(video_path, output_file)

# ---------- Run ----------
if __name__ == "__main__":
    import argparse
    
    # Check FFmpeg availability first
    if not check_ffmpeg():
        print("❌ Error: FFmpeg is not installed or not found in PATH!")
        print("Please install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Or use: winget install ffmpeg")
        print("  Or use: choco install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        sys.exit(1)
    
    print("✅ FFmpeg found and ready to use!")
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Generate captions from video files using Whisper")
    parser.add_argument("video_files", nargs="*", help="Path(s) to video file(s) (optional)")
    parser.add_argument("--output", "-o", default="captions", help="Output folder for captions (default: captions)")
    parser.add_argument("--model", "-m", default="base", choices=["tiny", "base", "small", "medium", "large"], 
                       help="Whisper model size (default: base)")
    parser.add_argument("--batch", "-b", action="store_true", help="Force batch processing mode")
    parser.add_argument("--folder", "-f", help="Process all videos in specified folder")
    parser.add_argument("--language", "-l", help="Specify language for transcription (e.g., 'en', 'bn', 'hi')")
    
    args = parser.parse_args()
    
    # Get video file path(s)
    if args.folder:
        # Process all videos in specified folder
        print(f"📁 Scanning folder: {args.folder}")
        video_files = detect_videos_in_folder(args.folder)
        
        if not video_files:
            print(f"❌ No video files found in folder '{args.folder}'!")
            print("Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP")
            sys.exit(1)
        
        print(f"🎬 Found {len(video_files)} video file(s):")
        for i, video_file in enumerate(video_files, 1):
            print(f"  {i}. {os.path.basename(video_file)}")
        
        # Ask for confirmation
        try:
            confirm = input(f"\nProcess all {len(video_files)} video(s)? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '']:
                print("❌ Operation cancelled by user")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            sys.exit(1)
        
        # Use folder name as output folder if not specified
        if args.output == "captions":
            folder_name = os.path.basename(os.path.normpath(args.folder))
            args.output = f"{folder_name}_captions"
        
    elif args.video_files:
        video_files = args.video_files
        # Check if all files exist
        for video_file in video_files:
            if not os.path.exists(video_file):
                print(f"❌ Error: Video file '{video_file}' not found!")
                sys.exit(1)
    else:
        # If no command line argument, show available video files and ask user
        video_files = [f for f in os.listdir('.') if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'))]
        
        if not video_files:
            print("❌ No video files found in current directory!")
            print("Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP")
            print("\n💡 Tip: Use --folder to specify a different folder path")
            sys.exit(1)
        
        print("📁 Available video files in current directory:")
        for i, file in enumerate(video_files, 1):
            print(f"  {i}. {file}")
        
        try:
            choice = input(f"\nSelect video file(s) (1-{len(video_files)}) or enter filename(s) separated by space: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(video_files):
                video_files = [video_files[int(choice) - 1]]
            else:
                video_files = choice.split()
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            sys.exit(1)
    
    # Determine processing mode
    if len(video_files) > 1 or args.batch:
        # Batch processing mode
        print(f"🚀 Starting Caption Generation...")
        print(f"📹 Videos: {len(video_files)} file(s)")
        print(f"📝 Output folder: {args.output}")
        print(f"🤖 Model: {args.model}")
        if args.language:
            print(f"🌍 Language: {args.language}")
        else:
            print(f"🌍 Language: Auto-detect")
        
        batch_process_videos(video_files, args.output, args.model, args.language)
    else:
        # Single video processing mode
        video_file = video_files[0]
        output_file = os.path.join(args.output, f"{os.path.splitext(os.path.basename(video_file))[0]}_captions.txt")
        
        # Create output folder if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        print(f"🚀 Starting Caption Generation...")
        print(f"📹 Video: {video_file}")
        print(f"📝 Output: {output_file}")
        print(f"🤖 Model: {args.model}")
        if args.language:
            print(f"🌍 Language: {args.language}")
        else:
            print(f"🌍 Language: Auto-detect")
        
        # Use the enhanced single video processing
        process_single_video(video_file, output_file, args.model, args.language)
