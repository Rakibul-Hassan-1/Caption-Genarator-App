#!/usr/bin/env python3
"""
Installation and setup script for Caption Generator App
This script will install all dependencies and run the app
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    print("📦 Installing required packages...")
    
    packages = [
        "streamlit",
        "openai-whisper",
        "torch",
        "torchaudio"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed")
        print("Please install FFmpeg:")
        print("  Windows: winget install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False

def run_app():
    """Run the Streamlit app"""
    print("🚀 Starting Caption Generator App...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_web.py", 
                       "--server.port", "8503", "--server.address", "localhost"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run app: {e}")
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")

def main():
    print("🎬 Caption Generator App - Installation & Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not install_requirements():
        print("❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg is required but not found.")
        print("Please install FFmpeg and try again.")
        sys.exit(1)
    
    print("\n🎉 Setup complete! Starting the app...")
    print("📱 The app will open in your browser at http://localhost:8503")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 50)
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main()
