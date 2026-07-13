# Edge Cases and Corner Scenarios

DineWise is designed to handle various unexpected scenarios gracefully:

- **No Restaurants Found**: If the strict filters result in zero candidates (e.g., looking for a 5-star restaurant on a very low budget in an obscure location), the backend will attempt progressive relaxation of constraints or return a friendly message suggesting the user broaden their criteria.
- **Invalid Location**: If a user inputs a location not present in the Zomato dataset, the system will identify this early and return a helpful error or suggest available nearby locations.
- **Empty Dropdowns/Missing Data**: If the user submits incomplete forms, the frontend validation will catch it, or the backend will use sensible defaults.
- **Missing Ratings or Prices**: Restaurants in the dataset with `NaN` or `0` for ratings/costs are handled during the preprocessing phase to ensure they don't break the filtering logic or sort order.
- **Invalid Budget**: Budget inputs are strictly validated against defined tiers (low, medium, high) to prevent backend parsing errors.
- **Groq API Failure**: If the Groq API times out, returns a 5xx error, or hits a rate limit, the backend will catch the exception and either return a fallback deterministic recommendation (based purely on ratings) or a clear error message to the user.
- **Backend Not Running**: The React frontend is configured to display a clear "Service Unavailable" or "Connection Error" state if it cannot reach the FastAPI server.
- **Dataset Download/Cache Issue**: If the initial Hugging Face download fails (e.g., due to network issues), the app will log the error and fail gracefully rather than crashing during a user request.
- **Slow Response**: LLM generation can take a few seconds. The frontend implements loading states (spinners or skeleton loaders) to manage user expectations during the wait.
- **No Image Available**: If the dataset or external image fetcher cannot find a suitable photo for a restaurant, the UI will fall back to a styled placeholder image to maintain the design aesthetic.
