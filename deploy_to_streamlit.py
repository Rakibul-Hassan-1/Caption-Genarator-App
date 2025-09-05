#!/usr/bin/env python3
"""
Quick deployment script for Streamlit Cloud
This script helps you prepare and deploy your Caption Generator App
"""

import subprocess
import sys
import os
import webbrowser

def check_git_status():
    """Check if git repository is ready"""
    print("🔍 Checking Git status...")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes:")
            print(result.stdout)
            return False
        else:
            print("✅ Git repository is clean")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False

def check_required_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        'app_web.py',
        'requirements.txt',
        'packages.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def commit_and_push():
    """Commit and push changes to GitHub"""
    print("📤 Committing and pushing to GitHub...")
    
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Files added to git")
        
        # Commit
        subprocess.run(['git', 'commit', '-m', 'Deploy to Streamlit Cloud'], check=True)
        print("✅ Changes committed")
        
        # Push
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Pushed to GitHub")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def open_streamlit_cloud():
    """Open Streamlit Cloud in browser"""
    print("🌐 Opening Streamlit Cloud...")
    webbrowser.open('https://share.streamlit.io')
    print("✅ Streamlit Cloud opened in your browser")

def main():
    print("🚀 Caption Generator App - Streamlit Deployment Assistant")
    print("=" * 60)
    
    # Check git status
    if not check_git_status():
        print("\n❌ Please commit your changes first:")
        print("   git add .")
        print("   git commit -m 'Your commit message'")
        return
    
    # Check required files
    if not check_required_files():
        print("\n❌ Missing required files. Please ensure all files are present.")
        return
    
    print("\n🎉 Everything looks good!")
    
    # Ask user if they want to proceed
    try:
        proceed = input("\n🚀 Ready to deploy? (y/n): ").strip().lower()
        if proceed not in ['y', 'yes']:
            print("❌ Deployment cancelled")
            return
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled")
        return
    
    # Commit and push
    if commit_and_push():
        print("\n✅ Code pushed to GitHub successfully!")
        
        # Open Streamlit Cloud
        open_streamlit_cloud()
        
        print("\n📋 Next steps:")
        print("1. Sign in to Streamlit Cloud with your GitHub account")
        print("2. Click 'New app'")
        print("3. Select your repository")
        print("4. Set main file to: app_web.py")
        print("5. Click 'Deploy!'")
        print("\n🎉 Your app will be live in a few minutes!")
        
    else:
        print("\n❌ Failed to push to GitHub. Please check your git configuration.")

if __name__ == "__main__":
    main()
