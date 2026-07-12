# 🍽️ DineWise — AI-Powered Restaurant Recommendations

**DineWise** is a smart restaurant recommendation system that combines structured restaurant data from the **Zomato** dataset with an LLM (via **Groq**) to deliver personalised, human-like restaurant suggestions with detailed explanations.

## ✨ Features

- **Intelligent Filtering** — narrow results by location, cuisine, budget, and minimum rating
- **LLM-Powered Explanations** — Groq generates personalised, natural-language reasoning for every recommendation
- **Modern Dashboard** — a responsive React + Vite frontend with search, filters, and rich restaurant cards
- **Fast API Backend** — a FastAPI server that handles filtering, LLM orchestration, and serves the frontend

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Uvicorn |
| LLM | Groq API (LLaMA 3.3 70B) |
| Data | Zomato restaurant dataset (Hugging Face) |
| Testing | Pytest, HTTPX |

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### 1. Clone & enter the project

```bash
git clone <your-repo-url>
cd restaurant-recommender
```

### 2. Backend setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start the backend server
.venv/bin/uvicorn app.api:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The dashboard will open at `http://localhost:5173`.

---

## Project Structure

```
restaurant-recommender/
├── app/
│   ├── api.py                  # FastAPI REST API (main entry point)
│   ├── config.py               # Environment & configuration
│   ├── logging_config.py       # Logging setup
│   ├── main.py                 # Legacy Streamlit entry point
│   ├── models/
│   │   ├── restaurant.py       # Restaurant data model
│   │   ├── user_preferences.py # User preference schema
│   │   └── recommendation.py   # Recommendation response model
│   ├── data/
│   │   ├── loader.py           # Dataset loading
│   │   └── preprocessor.py     # Data cleaning & transformation
│   └── services/
│       ├── filter.py           # Deterministic filtering logic
│       ├── prompt_builder.py   # LLM prompt construction
│       ├── groq_client.py      # Groq API client
│       ├── image_fetcher.py    # Restaurant image lookup
│       └── recommender.py      # Recommendation orchestrator
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React application
│   │   ├── components/         # Reusable UI components
│   │   └── utils/              # Frontend utilities
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── prompts/
│   └── recommendation.txt      # LLM prompt template
├── tests/                      # Pytest test suite
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key | *(required)* |
| `GROQ_MODEL` | Model identifier | `llama-3.3-70b-versatile` |
| `GROQ_TIMEOUT` | API call timeout (seconds) | `30` |
| `GROQ_MAX_RETRIES` | Retries on transient failures | `1` |
| `DATASET_NAME` | Hugging Face dataset ID | `ManikaSaini/zomato-restaurant-recommendation` |
| `MAX_CANDIDATES` | Max candidates sent to LLM | `30` |
| `DEFAULT_TOP_K` | Default recommendations returned | `5` |
| `BUDGET_LOW_MAX` | Upper bound for "low" budget (₹) | `500` |
| `BUDGET_MEDIUM_MAX` | Upper bound for "medium" budget (₹) | `1500` |

See [.env.example](.env.example) for the full template.

---

## Architecture

**Design principle:** *Filter first, LLM second* — hard constraints (location, budget, rating) are applied deterministically; soft reasoning (ranking, personalised explanations) is handled by the LLM.

```
User Query → FastAPI → Filter Pipeline → Top Candidates → Groq LLM → Ranked Recommendations
```

---

## Dataset Note

The Zomato restaurant dataset (`app/data/zomato_data.parquet`, ~149 MB) is **not pushed to GitHub** because it exceeds the 100 MB file size limit. It is listed in `.gitignore`.

On first run, the application automatically downloads the dataset from Hugging Face and caches it locally.

---

## Running Tests

```bash
pytest
```

---

## License

This project is for educational / demonstration purposes.
