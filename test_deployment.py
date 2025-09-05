#!/usr/bin/env python3
"""
Test script to verify the deployment setup
"""

import subprocess
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import whisper
        print("✅ OpenAI Whisper")
    except ImportError as e:
        print(f"❌ Whisper import failed: {e}")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    return True

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\n🧪 Testing FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg command failed")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        return False

def test_streamlit_app():
    """Test if the Streamlit app can be loaded"""
    print("\n🧪 Testing Streamlit app...")
    
    if not os.path.exists('streamlit_app.py'):
        print("❌ streamlit_app.py not found")
        return False
    
    try:
        # Try to import the app module
        import importlib.util
        spec = importlib.util.spec_from_file_location("streamlit_app", "streamlit_app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        print("✅ Streamlit app loads successfully")
        return True
    except Exception as e:
        print(f"❌ Streamlit app load failed: {e}")
        return False

def main():
    print("🎬 Caption Generator App - Deployment Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test FFmpeg
    if not test_ffmpeg():
        all_tests_passed = False
    
    # Test Streamlit app
    if not test_streamlit_app():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Your app is ready for deployment.")
        print("\n📱 To run locally:")
        print("   python -m streamlit run streamlit_app.py")
        print("\n🐳 To run with Docker:")
        print("   docker-compose up --build")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
