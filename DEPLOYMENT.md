# 🚀 Streamlit Cloud Deployment Guide

## Caption Generator App - Deployment Instructions

### 📋 Prerequisites
- GitHub repository with your code
- Streamlit Cloud account (free)
- OpenRouter API key

### 🔧 Deployment Steps

#### 1. **Prepare Your Repository**
- ✅ All code is committed and pushed to GitHub
- ✅ `requirements.txt` is updated with all dependencies
- ✅ Main app file is `app_web.py`

#### 2. **Deploy to Streamlit Cloud**

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)

2. **Sign in**: Use your GitHub account to sign in

3. **New App**: Click "New app"

4. **Repository Settings**:
   - **Repository**: `Rakibul-Hassan-1/Caption-Genarator-App`
   - **Branch**: `main`
   - **Main file path**: `app_web.py`

5. **App URL**: Choose your app URL (e.g., `caption-generator-app`)

#### 3. **Configure Secrets**

In the Streamlit Cloud dashboard, add these secrets:

```toml
OPENROUTER_API_KEY = "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"
SITE_URL = "https://your-app-name.streamlit.app"
SITE_NAME = "Caption Generator App"
```

**How to add secrets:**
1. Go to your app's settings in Streamlit Cloud
2. Click "Secrets"
3. Add the above configuration

#### 4. **Deploy**
- Click "Deploy!"
- Wait for the deployment to complete (5-10 minutes)

### 🎯 Features After Deployment

- ✅ **AI-Powered Captions**: Whisper transcription
- ✅ **Premium Descriptions**: GPT-4o via OpenRouter
- ✅ **Batch Processing**: Multiple videos at once
- ✅ **Multiple Languages**: Auto-detect or specify
- ✅ **Download Options**: TXT files for captions and descriptions

### 🔧 Troubleshooting

**Common Issues:**

1. **FFmpeg not found**: Streamlit Cloud doesn't support FFmpeg
   - **Solution**: The app will show an error message
   - **Workaround**: Use local processing for audio extraction

2. **API Key Issues**: 
   - Check secrets are properly configured
   - Verify API key is correct

3. **Memory Issues**:
   - Use smaller Whisper models (tiny, base)
   - Process shorter videos

### 📊 App Performance

- **Free Tier**: 1GB RAM, 1 CPU
- **Recommended**: Use "base" or "small" Whisper models
- **Video Size**: Keep under 100MB for best performance

### 🌐 Your Live App

Once deployed, your app will be available at:
`https://your-app-name.streamlit.app`

### 📞 Support

If you encounter issues:
1. Check the Streamlit Cloud logs
2. Verify all secrets are configured
3. Test with smaller video files first

---

**🎉 Congratulations!** Your AI-powered Caption Generator is now live on the web!
