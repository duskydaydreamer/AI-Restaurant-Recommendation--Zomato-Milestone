# Technical Architecture

DineWise is built with a modern, decoupled architecture featuring a React frontend and a FastAPI backend.

## Architecture Flow

```text
User Input (React UI)
       │
       ▼
 FastAPI Backend (`app/`)
       │
       ├─► 1. Data Loader (Loads Zomato dataset from Hugging Face)
       │
       ├─► 2. Filter Layer (Applies strict constraints: location, budget, rating)
       │
       └─► 3. Prompt Builder (Constructs context from filtered candidates)
                 │
                 ▼
          Groq API (LLaMA Model)
                 │
                 ▼
 FastAPI Backend (Parses & formats LLM response)
       │
       ▼
User Interface (Displays ranked recommendations & explanations)
```

## Components

- **Frontend (`frontend/`)**: A responsive, interactive user interface built with React and Vite. It collects user preferences (location, budget, cuisine, etc.) and displays the recommendations in rich, accessible cards.
- **Backend (`app/`)**: A high-performance REST API built with FastAPI. It handles business logic, dataset management, and orchestrates the recommendation pipeline.
- **Dataset**: The system uses a comprehensive Zomato restaurant recommendation dataset sourced from Hugging Face, stored as a Parquet file for fast loading and querying.
- **Filtering Layer**: A deterministic rule engine within the backend that quickly reduces the dataset from thousands of rows to a small, highly relevant subset based on the user's strict parameters.
- **Groq LLM Layer**: The intelligent core of the application. Using the Groq API (powered by a LLaMA model), it processes the filtered candidates alongside the user's nuanced requests to produce ranked, personalized recommendations with natural language explanations.
