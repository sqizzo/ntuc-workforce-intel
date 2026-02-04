# Deployment Guide - Monorepo Setup

This project uses a monorepo structure with:

- **Backend**: FastAPI (Python) deployed on **Render**
- **Frontend**: Next.js deployed on **Vercel**

---

## 🚀 Backend Deployment (Render)

### Prerequisites

1. Create a [Render](https://render.com) account
2. Have your OpenAI API key ready

### Steps

1. **Connect Repository**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the branch: `features_scraping_enhanced` (or `main`)

2. **Configure Service**
   - Render will auto-detect `render.yaml`
   - Or manually configure:
     - **Name**: `ntuc-workforce-backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `cd backend-py && pip install -r requirements.txt`
     - **Start Command**: `cd backend-py && uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free (or choose your plan)
     - **Region**: Singapore (or closest to your users)

3. **Set Environment Variables** (in Render dashboard)

   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here
   FRONTEND_URL=https://your-frontend.vercel.app
   PYTHON_ENV=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5-10 minutes)
   - Copy your backend URL: `https://your-backend.onrender.com`

5. **Verify**
   - Visit: `https://your-backend.onrender.com/health`
   - Should return: `{"status":"healthy","service":"ntuc-workforce-backend","version":"1.0.0"}`
   - Visit: `https://your-backend.onrender.com/docs` for API documentation

---

## 🎨 Frontend Deployment (Vercel)

### Prerequisites

1. Create a [Vercel](https://vercel.com) account
2. Have your backend URL from Render

### Steps

1. **Connect Repository**
   - Go to Vercel Dashboard
   - Click "Add New..." → "Project"
   - Import your GitHub repository

2. **Configure Project**
   - Vercel auto-detects Next.js (root directory)
   - **Framework Preset**: Next.js
   - **Root Directory**: `./` (default)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

3. **Set Environment Variables** (in Vercel dashboard)

   ```
   NEXT_PUBLIC_PYTHON_BACKEND_URL=https://your-backend.onrender.com
   ```

   ⚠️ **Important**: Replace `your-backend` with your actual Render service name

4. **Deploy**
   - Click "Deploy"
   - Wait for build (~2-3 minutes)
   - Copy your frontend URL: `https://your-project.vercel.app`

5. **Update Backend CORS**
   - Go back to Render dashboard
   - Update `FRONTEND_URL` environment variable to your Vercel URL
   - Redeploy backend (or it will auto-redeploy)

6. **Verify**
   - Visit your Vercel URL
   - Test scraping functionality
   - Check network tab for API calls to your Render backend

---

## 🔄 Continuous Deployment

### Automatic Deployments

**Render** (Backend):

- Automatically deploys on every push to `main` or `features_scraping_enhanced` branch
- Monitors `/health` endpoint

**Vercel** (Frontend):

- Automatically deploys on every push to connected branch
- Preview deployments for PRs

### Manual Deployment

**Render**:

```bash
git push origin features_scraping_enhanced
# Render automatically deploys
```

**Vercel**:

```bash
git push origin features_scraping_enhanced
# Vercel automatically deploys
```

---

## 🔧 Local Development

### Backend

```bash
cd backend-py
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs at: `http://localhost:8000`

### Frontend

```bash
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

### Environment Variables

**Local `.env.local`** (for development):

```env
NEXT_PUBLIC_PYTHON_BACKEND_URL=http://localhost:8000
PYTHON_BACKEND_URL=http://localhost:8000
```

**Production** (set in Render/Vercel dashboards):

- See deployment steps above

---

## 📊 Monitoring

### Health Checks

**Backend Health**: `https://your-backend.onrender.com/health`

- Returns: `{"status":"healthy","service":"ntuc-workforce-backend","version":"1.0.0"}`

**API Documentation**: `https://your-backend.onrender.com/docs`

- Interactive Swagger UI for testing endpoints

### Logs

**Render**:

- Dashboard → Your Service → Logs tab
- Real-time logs for debugging

**Vercel**:

- Dashboard → Your Project → Deployments → Click deployment → Functions tab
- Shows build logs and runtime logs

---

## 🐛 Troubleshooting

### CORS Issues

**Problem**: Frontend can't connect to backend
**Solution**:

1. Verify `FRONTEND_URL` is set correctly in Render
2. Check browser console for CORS errors
3. Ensure frontend URL matches exactly (with https://)

### Backend Not Starting

**Problem**: Render build fails or crashes
**Solution**:

1. Check logs in Render dashboard
2. Verify all dependencies in `requirements.txt`
3. Check Python version compatibility

### Environment Variables Not Working

**Problem**: API calls fail with authentication errors
**Solution**:

1. Verify all environment variables are set in Render/Vercel
2. Redeploy after updating environment variables
3. Check variable names match exactly (case-sensitive)

### Cold Starts (Render Free Tier)

**Problem**: First request takes 30-60 seconds
**Solution**:

- This is normal for free tier (service spins down after 15 min inactivity)
- Consider upgrading to paid plan for always-on service
- Or use a cron job to ping `/health` every 10 minutes

---

## 🔐 Security Checklist

- [ ] OpenAI API key stored in environment variables (not in code)
- [ ] CORS configured to allow only your frontend domain
- [ ] Environment variables marked as "secret" in Render
- [ ] Frontend uses `NEXT_PUBLIC_` prefix only for truly public values
- [ ] `.env.local` added to `.gitignore`
- [ ] Rate limiting implemented for production (optional)

---

## 📝 Post-Deployment Checklist

- [ ] Backend health check returns 200 OK
- [ ] Frontend loads successfully
- [ ] Can perform company search from frontend
- [ ] Hypothesis analysis works end-to-end
- [ ] Google News scraper fetches data
- [ ] All 52 signals appear in hypothesis results
- [ ] Source distribution counts match (News: 42, Social: 10)
- [ ] Environment variables secure and correct
- [ ] Monitoring set up (optional: Render metrics, Vercel analytics)

---

## 🚀 Going Live

1. ✅ Complete all deployment steps above
2. ✅ Test thoroughly on production URLs
3. ✅ Run through post-deployment checklist
4. ✅ Update any documentation with production URLs
5. ✅ Share with team/users

**Production URLs**:

- Backend: `https://your-backend.onrender.com`
- Frontend: `https://your-project.vercel.app`
- API Docs: `https://your-backend.onrender.com/docs`

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

---

**Last Updated**: February 4, 2026
