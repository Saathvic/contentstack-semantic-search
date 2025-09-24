# Render Deployment Guide for Contentstack Semantic Search

## Quick Deploy to Render

1. **Connect Repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository containing this code

2. **Configure Deployment Settings**
   - **Name**: `contentstack-semantic-search`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -c gunicorn.conf.py webhook:app`
   - **Instance Type**: `Starter` (free tier)

3. **Set Environment Variables**
   Add these environment variables in Render:
   ```
   CONTENTSTACK_API_KEY=your_contentstack_api_key
   CONTENTSTACK_DELIVERY_TOKEN=your_contentstack_delivery_token
   CONTENTSTACK_ENVIRONMENT=your_environment_name
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=your_pinecone_index_name
   FLASK_ENV=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (~2-3 minutes)
   - Your API will be available at: `https://your-service-name.onrender.com`

## Update Frontend

After deployment, update your React app's API endpoint:

```javascript
// In your React component
const API_BASE_URL = 'https://your-service-name.onrender.com';

// Replace localhost URLs with your Render URL
const response = await fetch(`${API_BASE_URL}/semantic_search`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query: searchQuery })
});
```

## Testing Production Deployment

Test your deployed API:

```bash
curl -X POST https://your-service-name.onrender.com/semantic_search \
  -H "Content-Type: application/json" \
  -d '{"query": "red sneakers"}'
```

## Key Features

✅ **Production-Ready**: Optimized Flask app with Gunicorn WSGI server
✅ **Real Data**: Connected to actual Pinecone vector database
✅ **CORS Configured**: Supports cross-origin requests from your frontend
✅ **Environment Detection**: Automatically detects production vs development
✅ **Scalable**: Configured for horizontal scaling on Render

## Architecture

- **Backend**: Flask + Gunicorn on Render
- **Vector Database**: Pinecone for semantic search
- **CMS**: Contentstack for product data
- **Frontend**: React (deploy separately to Render Static Site)

## Monitoring

- **Logs**: Available in Render dashboard
- **Health Check**: `GET /` returns API status
- **Metrics**: Render provides CPU, memory, and request metrics

Your Contentstack semantic search application is now production-ready! 🚀