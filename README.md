# 🎬 Caption Generator App - Final Version

## 📱 **Option 1: Web Interface (Recommended)**

### **Quick Start:**
```bash
python install_and_run.py
```
This will:
- ✅ Install all dependencies automatically
- ✅ Check system requirements
- ✅ Start the web app at http://localhost:8503

### **Manual Start:**
```bash
# Install dependencies
pip install streamlit openai-whisper torch torchaudio

# Run the app
streamlit run app_web.py --server.port 8503 --server.address localhost
```

## 💻 **Option 2: Command Line (Original)**

```bash
# Process a single video
python app.py your_video.mp4

# Process all demo videos
python app.py --folder demo_videos/

# Process with high quality
python app.py your_video.mp4 --model large --language en
```

## 🐳 **Option 3: Docker (Optional)**

```bash
# Build and run with Docker
docker build -t caption-generator .
docker run -p 8501:8501 caption-generator

# Access at: http://localhost:8501
```

## ☁️ **Option 4: Streamlit Cloud Deployment (Free)**

1. **Push to GitHub**: `git push origin main`
2. **Go to Streamlit Cloud**: https://share.streamlit.io/
3. **Sign in with GitHub**
4. **Deploy New App**:
   - Select your repository
   - Main file: `app_web.py`
   - Click "Deploy!"
5. **Your app is live**: `https://your-app-name.streamlit.app`

## 🎯 **What You Get:**

### **Web Interface Features:**
- 📹 **Single & Batch Upload** - Upload one or multiple videos at once
- 🤖 **AI Models** - Choose from 5 Whisper model sizes
- 🌍 **Multi-language** - Support for 10+ languages
- 📊 **Real-time Progress** - Live processing updates for batch operations
- 💾 **Download Results** - Individual caption downloads for each video
- 🎨 **Modern UI** - Clean, professional interface
- 📦 **Batch Processing** - Process multiple videos with progress tracking

### **Command Line Features:**
- ⚡ **Fast Processing** - Direct video processing
- 📁 **Batch Processing** - Process multiple videos
- 🔧 **Advanced Options** - Full control over settings
- 📊 **Progress Tracking** - Detailed processing logs

## 🔧 **System Requirements:**

- ✅ **Python 3.9+**
- ✅ **FFmpeg** (for audio extraction)
- ✅ **4GB+ RAM** (for larger models)
- ✅ **Internet connection** (for model downloads)

## 📦 **Files Included:**

- `app_web.py` - **Main web application**
- `app.py` - **Command-line version**
- `requirements.txt` - **Python dependencies**
- `packages.txt` - **FFmpeg for Streamlit Cloud**
- `README.md` - **Documentation**

## 🎬 **How to Use:**

### **Web Interface:**
1. Run: `streamlit run app_web.py`
2. Upload your videos (single or batch)
3. Choose model and language settings
4. Generate and download captions

### **Command Line:**
```bash
# Single video
python app.py your_video.mp4

# Multiple videos
python app.py video1.mp4 video2.mp4 video3.mp4

# Process folder
python app.py --folder your_videos_folder/
```

## 📦 **New Batch Upload Feature:**

### **Single Video Mode:**
- Upload one video at a time
- Perfect for individual projects
- Quick processing and download

### **Batch Mode:**
- Upload multiple videos simultaneously
- Real-time progress tracking
- Individual downloads for each video
- Success/failure summary
- Perfect for processing entire folders

### **Batch Processing Benefits:**
- ⚡ **Efficient**: Process multiple videos in one go
- 📊 **Progress Tracking**: See real-time progress for each video
- 📦 **Individual Downloads**: Get separate caption files for each video
- 🎯 **Error Handling**: Clear success/failure reporting
- 💾 **Organized Results**: Each video's captions are clearly labeled
- 🎨 **Clean Layout**: Results displayed in organized columns

## 🆘 **Troubleshooting:**

### **FFmpeg Issues:**
```bash
# Windows
winget install ffmpeg

# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### **Whisper Issues:**
```bash
pip install openai-whisper
```

### **Memory Issues:**
- Use smaller models (tiny, base)
- Process shorter videos
- Close other applications

## 🎉 **You're All Set!**

Your Caption Generator App is now:
- ✅ **Error-free**
- ✅ **Web-enabled**
- ✅ **Cloud-deployable**
- ✅ **Production-ready**
- ✅ **User-friendly**

**Choose your preferred method and start generating captions! 🚀**

---

