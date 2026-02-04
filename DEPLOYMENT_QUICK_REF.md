# Quick Deployment Reference

## 🎯 Environment Variables

### Render (Backend)

```
OPENAI_API_KEY=sk-proj-...your-key...
FRONTEND_URL=https://your-frontend.vercel.app
PYTHON_ENV=production
```

### Vercel (Frontend)

```
NEXT_PUBLIC_PYTHON_BACKEND_URL=https://your-backend.onrender.com
```

---

## 🔗 Important URLs

After deployment, you'll have:

- **Backend API**: `https://your-backend.onrender.com`
- **Backend Health**: `https://your-backend.onrender.com/health`
- **API Docs**: `https://your-backend.onrender.com/docs`
- **Frontend**: `https://your-project.vercel.app`

---

## ⚡ Quick Commands

### Deploy to Render (Backend)

```bash
git add .
git commit -m "deploy: backend updates"
git push origin features_scraping_enhanced
# Render auto-deploys
```

### Deploy to Vercel (Frontend)

```bash
git add .
git commit -m "deploy: frontend updates"
git push origin features_scraping_enhanced
# Vercel auto-deploys
```

### Local Development

```bash
# Terminal 1 - Backend
cd backend-py
python main.py

# Terminal 2 - Frontend
npm run dev
```

---

## ✅ Verification Steps

1. **Backend Health Check**

   ```bash
   curl https://your-backend.onrender.com/health
   ```

   Should return: `{"status":"healthy",...}`

2. **Frontend Access**
   - Open: `https://your-project.vercel.app`
   - Should load the application

3. **End-to-End Test**
   - Search for "Twelve Cupcakes" on frontend
   - Check that it fetches data from backend
   - Verify hypothesis analysis shows 52 signals

---

## 🐛 Common Issues

### CORS Error

```
Access to XMLHttpRequest blocked by CORS policy
```

**Fix**: Update `FRONTEND_URL` in Render dashboard, then redeploy

### Backend Not Responding

```
Failed to fetch or 504 Gateway Timeout
```

**Fix**: Render free tier has cold starts (30-60s first request)

### Environment Variable Not Found

```
KeyError: 'OPENAI_API_KEY'
```

**Fix**: Set environment variable in Render dashboard, then redeploy

---

## 📱 Mobile Checklist

When sharing with users:

- [ ] Test on mobile browsers
- [ ] Check responsive design
- [ ] Verify API calls work over mobile network
- [ ] Test performance on slower connections

---

**See DEPLOYMENT.md for detailed instructions**
