# 🍽️ AI-Powered Restaurant Recommendation System

An AI-powered restaurant recommendation service inspired by **Zomato**. The system combines structured restaurant data from Hugging Face with an LLM (via **Groq**) to deliver personalised, human-like restaurant suggestions.

---

## Quick Start

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com)

### 1. Clone & enter the project

```bash
cd restaurant-recommender
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 5. Run the application

```bash
streamlit run app/main.py
```

The app will open at `http://localhost:8501`.

---

## Project Structure

```
restaurant-recommender/
├── app/
│   ├── main.py                 # Streamlit entry point
│   ├── config.py               # Environment & configuration
│   ├── models/                 # Pydantic data models
│   │   ├── restaurant.py
│   │   ├── user_preferences.py
│   │   └── recommendation.py
│   ├── data/                   # Dataset loading & preprocessing
│   │   ├── loader.py
│   │   └── preprocessor.py
│   ├── services/               # Business logic
│   │   ├── filter.py
│   │   ├── prompt_builder.py
│   │   ├── groq_client.py
│   │   └── recommender.py
│   └── ui/                     # Streamlit UI components
│       └── components.py
├── prompts/
│   └── recommendation.txt      # LLM prompt template
├── tests/                      # Pytest test suite
├── docs/                       # Architecture & design docs
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
| `DATASET_NAME` | Hugging Face dataset ID | `ManikaSaini/zomato-restaurant-recommendation` |
| `MAX_CANDIDATES` | Max candidates sent to LLM | `30` |
| `DEFAULT_TOP_K` | Default recommendations count | `5` |
| `BUDGET_LOW_MAX` | Upper bound for "low" budget tier (₹) | `500` |
| `BUDGET_MEDIUM_MAX` | Upper bound for "medium" budget tier (₹) | `1500` |

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full technical design.

**Design principle:** Filter first, LLM second — hard constraints (location, budget, rating) are deterministic; soft reasoning (ranking, explanations) is LLM-driven.

---

## Running Tests

```bash
pytest
```

---

## License

This project is for educational / demonstration purposes.
