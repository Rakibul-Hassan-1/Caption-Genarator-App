import streamlit as st
import os
import tempfile
import subprocess
import sys
from pathlib import Path
import time

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
    """Extract audio from video using FFmpeg"""
    try:
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '1',
            '-af', 'highpass=f=200,lowpass=f=3000,volume=1.5',
            '-y',
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            return audio_path
        else:
            return None
            
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path, model_size="base", language=None):
    """Transcribe audio using Whisper"""
    try:
        import whisper
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"Loading Whisper model: {model_size}")
        progress_bar.progress(20)
        
        model = whisper.load_model(model_size)
        progress_bar.progress(40)
        
        options = {
            "language": language,
            "task": "transcribe",
            "fp16": False,
            "verbose": False,
            "temperature": 0.0,
        }
        
        status_text.text("Transcribing audio...")
        progress_bar.progress(60)
        
        result = model.transcribe(audio_path, **options)
        progress_bar.progress(80)
        
        text = result["text"].strip()
        
        if text:
            text = ' '.join(text.split())
            text = text.replace('  ', ' ')
            if not text.endswith(('.', '!', '?')):
                text += '.'
        
        progress_bar.progress(100)
        status_text.text("Transcription completed!")
        
        return text
        
    except ImportError:
        st.error("Whisper is not installed. Please install it with: pip install openai-whisper")
        return None
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def process_video(video_file, model_size="base", language=None, video_name="video"):
    """Process a single video file and return captions"""
    if not check_ffmpeg():
        st.error("FFmpeg is not installed or not found in PATH!")
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(video_file.read())
        video_path = tmp_file.name
    
    try:
        st.info(f"Processing {video_name}...")
        
        audio_path = extract_audio(video_path)
        if not audio_path:
            return None
        
        st.success(f"Audio extracted from {video_name}")
        
        captions = transcribe_audio(audio_path, model_size, language)
        if not captions:
            return None
        
        return captions
        
    finally:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            st.warning(f"Could not remove temporary files: {e}")

def process_batch_videos(video_files, model_size="base", language=None):
    """Process multiple video files and return results"""
    results = []
    total_videos = len(video_files)
    
    # Create progress bar for batch processing
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, video_file in enumerate(video_files):
        status_text.text(f"Processing {i+1}/{total_videos}: {video_file.name}")
        
        captions = process_video(video_file, model_size, language, video_file.name)
        
        if captions:
            results.append({
                'filename': video_file.name,
                'captions': captions,
                'success': True
            })
            st.success(f"✅ {video_file.name} processed successfully")
        else:
            results.append({
                'filename': video_file.name,
                'captions': None,
                'success': False
            })
            st.error(f"❌ Failed to process {video_file.name}")
        
        # Update progress
        progress_bar.progress((i + 1) / total_videos)
    
    status_text.text("Batch processing completed!")
    return results

def main():
    st.set_page_config(
        page_title="Caption Generator App",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state for batch results
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = None
    if 'batch_processed' not in st.session_state:
        st.session_state.batch_processed = False
    
    # Header
    st.title("🎬 Caption Generator App")
    st.markdown("Generate high-quality captions from your videos using AI-powered speech recognition")
    
    # Sidebar for settings
    st.sidebar.header("⚙️ Settings")
    
    # Model selection
    model_size = st.sidebar.selectbox(
        "🤖 Whisper Model Size",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
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
    st.header("📹 Upload Your Videos")
    
    # Upload mode selection
    upload_mode = st.radio(
        "Choose upload mode:",
        ["Single Video", "Multiple Videos (Batch)"],
        horizontal=True
    )
    
    # Clear batch results when switching modes
    if 'last_upload_mode' not in st.session_state:
        st.session_state.last_upload_mode = upload_mode
    elif st.session_state.last_upload_mode != upload_mode:
        st.session_state.batch_results = None
        st.session_state.batch_processed = False
        st.session_state.last_upload_mode = upload_mode
    
    if upload_mode == "Single Video":
        # Single file uploader
        uploaded_files = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'],
            help="Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP",
            accept_multiple_files=False
        )
        
        if uploaded_files is not None:
            # Display video info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📁 File Name", uploaded_files.name)
            with col2:
                st.metric("📊 File Size", f"{uploaded_files.size / (1024*1024):.1f} MB")
            with col3:
                st.metric("🤖 Model", model_size)
            
            # Process button
            if st.button("🚀 Generate Captions", type="primary"):
                captions = process_video(uploaded_files, model_size, language, uploaded_files.name)
                
                if captions:
                    st.success("Captions generated successfully!")
                    
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
                        file_name=f"{Path(uploaded_files.name).stem}_captions.txt",
                        mime="text/plain"
                    )
                    
                    # Display word count
                    word_count = len(captions.split())
                    st.info(f"📊 Caption Statistics: {word_count} words, {len(captions)} characters")
    
    else:  # Multiple Videos (Batch)
        # Multiple file uploader
        uploaded_files = st.file_uploader(
            "Choose multiple video files",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'],
            help="Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP",
            accept_multiple_files=True
        )
        
        if uploaded_files is not None and len(uploaded_files) > 0:
            # Display batch info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📁 Total Files", len(uploaded_files))
            with col2:
                total_size = sum(f.size for f in uploaded_files) / (1024*1024)
                st.metric("📊 Total Size", f"{total_size:.1f} MB")
            with col3:
                st.metric("🤖 Model", model_size)
            
            # Show file list
            st.subheader("📋 Files to Process:")
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size / (1024*1024):.1f} MB)")
            
            # Process button
            if st.button("🚀 Generate Captions for All Videos", type="primary"):
                results = process_batch_videos(uploaded_files, model_size, language)
                # Store results in session state
                st.session_state.batch_results = results
                st.session_state.batch_processed = True
                st.rerun()  # Refresh the page to show results
        
        # Display results if they exist in session state
        if st.session_state.batch_results is not None:
            st.header("📝 Batch Processing Results")
            st.info("💡 **Tip**: Results are saved in your session. You can download all captions without losing the results!")
            
            results = st.session_state.batch_results
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            # Summary
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"✅ Successful: {len(successful)}")
            with col2:
                if failed:
                    st.error(f"❌ Failed: {len(failed)}")
            
            # Show successful results
            if successful:
                st.subheader("🎉 Successfully Processed Videos:")
                
                # Create columns for better layout
                cols = st.columns(min(len(successful), 3))  # Max 3 columns
                
                for i, result in enumerate(successful):
                    col_idx = i % 3
                    
                    with cols[col_idx]:
                        st.markdown(f"**📹 {result['filename']}**")
                        
                        # Show captions in a smaller text area
                        st.text_area(
                            "Captions",
                            result['captions'],
                            height=150,
                            key=f"captions_{result['filename']}",
                            label_visibility="collapsed"
                        )
                        
                        # Download button for each file
                        st.download_button(
                            label=f"💾 Download {Path(result['filename']).stem} Captions",
                            data=result['captions'],
                            file_name=f"{Path(result['filename']).stem}_captions.txt",
                            mime="text/plain",
                            key=f"download_{result['filename']}",
                            use_container_width=True
                        )
                        
                        # Add some spacing
                        st.markdown("---")
                
                # Summary of downloads
                st.info(f"📦 {len(successful)} caption files ready for download above")
            
            # Show failed results
            if failed:
                st.subheader("❌ Failed Videos:")
                for result in failed:
                    st.error(f"Failed to process: {result['filename']}")
            
            # Clear results button
            if st.button("🗑️ Clear Results", type="secondary"):
                st.session_state.batch_results = None
                st.session_state.batch_processed = False
                st.rerun()
    
    # Tips section
    st.header("💡 Tips for Best Results")
    
    st.markdown("""
    **For optimal caption quality:**
    - Use **medium** or **large** models for better accuracy
    - Specify the correct language for your content
    - Ensure your videos have clear audio
    - For long videos, processing may take several minutes
    - Batch processing shows progress for each video
    """)
    
    # Instructions section
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        #### Single Video Processing:
        1. **Select Mode**: Choose "Single Video"
        2. **Upload Video**: Click "Browse files" and select your video
        3. **Configure Settings**: 
           - Choose model size (larger = better quality, slower)
           - Select language (or use auto-detect)
        4. **Generate**: Click "Generate Captions" button
        5. **Download**: Copy the text or download as TXT file
        
        #### Batch Processing (Multiple Videos):
        1. **Select Mode**: Choose "Multiple Videos (Batch)"
        2. **Upload Videos**: Click "Browse files" and select multiple videos
        3. **Configure Settings**: Same as single video
        4. **Generate**: Click "Generate Captions for All Videos"
        5. **Download**: Download each video's captions separately
        
        ### Tips for Best Results:
        - Use **medium** or **large** models for better accuracy
        - Specify the correct language for your content
        - Ensure your videos have clear audio
        - For long videos, processing may take several minutes
        - Batch processing shows progress for each video
        
        ### Command Line Alternative:
        If the web interface has issues, you can always use the command line:
        ```bash
        python app.py your_video.mp4
        python app.py --folder your_videos_folder/
        ```
        """)
    
    # Status section
    st.header("🔧 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if check_ffmpeg():
            st.success("✅ FFmpeg is available")
        else:
            st.error("❌ FFmpeg not found")
    
    with col2:
        try:
            import whisper
            st.success("✅ Whisper is available")
        except ImportError:
            st.error("❌ Whisper not installed")
    
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
