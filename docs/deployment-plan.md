# Future Deployment Plan

*Note: DineWise is currently running locally. This plan outlines the strategy for a future production release.*

## Frontend Deployment (React + Vite)
- **Target Platform**: Vercel.
- **Strategy**: The `frontend/` directory will be built using `npm run build`. Vercel provides excellent out-of-the-box support for Vite projects, enabling continuous deployment from the GitHub repository.
- **Environment**: The frontend will need an environment variable pointing to the deployed backend URL instead of `localhost`.

## Backend Deployment (FastAPI)
- **Target Platform**: Railway or Render.
- **Strategy**: The `app/` directory will be deployed as a Python web service. These platforms support running FastAPI applications directly using `uvicorn`.
- **Environment Variables**: The production environment will securely store essential secrets:
  - `GROQ_API_KEY`: Required for LLM integration.
  - CORS settings: Must be updated to allow requests from the deployed Vercel frontend domain.

## Large Dataset Considerations
- **Storage Limit**: The Zomato dataset (Parquet file) is ~149MB, which can exceed the limits of some free-tier ephemeral file systems or Git repositories.
- **Mitigation**:
  - The application is designed to download the dataset directly from Hugging Face on startup and cache it.
  - For deployment, the host environment must have sufficient RAM and ephemeral disk space to hold this cache in memory or on disk during runtime, avoiding the need to commit the large file to the repository.
