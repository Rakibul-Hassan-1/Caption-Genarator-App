import streamlit as st
import os
import tempfile
import subprocess
import sys
from pathlib import Path
import time
import re
import requests
import json

# Ensure higher upload limit is reflected in the app UI/runtime
try:
    import streamlit as st  # already imported above; kept for clarity in some IDEs
    st.set_option('server.maxUploadSize', 4096)
except Exception:
    pass

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

def extract_audio(video_path, audio_path=None):
    """Extract audio from video using FFmpeg"""
    try:
        # Create a temporary audio file if not provided
        if audio_path is None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                audio_path = tmp_audio.name
        
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
            st.error("Audio extraction failed - output file is empty or missing")
            return None
            
    except subprocess.CalledProcessError as e:
        st.error(f"FFmpeg error: {e.stderr if e.stderr else e}")
        return None
    except Exception as e:
        st.error(f"Error extracting audio: {e}")
        return None

def transcribe_audio(audio_path, model_size="base", language=None):
    """Transcribe audio using Whisper"""
    try:
        import whisper
        
        # Check if audio file exists
        if not os.path.exists(audio_path):
            st.error(f"Audio file not found: {audio_path}")
            return None
        
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
    
    audio_path = None
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
            if audio_path and os.path.exists(audio_path):
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

def generate_youtube_description_with_llm(captions, video_title="", custom_prompt="", include_timestamps=False, include_hashtags=True, use_openrouter=False):
    """Generate YouTube description using LLM (OpenRouter API or local model)"""
    try:
        # Check if OpenRouter API key is available and user wants to use it
        if use_openrouter:
            try:
                # Use the provided API key directly
                openrouter_api_key = "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"
                if openrouter_api_key:
                    return generate_with_openai(captions, video_title, custom_prompt, include_timestamps, include_hashtags, openrouter_api_key)
                else:
                    st.warning("OpenRouter API key not found. Using local generation instead.")
            except Exception as e:
                st.warning(f"Could not access OpenRouter API: {e}. Using local generation instead.")
        
        # Use local generation (fallback or default)
        return generate_with_local_llm(captions, video_title, custom_prompt, include_timestamps, include_hashtags)
            
    except Exception as e:
        return f"Error generating description: {e}"

def generate_with_openai(captions, video_title, custom_prompt, include_timestamps, include_hashtags, api_key):
    """Generate description using OpenRouter API (GPT-4o)"""
    try:
        # Prepare the prompt
        system_prompt = """You are a professional YouTube content creator and SEO expert. Create an engaging, SEO-optimized YouTube description based on the video captions provided. The description should be professional, engaging, and optimized for YouTube's algorithm."""
        
        user_prompt = f"""
Create a YouTube description for this video:

Video Title: {video_title if video_title else "Untitled Video"}

Video Captions:
{captions}

Custom Instructions: {custom_prompt if custom_prompt else "Create a professional YouTube description"}

Requirements:
- Include a compelling summary of the video content
- Add relevant keywords for SEO
- Include a call-to-action for engagement
- Make it engaging and professional
- Keep it under 5000 characters (YouTube limit)
{"- Include timestamps if the video is long enough" if include_timestamps else ""}
{"- Include relevant hashtags at the end" if include_hashtags else ""}

Format the description with proper sections and emojis for better readability.
"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://caption-generator-app.streamlit.app",
            "X-Title": "Caption Generator App"
        }
        
        data = {
            "model": "openai/gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            st.error(f"OpenRouter API Error: {response.status_code} - {response.text}")
            return generate_with_local_llm(captions, video_title, custom_prompt, include_timestamps, include_hashtags)
            
    except Exception as e:
        st.warning(f"OpenRouter API failed: {e}. Using local generation.")
        return generate_with_local_llm(captions, video_title, custom_prompt, include_timestamps, include_hashtags)

def generate_with_local_llm(captions, video_title, custom_prompt, include_timestamps, include_hashtags):
    """Generate description using local processing (fallback)"""
    try:
        # Clean and process captions
        clean_captions = captions.strip()
        
        # Extract key phrases and words
        words = clean_captions.lower().split()
        word_freq = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 3 and clean_word not in ['this', 'that', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'there', 'could', 'other', 'after', 'first', 'well', 'also', 'where', 'much', 'some', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'these', 'think', 'want', 'what', 'year', 'your', 'good', 'know', 'look', 'most', 'only', 'other', 'right', 'seem', 'tell', 'turn', 'use', 'way', 'work']:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [word for word, freq in top_keywords]
        
        # Generate description sections
        description_parts = []
        
        # Main description
        if video_title:
            description_parts.append(f"🎬 {video_title}")
            description_parts.append("")
        
        # Custom prompt integration - make it more prominent
        if custom_prompt:
            description_parts.append("📝 About This Video:")
            description_parts.append(custom_prompt)
            description_parts.append("")
        
        # Enhanced video summary based on custom prompt
        description_parts.append("📖 Video Summary:")
        sentences = re.split(r'[.!?]+', clean_captions)
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        
        # If custom prompt mentions specific topics, try to include them
        if custom_prompt and any(word in custom_prompt.lower() for word in ['tutorial', 'guide', 'how to', 'learn', 'education']):
            description_parts.append("This educational video covers: " + " ".join(summary_sentences) + ".")
        elif custom_prompt and any(word in custom_prompt.lower() for word in ['review', 'test', 'comparison']):
            description_parts.append("In this review video, we explore: " + " ".join(summary_sentences) + ".")
        elif custom_prompt and any(word in custom_prompt.lower() for word in ['entertainment', 'fun', 'comedy']):
            description_parts.append("Join us for this entertaining content: " + " ".join(summary_sentences) + ".")
        else:
            description_parts.append(" ".join(summary_sentences) + ".")
        
        description_parts.append("")
        
        # Key topics with better formatting
        if keywords:
            description_parts.append("🔑 Key Topics:")
            # Group related keywords
            topic_groups = []
            for keyword in keywords[:8]:
                if keyword not in [word for group in topic_groups for word in group]:
                    topic_groups.append([keyword])
            
            topics_text = ", ".join(keywords[:8])
            description_parts.append(topics_text)
            description_parts.append("")
        
        # Timestamps (if requested)
        if include_timestamps:
            description_parts.append("⏰ Timestamps:")
            sentences = [s.strip() for s in re.split(r'[.!?]+', clean_captions) if s.strip()]
            total_sentences = len(sentences)
            if total_sentences > 0:
                for i in range(0, min(total_sentences, 5), 2):
                    minutes = (i * 2) // 60
                    seconds = (i * 2) % 60
                    timestamp = f"{minutes:02d}:{seconds:02d}"
                    sentence = sentences[i][:50] + "..." if len(sentences[i]) > 50 else sentences[i]
                    description_parts.append(f"{timestamp} - {sentence}")
            description_parts.append("")
        
        # Enhanced call to action based on custom prompt
        description_parts.append("👍 If you enjoyed this video, please:")
        if custom_prompt and any(word in custom_prompt.lower() for word in ['tutorial', 'guide', 'learn']):
            description_parts.append("• Like if this tutorial helped you")
            description_parts.append("• Subscribe for more educational content")
        elif custom_prompt and any(word in custom_prompt.lower() for word in ['review', 'test']):
            description_parts.append("• Like if you found this review helpful")
            description_parts.append("• Subscribe for more reviews and tests")
        else:
            description_parts.append("• Like and subscribe for more content")
        
        description_parts.append("• Share with your friends")
        description_parts.append("• Leave a comment below")
        description_parts.append("")
        
        # Hashtags (if requested)
        if include_hashtags and keywords:
            description_parts.append("🏷️ Tags:")
            hashtags = ["#" + word.replace(" ", "") for word in keywords[:8]]
            description_parts.append(" ".join(hashtags))
            description_parts.append("")
        
        # Footer
        description_parts.append("─" * 50)
        description_parts.append("📺 Subscribe to our channel for more amazing content!")
        description_parts.append("🔔 Turn on notifications to never miss a video!")
        
        return "\n".join(description_parts)
        
    except Exception as e:
        return f"Error generating description: {e}"

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
    
    # YouTube Description Options
    st.sidebar.header("📺 YouTube Description")
    
    generate_description = st.sidebar.checkbox(
        "Generate YouTube Description",
        value=True,
        help="Automatically generate YouTube description from captions"
    )
    
    if generate_description:
        video_title = st.sidebar.text_input(
            "Video Title (Optional)",
            placeholder="Enter your video title",
            help="Title will be included in the description"
        )
        
        custom_prompt = st.sidebar.text_area(
            "Custom Prompt/Instructions",
            placeholder="e.g., 'Create a description for a tech tutorial video focusing on beginners' or 'Make it sound professional and educational'",
            help="Provide specific instructions for how you want the description to be written",
            height=100
        )
        
        # LLM Options
        st.sidebar.subheader("🤖 LLM Options")
        
        use_openrouter = st.sidebar.checkbox(
            "Use OpenRouter GPT-4o (Premium Quality)",
            value=True,
            help="Uses GPT-4o via OpenRouter for high-quality descriptions. Falls back to local generation if unavailable."
        )
        
        if use_openrouter:
            st.sidebar.success("✅ OpenRouter GPT-4o is configured and ready!")
            st.sidebar.info("💡 Premium AI-powered descriptions with GPT-4o")
        
        include_timestamps = st.sidebar.checkbox(
            "Include Timestamps",
            value=False,
            help="Add timestamps to the description"
        )
        
        include_hashtags = st.sidebar.checkbox(
            "Include Hashtags",
            value=True,
            help="Add relevant hashtags to the description"
        )
    
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
                    
                    # Download captions button
                    st.download_button(
                        label="💾 Download Captions as TXT",
                        data=captions,
                        file_name=f"{Path(uploaded_files.name).stem}_captions.txt",
                        mime="text/plain"
                    )
                    
                    # Display word count
                    word_count = len(captions.split())
                    st.info(f"📊 Caption Statistics: {word_count} words, {len(captions)} characters")
                    
                    # Generate YouTube Description
                    if generate_description:
                        st.header("📺 YouTube Description")
                        
                        with st.spinner("Generating YouTube description with AI..."):
                            youtube_desc = generate_youtube_description_with_llm(
                                captions, 
                                video_title, 
                                custom_prompt,
                                include_timestamps, 
                                include_hashtags,
                                use_openrouter
                            )
                        
                        st.text_area(
                            "YouTube Description",
                            youtube_desc,
                            height=400,
                            help="Copy this description to use in your YouTube video"
                        )
                        
                        # Download YouTube description button
                        st.download_button(
                            label="📺 Download YouTube Description",
                            data=youtube_desc,
                            file_name=f"{Path(uploaded_files.name).stem}_youtube_description.txt",
                            mime="text/plain"
                        )
                        
                        # Combined download (captions + description)
                        combined_content = f"=== CAPTIONS ===\n\n{captions}\n\n\n=== YOUTUBE DESCRIPTION ===\n\n{youtube_desc}"
                        st.download_button(
                            label="📦 Download Both (Captions + Description)",
                            data=combined_content,
                            file_name=f"{Path(uploaded_files.name).stem}_complete.txt",
                            mime="text/plain"
                        )
    
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
                        
                        # Download captions button
                        st.download_button(
                            label=f"💾 Captions",
                            data=result['captions'],
                            file_name=f"{Path(result['filename']).stem}_captions.txt",
                            mime="text/plain",
                            key=f"download_captions_{result['filename']}",
                            use_container_width=True
                        )
                        
                        # Generate and download YouTube description if enabled
                        if generate_description:
                            youtube_desc = generate_youtube_description_with_llm(
                                result['captions'], 
                                video_title, 
                                custom_prompt,
                                include_timestamps, 
                                include_hashtags,
                                use_openrouter
                            )
                            
                            st.download_button(
                                label=f"📺 YouTube Desc",
                                data=youtube_desc,
                                file_name=f"{Path(result['filename']).stem}_youtube_description.txt",
                                mime="text/plain",
                                key=f"download_youtube_{result['filename']}",
                                use_container_width=True
                            )
                            
                            # Combined download
                            combined_content = f"=== CAPTIONS ===\n\n{result['captions']}\n\n\n=== YOUTUBE DESCRIPTION ===\n\n{youtube_desc}"
                            st.download_button(
                                label=f"📦 Both",
                                data=combined_content,
                                file_name=f"{Path(result['filename']).stem}_complete.txt",
                                mime="text/plain",
                                key=f"download_combined_{result['filename']}",
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
    
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        # Check OpenRouter API key
        try:
            openrouter_key = "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"
            if openrouter_key:
                st.success("✅ OpenRouter API configured")
            else:
                st.info("ℹ️ OpenRouter API not configured")
        except Exception:
            st.info("ℹ️ OpenRouter API not configured")
    
    # OpenRouter API Setup Instructions
    if generate_description:
        with st.expander("🔑 OpenRouter API Information"):
            st.markdown("""
            **Premium AI-powered YouTube descriptions with GPT-4o:**
            
            ✅ **Already Configured!** Your OpenRouter API key is integrated.
            
            **Features:**
            - Uses GPT-4o for superior description quality
            - Professional, engaging, and SEO-optimized content
            - Automatic fallback to local generation if needed
            - Enhanced creativity and context understanding
            
            **Benefits:**
            - Much higher quality than local generation
            - Better SEO optimization
            - More engaging call-to-actions
            - Professional formatting with emojis and sections
            
            **Cost:** Very affordable per description (~$0.01-0.05)
            
            **How it works:**
            1. Enable "Use OpenRouter GPT-4o" in sidebar (default: ON)
            2. Upload your video and generate captions
            3. Get premium AI-generated YouTube descriptions
            4. Download or copy the professional descriptions
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🎬 Caption Generator App | Powered by OpenAI Whisper, OpenRouter GPT-4o & FFmpeg</p>
        <p>Made with ❤️ for content creators</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
