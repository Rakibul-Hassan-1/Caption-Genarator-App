import streamlit as st
import os
import tempfile
import subprocess
import sys
from pathlib import Path
import time

# Check if required packages are installed
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    st.error("❌ Error: whisper is not installed. Please install it with: pip install openai-whisper")
    st.info("For now, you can use the command-line version: `python app.py your_video.mp4`")
    st.stop()

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
            st.error(f"❌ Error: Audio extraction failed - output file is empty or missing")
            return None
            
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error extracting audio with FFmpeg: {e}")
        if e.stderr:
            st.error(f"FFmpeg error: {e.stderr}")
        return None
    except Exception as e:
        st.error(f"❌ Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path, model_size="medium", language=None):
    """Enhanced transcription with better Whisper settings"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"🤖 Loading Whisper model: {model_size}")
        progress_bar.progress(20)
        
        model = whisper.load_model(model_size)
        progress_bar.progress(40)
        
        # Enhanced transcription options
        options = {
            "language": language,  # Auto-detect if None
            "task": "transcribe",
            "fp16": False,  # Use FP32 for better accuracy on CPU
            "verbose": False,
            "temperature": 0.0,  # Deterministic output
        }
        
        status_text.text("🔤 Transcribing with enhanced settings...")
        progress_bar.progress(60)
        
        result = model.transcribe(audio_path, **options)
        progress_bar.progress(80)
        
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
        
        progress_bar.progress(100)
        status_text.text("✅ Transcription completed!")
        
        return text
        
    except Exception as e:
        st.error(f"❌ Error transcribing audio: {e}")
        return None

def process_video(video_file, model_size="base", language=None):
    """Process a single video file and return captions"""
    if not check_ffmpeg():
        st.error("❌ Error: FFmpeg is not installed or not found in PATH!")
        st.info("Please install FFmpeg:\n- Windows: winget install ffmpeg\n- Linux: sudo apt install ffmpeg\n- macOS: brew install ffmpeg")
        return None
    
    # Create a temporary file for the uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(video_file.read())
        video_path = tmp_file.name
    
    try:
        st.info("🎬 Processing video...")
        
        # Extract audio
        audio_path = extract_audio(video_path)
        if not audio_path:
            return None
        
        st.success("🎵 Audio extracted successfully")
        
        # Transcribe audio
        captions = transcribe_audio(audio_path, model_size, language)
        if not captions:
            return None
        
        return captions
        
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            st.warning(f"⚠️ Warning: Could not remove temporary files: {e}")

# Streamlit UI
def main():
    st.set_page_config(
        page_title="🎬 Caption Generator App",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🎬 Caption Generator App")
    st.markdown("Generate high-quality captions from your videos using AI-powered speech recognition")
    
    # Sidebar for settings
    st.sidebar.header("⚙️ Settings")
    
    # Model selection
    model_size = st.sidebar.selectbox(
        "🤖 Whisper Model Size",
        ["tiny", "base", "small", "medium", "large"],
        index=1,  # Default to "base"
        help="Larger models provide better accuracy but are slower"
    )
    
    # Language selection
    language_options = {
        "Auto-detect": None,
        "English": "en",
        "Bengali": "bn", 
        "Hindi": "hi",
        "Chinese": "zh",
        "Japanese": "ja",
        "Korean": "ko",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Arabic": "ar"
    }
    
    selected_language = st.sidebar.selectbox(
        "🌍 Language",
        list(language_options.keys()),
        help="Specify language for better accuracy, or use auto-detect"
    )
    language = language_options[selected_language]
    
    # Main content area
    st.header("📹 Upload Your Video")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'],
        help="Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP"
    )
    
    if uploaded_file is not None:
        # Display video info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 File Name", uploaded_file.name)
        with col2:
            st.metric("📊 File Size", f"{uploaded_file.size / (1024*1024):.1f} MB")
        with col3:
            st.metric("🤖 Model", model_size)
        
        # Process button
        if st.button("🚀 Generate Captions", type="primary"):
            if not check_ffmpeg():
                st.error("❌ FFmpeg is required but not found. Please install FFmpeg first.")
                st.stop()
            
            # Process the video
            with st.spinner("Processing your video..."):
                captions = process_video(uploaded_file, model_size, language)
            
            if captions:
                st.success("✅ Captions generated successfully!")
                
                # Display captions
                st.header("📝 Generated Captions")
                st.text_area(
                    "Captions",
                    captions,
                    height=300,
                    help="Copy the text below to use in your video editing software"
                )
                
                # Download button
                st.download_button(
                    label="💾 Download Captions as TXT",
                    data=captions,
                    file_name=f"{Path(uploaded_file.name).stem}_captions.txt",
                    mime="text/plain"
                )
                
                # Display word count
                word_count = len(captions.split())
                st.info(f"📊 Caption Statistics: {word_count} words, {len(captions)} characters")
    
    # Instructions section
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Upload Video**: Click "Browse files" and select your video
        2. **Configure Settings**: 
           - Choose model size (larger = better quality, slower)
           - Select language (or use auto-detect)
        3. **Generate**: Click "Generate Captions" button
        4. **Download**: Copy the text or download as TXT file
        
        ### Tips for Best Results:
        - Use **medium** or **large** models for better accuracy
        - Specify the correct language for your content
        - Ensure your video has clear audio
        - For long videos, processing may take several minutes
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🎬 Caption Generator App | Powered by OpenAI Whisper & FFmpeg</p>
        <p>Made with ❤️ for content creators</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
