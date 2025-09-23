# Deployment Setup for Contentstack Marketplace App

## Overview
You now have **2 separate public URLs** for different purposes:

### 🌐 Frontend-Backend Communication
- **Domain**: `unlifted-sisterlike-melinda.ngrok-free.dev`
- **Purpose**: React app calls Flask API
- **Auth Token**: `336PFm2MonGP4SYX5Uh2VIaf7uZ_3VCSqyYAdMZdF71tzi9Jk`

### 🔗 Webhook Communication  
- **Domain**: `destined-mammoth-flowing.ngrok-free.app`
- **Purpose**: Contentstack sends webhooks to Flask
- **Auth Token**: `2nWHZkIZ0gAxAgUBeu6uBpsDZWY_4iQJJaypdUd28qtTYA3NW`

## Deployment Steps

### 1. Start Frontend Ngrok Tunnel
```bash
python frontend_ngrok.py
```
This exposes your Flask API at: `https://unlifted-sisterlike-melinda.ngrok-free.dev`

### 2. Start Webhook Ngrok Tunnel (Optional)
```bash
python webhook_ngrok.py
```
This exposes webhooks at: `https://destined-mammoth-flowing.ngrok-free.app/webhook`

### 3. Start Flask Backend
```bash
python webhook.py
```
Runs locally on port 5000, accessible via both ngrok tunnels.

### 4. Deploy React Frontend
Build and deploy your React app to any hosting service:
```bash
cd contentstack-demo
npm run build
```

The React app is configured to call: `https://unlifted-sisterlike-melinda.ngrok-free.dev`

## Configuration Summary

### Environment Variables
- `NGROK_FRONTEND_DOMAIN`: `unlifted-sisterlike-melinda.ngrok-free.dev`
- `NGROK_FRONTEND_AUTH_TOKEN`: `336PFm2MonGP4SYX5Uh2VIaf7uZ_3VCSqyYAdMZdF71tzi9Jk`
- `NGROK_WEBHOOK_DOMAIN`: `destined-mammoth-flowing.ngrok-free.app`

### React App Configuration
- `REACT_APP_API_URL`: `https://unlifted-sisterlike-melinda.ngrok-free.dev`

### CORS Configuration
Flask now accepts requests from:
- `http://localhost:3000` (local development)
- `https://unlifted-sisterlike-melinda.ngrok-free.dev` (production)

## Benefits
✅ **Separation of Concerns**: Frontend and webhook traffic are isolated  
✅ **Static URLs**: Both ngrok domains are persistent  
✅ **Flexible Deployment**: Deploy React anywhere, keep Flask local  
✅ **Webhook Compatibility**: Contentstack webhooks continue working  

## Usage
1. **For Development**: Use localhost URLs
2. **For Production**: Use the respective ngrok domains
3. **For Contentstack**: Configure webhook to the webhook domain