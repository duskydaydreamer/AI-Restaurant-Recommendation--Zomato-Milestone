# Deployment Plan: Railway & Vercel

This guide outlines the step-by-step process for deploying the DineWise application to production, using **Railway** for the FastAPI backend and **Vercel** for the React frontend.

---

## Part 1: Backend Deployment (Railway)

We will deploy the Python FastAPI backend to Railway. Railway natively supports Python applications and will automatically build our environment using `requirements.txt`.

### Steps:
1. **Create a Railway Project:**
   - Sign up or log into [Railway](https://railway.app/).
   - Click **New Project** → **Deploy from GitHub repo**.
   - Select your `restaurant-recommender` repository.

2. **Configure the Start Command (Optional but recommended):**
   - Railway usually detects Python and runs `uvicorn app.api:app --host 0.0.0.0 --port $PORT` automatically, but you can explicitly set the **Start Command** in the Settings tab to:
     ```bash
     uvicorn app.api:app --host 0.0.0.0 --port $PORT
     ```

3. **Set Environment Variables:**
   - Go to the **Variables** tab in your Railway service.
   - Add the following environment variable:
     - `GROQ_API_KEY`: *(Your Groq API key from console.groq.com)*

4. **Resource Requirements (Important):**
   - The application downloads a ~149MB Parquet dataset on startup. 
   - Railway's ephemeral filesystem can handle the download, but you should ensure the service has at least **512MB RAM** (1GB recommended) because the dataset is loaded entirely into memory by the API.

5. **Get the Deployed URL:**
   - Once deployed, go to the **Settings** tab and click **Generate Domain** (if one hasn't been generated automatically).
   - Save this URL (e.g., `https://your-backend-app.up.railway.app`). You will need it for the frontend.

---

## Part 2: Frontend Deployment (Vercel)

We will deploy the Vite + React frontend to Vercel. Because this is a monorepo (frontend code is in a subdirectory), we need to specify the Root Directory.

### Steps:
1. **Create a Vercel Project:**
   - Log into [Vercel](https://vercel.com/) and click **Add New** → **Project**.
   - Import your `restaurant-recommender` GitHub repository.

2. **Configure Project Settings:**
   - **Framework Preset**: Vercel will likely auto-detect Vite. If not, select **Vite**.
   - **Root Directory**: Click *Edit* and select the `frontend` directory. 
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

3. **Set Environment Variables:**
   - Open the **Environment Variables** section.
   - Add the variable to connect to your Railway backend:
     - **Name**: `VITE_API_BASE_URL`
     - **Value**: `https://your-backend-app.up.railway.app/api` *(Make sure to append `/api` to the Railway URL you got from Part 1)*

4. **Deploy:**
   - Click **Deploy**. Vercel will build the frontend and provide you with a live URL.

---

## Part 3: Post-Deployment Steps (CORS Security)

Currently, the API allows all origins by default (`*`) to make testing and initial deployment easy. 

Once your Vercel frontend is live, you should secure the backend by restricting CORS to your specific Vercel domain using environment variables.

1. Go back to your **Railway** project dashboard.
2. Open the **Variables** tab.
3. Add a new variable:
   - **Name**: `ALLOWED_ORIGINS`
   - **Value**: `https://your-vercel-frontend-url.vercel.app`
4. Railway will automatically redeploy with the new, secure CORS settings!
