# 🎬 Caption Generator App

A powerful, AI-powered application that automatically generates high-quality captions from video files using OpenAI's Whisper model and optimized FFmpeg audio processing.

## ✨ Features

- 🎵 **High-Quality Audio Extraction**: Uses FFmpeg with optimized settings for speech recognition
- 🤖 **Advanced AI Transcription**: Powered by OpenAI Whisper with multiple model sizes
- 🌍 **Multi-Language Support**: Auto-detection and manual language specification
- 📁 **Batch Processing**: Process multiple videos or entire folders at once
- 📂 **Organized Output**: Clean folder structure with processing summaries
- 🚀 **Fast & Reliable**: No more crashes or disturbances from moviepy
- 📊 **Progress Tracking**: Real-time progress updates and detailed summaries

## 🚀 Quick Start

### 1. Install FFmpeg (Required)

**Windows:**
```bash
# Option 1: Using winget (recommended)
winget install ffmpeg

# Option 2: Using Chocolatey
choco install ffmpeg

# Option 3: Manual download
# Download from https://ffmpeg.org/download.html and add to PATH
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or install manually
pip install openai-whisper torch torchaudio
```

### 3. Run the App

```bash
# Process a single video
python app.py your_video.mp4

# Process multiple videos
python app.py video1.mp4 video2.mp4 video3.mp4

# Process entire folder
python app.py --folder demo_videos/
```

## 📖 Usage Guide

### Basic Usage

#### Single Video Processing
```bash
# Basic usage
python app.py video.mp4

# With custom output folder
python app.py video.mp4 --output my_captions

# With specific model for better quality
python app.py video.mp4 --model medium --output high_quality
```

#### Multiple Video Processing
```bash
# Process multiple videos
python app.py video1.mp4 video2.mp4 video3.mp4

# Batch processing with custom settings
python app.py video1.mp4 video2.mp4 --model large --language en
```

#### Folder Processing
```bash
# Process all videos in a folder
py app.py --folder demo_videos/

# Process folder with enhanced settings
py app.py --folder demo_videos/ --model medium --language en
```

### Advanced Options

#### Model Selection
```bash
--model tiny      # Fastest, least accurate
--model base      # Good balance (default)
--model small     # Better accuracy
--model medium    # High accuracy (recommended)
--model large     # Best accuracy, slowest
```

#### Language Specification
```bash
--language en     # English
--language bn     # Bengali
--language hi     # Hindi
--language zh     # Chinese
--language ja     # Japanese
--language ko     # Korean
# Leave empty for auto-detection
```

#### Output Control
```bash
--output my_folder    # Custom output folder
--batch               # Force batch processing mode
```

## 🔧 Command Line Reference

```bash
python app.py [OPTIONS] [VIDEO_FILES...]

OPTIONS:
  -h, --help            Show help message
  --output, -o          Output folder for captions (default: captions)
  --model, -m           Whisper model size (default: base)
  --batch, -b           Force batch processing mode
  --folder, -f          Process all videos in specified folder
  --language, -l        Specify language for transcription

EXAMPLES:
  # Process single video
  python app.py video.mp4

  # Process with high quality
  python app.py video.mp4 --model large --language en

  # Process folder
  python app.py --folder /videos --model medium

  # Batch process multiple videos
  python app.py v1.mp4 v2.mp4 v3.mp4 --output batch_captions
```

## 📁 Output Structure

### Single Video
```
captions/
└── video_name_captions.txt
```

### Batch Processing
```
output_folder/
├── video1_captions.txt
├── video2_captions.txt
├── video3_captions.txt
└── processing_summary.txt
```

## 🎯 Best Practices

### For Best Quality
1. **Use larger models**: `--model medium` or `--model large`
2. **Specify language**: `--language en` for English content
3. **Good audio quality**: Ensure your videos have clear audio
4. **Proper lighting**: Well-lit videos often have better audio

### For Speed
1. **Use smaller models**: `--model tiny` or `--model base`
2. **Process in batches**: Use `--folder` for multiple videos
3. **SSD storage**: Faster storage improves processing speed

## 🆘 Troubleshooting

### Common Issues

#### "FFmpeg is not installed"
```bash
# Install FFmpeg (see installation section above)
winget install ffmpeg  # Windows
sudo apt install ffmpeg  # Linux
brew install ffmpeg  # macOS
```

#### "Whisper is not installed"
```bash
pip install openai-whisper
```

#### Poor Caption Quality
```bash
# Use larger model
python app.py video.mp4 --model large

# Specify language
python app.py video.mp4 --language en

# Check audio quality of your video
```

#### Memory Issues
```bash
# Use smaller model
python app.py video.mp4 --model tiny

# Process shorter videos first
# Close other applications to free memory
```

### Performance Tips

- **Model Size**: Larger models = better quality but slower processing
- **Language**: Specifying language improves accuracy
- **Audio Quality**: Better audio = better captions
- **Batch Processing**: More efficient than processing individually

## 📋 Supported Formats

### Video Formats
- MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP
- Any format supported by FFmpeg

### Audio Formats (Output)
- WAV (PCM 16-bit, 44.1kHz, Mono)
- Optimized for speech recognition

## 🌟 What's New in This Version

- ✅ **FFmpeg Integration**: Replaced moviepy with reliable FFmpeg
- ✅ **Enhanced Audio Processing**: Optimized settings for speech recognition
- ✅ **Better Whisper Models**: Support for all model sizes
- ✅ **Language Detection**: Automatic and manual language specification
- ✅ **Batch Processing**: Process multiple videos efficiently
- ✅ **Progress Tracking**: Real-time updates and detailed summaries
- ✅ **Error Handling**: Better error messages and recovery

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **OpenAI Whisper**: For the powerful speech recognition model
- **FFmpeg**: For reliable audio/video processing
- **PyTorch**: For the machine learning framework

---

**Made with ❤️ for content creators who need high-quality captions!**

For support or questions, please check the troubleshooting section above or create an issue in the project repository.
