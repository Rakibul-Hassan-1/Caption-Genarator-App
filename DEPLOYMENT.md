# 🚀 Deployment Guide - Caption Generator App

This guide will help you deploy your Caption Generator App to various platforms.

## 📋 Prerequisites

- Python 3.9+
- FFmpeg installed
- Git (for version control)

## 🐳 Docker Deployment (Recommended)

### Local Docker Deployment

1. **Build and run with Docker Compose:**
```bash
# Build and start the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

2. **Access the application:**
- Open your browser and go to `http://localhost:8501`

3. **Stop the application:**
```bash
docker-compose down
```

### Manual Docker Build

```bash
# Build the Docker image
docker build -t caption-generator .

# Run the container
docker run -p 8501:8501 caption-generator
```

## ☁️ Cloud Deployment Options

### 1. Heroku Deployment

1. **Install Heroku CLI:**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login and create app:**
```bash
heroku login
heroku create your-caption-generator-app
```

3. **Add FFmpeg buildpack:**
```bash
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add heroku/python
```

4. **Deploy:**
```bash
git add .
git commit -m "Deploy caption generator app"
git push heroku main
```

5. **Open your app:**
```bash
heroku open
```

### 2. Railway Deployment

1. **Connect your GitHub repository to Railway**
2. **Railway will automatically detect the Dockerfile**
3. **Set environment variables if needed**
4. **Deploy automatically on git push**

### 3. Render Deployment

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Use these settings:**
   - **Build Command:** `pip install -r requirements_web.txt`
   - **Start Command:** `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Environment:** Python 3.9

### 4. Google Cloud Run

1. **Build and push to Google Container Registry:**
```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build and tag
docker build -t gcr.io/$PROJECT_ID/caption-generator .

# Push to registry
docker push gcr.io/$PROJECT_ID/caption-generator

# Deploy to Cloud Run
gcloud run deploy caption-generator \
  --image gcr.io/$PROJECT_ID/caption-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 5. AWS Elastic Beanstalk

1. **Create a `Dockerrun.aws.json` file:**
```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "your-account.dkr.ecr.region.amazonaws.com/caption-generator:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": "8501"
    }
  ]
}
```

2. **Deploy using EB CLI:**
```bash
eb init
eb create production
eb deploy
```

## 🖥️ Local Development

### Option 1: Direct Python

1. **Install dependencies:**
```bash
pip install -r requirements_web.txt
```

2. **Run the app:**
```bash
streamlit run streamlit_app.py
```

### Option 2: Virtual Environment

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements_web.txt
```

3. **Run the app:**
```bash
streamlit run streamlit_app.py
```

## 🔧 Configuration

### Environment Variables

You can set these environment variables for customization:

- `STREAMLIT_SERVER_PORT`: Port number (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)
- `STREAMLIT_THEME_BASE`: Theme (light/dark)

### Streamlit Configuration

The app uses `.streamlit/config.toml` for configuration. You can modify:
- Server settings
- Browser behavior
- Theme settings

## 📊 Monitoring and Logs

### Docker Logs
```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f caption-generator
```

### Heroku Logs
```bash
heroku logs --tail
```

### Railway Logs
- Available in the Railway dashboard

## 🚨 Troubleshooting

### Common Issues

1. **FFmpeg not found:**
   - Ensure FFmpeg is installed in your deployment environment
   - For Docker: FFmpeg is included in the Dockerfile
   - For Heroku: Use the FFmpeg buildpack

2. **Port issues:**
   - Make sure the port is correctly configured
   - For cloud deployments, use the `$PORT` environment variable

3. **Memory issues:**
   - Large Whisper models require significant memory
   - Consider using smaller models for production
   - Monitor memory usage in your deployment platform

4. **File upload limits:**
   - Most platforms have file size limits
   - Consider implementing file size validation
   - For large files, consider chunked processing

### Performance Optimization

1. **Model Selection:**
   - Use `tiny` or `base` models for faster processing
   - Use `medium` or `large` for better accuracy

2. **Caching:**
   - Streamlit automatically caches functions
   - Consider implementing result caching for repeated requests

3. **Resource Limits:**
   - Monitor CPU and memory usage
   - Scale resources based on demand

## 🔒 Security Considerations

1. **File Upload Security:**
   - Validate file types and sizes
   - Scan uploaded files for malware
   - Implement rate limiting

2. **Access Control:**
   - Consider adding authentication
   - Implement IP whitelisting if needed
   - Use HTTPS in production

3. **Data Privacy:**
   - Don't store uploaded files permanently
   - Implement data retention policies
   - Consider GDPR compliance

## 📈 Scaling

### Horizontal Scaling
- Use load balancers for multiple instances
- Implement session management
- Consider using Redis for shared state

### Vertical Scaling
- Increase memory and CPU resources
- Use faster storage (SSD)
- Optimize model loading

## 🆘 Support

If you encounter issues:

1. Check the logs for error messages
2. Verify all dependencies are installed
3. Ensure FFmpeg is available
4. Check platform-specific documentation
5. Review the troubleshooting section above

## 📝 Notes

- The app automatically cleans up temporary files
- Processing time depends on video length and model size
- Large models require more memory but provide better accuracy
- Consider implementing a queue system for high-traffic deployments

---

**Happy Deploying! 🚀**
