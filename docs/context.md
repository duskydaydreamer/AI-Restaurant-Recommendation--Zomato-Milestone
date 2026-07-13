# Product Context

DineWise is an AI-powered restaurant recommendation system designed to simplify the dining decision process.

## Target Users
- Food enthusiasts looking for specific culinary experiences.
- Planners organizing group dinners with budget and location constraints.
- Anyone suffering from decision fatigue when choosing where to eat.

## The Problem with Restaurant Discovery
While there is an abundance of restaurant data available online, discovery remains difficult. Traditional search engines and directory apps rely heavily on keywords and rigid filters. They fail to understand the nuances of a user's request (e.g., "a quiet place for a date night under ₹1500") and often return overwhelming, unfiltered lists.

## The DineWise Approach: Structured Data + LLM Reasoning
To provide high-quality recommendations, DineWise adopts a hybrid approach:
1.  **Structured Data Filtering:** We utilize a rich Zomato dataset from Hugging Face to quickly eliminate options that don't meet strict criteria (location, budget tier, minimum rating). This ensures the AI isn't hallucinating places or recommending unaffordable options.
2.  **LLM Reasoning:** The filtered candidates are sent to an advanced LLM (Groq API using LLaMA). The model analyzes the user's specific context and preferences, ranks the candidates, and generates a personalized, persuasive explanation for each choice, mimicking a knowledgeable local food critic.
