#!/usr/bin/env python3
"""
Simple deployment script for Caption Generator App
This script will help you deploy the app to various platforms
"""

import os
import subprocess
import sys
import platform

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking deployment requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required!")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check if FFmpeg is available
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg is not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg is not installed")
        return False
    
    # Check if required files exist
    required_files = ['app.py', 'streamlit_app.py', 'requirements_web.txt', 'Dockerfile']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            return False
    
    return True

def deploy_docker():
    """Deploy using Docker"""
    print("\n🐳 Deploying with Docker...")
    
    try:
        # Build the Docker image
        print("Building Docker image...")
        result = subprocess.run(['docker', 'build', '-t', 'caption-generator', '.'], 
                              check=True, capture_output=True, text=True)
        print("✅ Docker image built successfully")
        
        # Run the container
        print("Starting Docker container...")
        result = subprocess.run(['docker', 'run', '-d', '-p', '8501:8501', '--name', 'caption-app', 'caption-generator'], 
                              check=True, capture_output=True, text=True)
        print("✅ Docker container started successfully")
        print("🌐 Your app is available at: http://localhost:8501")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker deployment failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Docker is not installed. Please install Docker first.")
        return False

def deploy_streamlit():
    """Deploy using Streamlit Cloud"""
    print("\n☁️ Preparing for Streamlit Cloud deployment...")
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for Streamlit deployment'], check=True)
        print("✅ Git repository initialized")
    
    print("📋 Streamlit Cloud deployment steps:")
    print("1. Push your code to GitHub")
    print("2. Go to https://share.streamlit.io/")
    print("3. Connect your GitHub repository")
    print("4. Set the main file to: streamlit_app.py")
    print("5. Deploy!")
    
    return True

def deploy_heroku():
    """Deploy using Heroku"""
    print("\n🚀 Preparing for Heroku deployment...")
    
    # Check if Heroku CLI is installed
    try:
        subprocess.run(['heroku', '--version'], check=True, capture_output=True)
        print("✅ Heroku CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Heroku CLI is not installed. Please install it first.")
        print("Download from: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    print("📋 Heroku deployment steps:")
    print("1. Run: heroku login")
    print("2. Run: heroku create your-app-name")
    print("3. Run: heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git")
    print("4. Run: heroku buildpacks:add heroku/python")
    print("5. Run: git push heroku main")
    print("6. Run: heroku open")
    
    return True

def main():
    print("🎬 Caption Generator App - Deployment Assistant")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return
    
    print("\n🎉 All requirements met! Choose your deployment method:")
    print("1. 🐳 Docker (Local)")
    print("2. ☁️ Streamlit Cloud (Free)")
    print("3. 🚀 Heroku (Free tier available)")
    print("4. 📋 Show all deployment options")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            deploy_docker()
        elif choice == "2":
            deploy_streamlit()
        elif choice == "3":
            deploy_heroku()
        elif choice == "4":
            print("\n📋 All Deployment Options:")
            print("\n🐳 Docker (Local):")
            print("   docker-compose up --build")
            print("   Access at: http://localhost:8501")
            
            print("\n☁️ Streamlit Cloud (Free):")
            print("   1. Push to GitHub")
            print("   2. Go to https://share.streamlit.io/")
            print("   3. Connect repository")
            print("   4. Deploy!")
            
            print("\n🚀 Heroku:")
            print("   1. heroku create your-app")
            print("   2. heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git")
            print("   3. git push heroku main")
            
            print("\n🌐 Railway:")
            print("   1. Connect GitHub to Railway")
            print("   2. Auto-deploy from Dockerfile")
            
            print("\n☁️ Render:")
            print("   1. Create Web Service")
            print("   2. Connect GitHub")
            print("   3. Use Docker deployment")
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Deployment cancelled by user")

if __name__ == "__main__":
    main()
