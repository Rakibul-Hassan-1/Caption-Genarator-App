#!/usr/bin/env python3
"""
Local development runner for Caption Generator App
This script helps you run the app locally with proper setup
"""

import subprocess
import sys
import os
import platform

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_web.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def run_streamlit():
    """Run the Streamlit app"""
    print("🚀 Starting Caption Generator App...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py'], 
                      check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")

def main():
    print("🎬 Caption Generator App - Local Development Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg is not installed!")
        print("\n📥 Please install FFmpeg:")
        if platform.system() == "Windows":
            print("  • winget install ffmpeg")
            print("  • choco install ffmpeg")
            print("  • Or download from https://ffmpeg.org/download.html")
        elif platform.system() == "Darwin":  # macOS
            print("  • brew install ffmpeg")
        else:  # Linux
            print("  • sudo apt install ffmpeg")
        sys.exit(1)
    
    print("✅ FFmpeg is available")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('.streamlit', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    print("\n🎉 Setup complete! Starting the app...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 50)
    
    # Run the app
    run_streamlit()

if __name__ == "__main__":
    main()
