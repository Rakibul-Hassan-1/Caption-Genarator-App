# 🚀 Streamlit Cloud Deployment Guide

## Complete Step-by-Step Instructions

### **Step 1: Create GitHub Repository**

1. **Go to GitHub**: Visit [github.com](https://github.com) and sign in
2. **Create New Repository**:
   - Click the "+" icon in the top right
   - Select "New repository"
   - Repository name: `caption-generator-app` (or any name you prefer)
   - Description: `AI-powered Caption Generator with Batch Processing`
   - Make it **Public** (required for free Streamlit Cloud)
   - **Don't** initialize with README (we already have one)
   - Click "Create repository"

### **Step 2: Push Your Code to GitHub**

Run these commands in your terminal:

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/caption-generator-app.git

# Push your code
git branch -M main
git push -u origin main
```

**Alternative: Use GitHub Desktop or VS Code Git integration**

### **Step 3: Deploy to Streamlit Cloud**

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)
2. **Sign in with GitHub**: Click "Sign in with GitHub"
3. **Authorize Streamlit**: Allow Streamlit to access your repositories
4. **Deploy New App**:
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/caption-generator-app`
   - Main file path: `app_web.py`
   - App URL: Choose a custom name (e.g., `your-caption-generator`)
   - Click "Deploy!"

### **Step 4: Configure App Settings**

After deployment, you may need to configure:

1. **Go to your app dashboard**
2. **Click "Settings"**
3. **Add Environment Variables** (if needed):
   - No special environment variables required for basic deployment

### **Step 5: Test Your Deployed App**

1. **Wait for deployment** (usually 2-5 minutes)
2. **Visit your app URL**: `https://your-caption-generator.streamlit.app`
3. **Test the features**:
   - Upload a single video
   - Try batch upload
   - Test different models and languages

## 🔧 **Important Notes for Streamlit Cloud**

### **File Requirements:**
- ✅ `app_web.py` - Main application file
- ✅ `requirements.txt` - Dependencies
- ✅ `README.md` - Documentation

### **Limitations:**
- ⚠️ **File Size Limit**: 200MB per file upload
- ⚠️ **Memory Limit**: 1GB RAM (use smaller models for large videos)
- ⚠️ **Timeout**: 30 minutes per session
- ⚠️ **No FFmpeg**: Streamlit Cloud doesn't include FFmpeg by default

### **FFmpeg Solution for Streamlit Cloud:**

Since Streamlit Cloud doesn't include FFmpeg, you have two options:

#### **Option A: Use Command Line Version**
Your command-line version (`app.py`) works perfectly and doesn't need FFmpeg in the cloud.

#### **Option B: Add FFmpeg to Streamlit Cloud**
Create a `packages.txt` file:

```bash
# Create packages.txt file
echo "ffmpeg" > packages.txt
```

Then add it to your repository and redeploy.

## 🎯 **Deployment Checklist**

Before deploying, ensure:

- [ ] All files are committed to Git
- [ ] Repository is public
- [ ] `app_web.py` is the main file
- [ ] `requirements.txt` includes all dependencies
- [ ] README.md is updated
- [ ] Test locally first

## 🚀 **Quick Deployment Commands**

```bash
# 1. Commit all changes
git add .
git commit -m "Ready for Streamlit deployment"

# 2. Push to GitHub
git push origin main

# 3. Go to share.streamlit.io and deploy!
```

## 📱 **Your App URLs**

After deployment, you'll have:
- **App URL**: `https://your-app-name.streamlit.app`
- **Dashboard**: `https://share.streamlit.io` (to manage your app)

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"App not found"**: Check repository name and main file path
2. **"Import errors"**: Verify `requirements.txt` has all dependencies
3. **"FFmpeg not found"**: Add `packages.txt` with `ffmpeg`
4. **"Memory errors"**: Use smaller models or shorter videos

### **Need Help?**
- Streamlit Cloud Docs: [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
- GitHub Issues: Create an issue in your repository

## 🎉 **Success!**

Once deployed, your Caption Generator App will be:
- ✅ **Publicly accessible** via web URL
- ✅ **Free to use** for anyone
- ✅ **Automatically updated** when you push changes
- ✅ **Scalable** and reliable

**Your app is now live on the internet! 🌐**
