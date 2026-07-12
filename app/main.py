"""
Restaurant Recommendation System — Streamlit Entry Point.
"""

import os
import streamlit as st

from app.logging_config import setup_logging
from app.data.loader import load_restaurants
from app.models.user_preferences import UserPreferences
from app.services.recommender import get_recommendations
from app.ui.components import inject_custom_css, render_recommendation_card, render_ai_summary, render_suggestions
from app.config import validate_config

# ── Initialization ────────────────────────────────────────────────────────

# Initialise structured logging
setup_logging()

# Set page config
st.set_page_config(
    page_title="Zomato AI Recommendations",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom styling
inject_custom_css()

# Cache the dataset loading
@st.cache_data(show_spinner="Warming up dataset...")
def get_dataset():
    warnings = validate_config()
    for w in warnings:
        st.warning(f"Config Warning: {w}")
    return load_restaurants()

dataset = get_dataset()

# Extract unique locations (cities + neighborhoods) for the dropdown
@st.cache_data
def get_locations(dataset):
    locs = set()
    for r in dataset:
        if r.city:
            locs.add(r.city)
        if r.location:
            locs.add(r.location)
    return sorted(list(locs))

locations = get_locations(dataset)

# Extract unique cuisines for the dropdown
@st.cache_data
def get_cuisines(dataset):
    cuisines_set = set()
    for r in dataset:
        for c in r.cuisines:
            cuisines_set.add(c.strip().title())
    return sorted(list(cuisines_set))

cuisines = get_cuisines(dataset)

# Image paths from the design folder
_DESIGN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "stitch_luxedine_ai_recommendations 2",
    "zomato_ai_recommendations_home"
)
HERO_IMAGE_PATH = os.path.join(_DESIGN_DIR, "screen.png")

_LOGO_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "stitch_luxedine_ai_recommendations 2",
    "epicurean_ai_creative_logo"
)
LOGO_IMAGE_PATH = os.path.join(_LOGO_DIR, "screen.png")


# ── Sidebar (Preferences Form) ────────────────────────────────────────────

with st.sidebar:
    if os.path.exists(LOGO_IMAGE_PATH):
        import base64
        with open(LOGO_IMAGE_PATH, "rb") as f:
            b64_logo = base64.b64encode(f.read()).decode()
            
        st.markdown(
            f"""
            <h1 style='color: #1c1c1c; font-size: 22px; font-weight: 800; display: flex; align-items: center; gap: 12px; margin-bottom: 8px; margin-top: 8px; font-family: "Outfit", sans-serif;'>
                <img src="data:image/png;base64,{b64_logo}" style="width: 36px; height: 36px; border-radius: 8px; object-fit: cover;" />
                Zomato AI
            </h1>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <h1 style='color: #1c1c1c; font-size: 22px; font-weight: 800; display: flex; align-items: center; gap: 12px; margin-bottom: 8px; margin-top: 8px; font-family: "Outfit", sans-serif;'>
                <div style='background-color: #E23744; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-style: italic; font-weight: 900; font-size: 22px; padding-right: 2px;'>z</div>
                Zomato AI
            </h1>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("<h3 style='color: #4b5563; font-size: 15px; font-weight: 600; margin-bottom: 8px; margin-top: 0px;'>Tell us what you're craving</h3>", unsafe_allow_html=True)
    
    with st.form("preferences_form"):
        # Changed location to a selectbox populated from dataset locations
        location = st.selectbox(
            "📍 Location (City or Neighborhood)", 
            options=locations,
            index=locations.index("Bangalore") if "Bangalore" in locations else 0
        )
        
        budget = st.selectbox(
            "💰 Budget Tier", 
            options=["low", "medium", "high"],
            index=1,
            format_func=lambda x: "Low (Under ₹500)" if x == "low" else "Medium (₹500 - ₹1500)" if x == "medium" else "High (Over ₹1500)"
        )
        
        cuisine = st.selectbox(
            "🍲 Cuisine (Optional)", 
            options=[""] + cuisines,
            format_func=lambda x: x if x else "Any Cuisine"
        )
        
        min_rating = st.slider("⭐ Minimum Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
        
        top_k = st.number_input("✨ Number of Recommendations", min_value=1, max_value=10, value=5)
        
        additional_prefs = st.text_area(
            "💭 Additional Preferences", 
            placeholder="e.g., family-friendly, romantic ambiance, quick service, outdoor seating..."
        )
        
        submitted = st.form_submit_button("Get AI Recommendations", type="primary", use_container_width=True)


# ── Main Content Area (Results) ───────────────────────────────────────────

if not submitted:
    # Initial / Empty State
    st.markdown(
        """
        <div style="text-align: left; margin-top: 48px; margin-bottom: 32px;">
            <h1 style="font-size: 42px; font-weight: 800; background: linear-gradient(135deg, #1c1c1c 0%, #4b5563 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em; margin: 0;">
                Recommendations
            </h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if os.path.exists(HERO_IMAGE_PATH):
        import base64
        with open(HERO_IMAGE_PATH, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode()
            
        hero_html = f"""
        <div style="
            background: linear-gradient(135deg, rgba(254, 226, 226, 0.85) 0%, rgba(255, 241, 242, 0.95) 100%), url('data:image/png;base64,{b64_image}');
            background-size: cover;
            background-position: center;
            border-radius: 32px;
            padding: 80px 48px;
            text-align: left;
            box-shadow: 0 16px 40px rgba(203, 32, 45, 0.08);
            width: 100%;
        ">
            <h2 style="font-family: 'Outfit', sans-serif; font-size: 40px; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 16px; line-height: 1.1; background: linear-gradient(135deg, #E23744 0%, #881337 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Ready to discover
            </h2>
            <p style="font-size: 20px; line-height: 1.6; max-width: 640px; margin: 0; color: #000000; font-family: 'Inter', sans-serif; font-weight: 500;">
                Just set your location, budget, and cravings in the sidebar. Our engine instantly filters through thousands of restaurants to hand-pick the absolute best spot for you.
            </p>
        </div>
        """
        st.markdown(hero_html, unsafe_allow_html=True)
    else:
        st.info("Set your preferences in the sidebar and click 'Get AI Recommendations' to start!")

else:
    # Processing state
    with st.spinner("Analyzing the best options for you..."):
        # Build preferences model
        prefs = UserPreferences(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=min_rating,
            top_k=top_k,
            additional_preferences=additional_prefs
        )
        
        # Call orchestrator
        result = get_recommendations(prefs, dataset)
        
    # Handle error / zero results
    if result.response is None or not result.response.recommendations:
        st.markdown("<h2>Hmm, we couldn't find a perfect match.</h2>", unsafe_allow_html=True)
        if result.relaxations:
            st.warning("We tried relaxing some constraints, but still came up empty: " + ", ".join(result.relaxations))
        render_suggestions(result.suggestions)
        
    else:
        # Success State
        st.markdown("<h3 style='color: #1c1c1c; font-size: 18px; font-weight: 700; margin-top: 24px; margin-bottom: 16px; font-family: \"Outfit\", sans-serif;'>Active Filters</h3>", unsafe_allow_html=True)
        filters_html = f"""
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 32px;">
            <span class="filter-pill">📍 {location}</span>
            <span class="filter-pill">💰 {budget.capitalize()}</span>
            <span class="filter-pill">★ {min_rating}+ Rating</span>
            {f'<span class="filter-pill">🍲 {cuisine}</span>' if cuisine else ''}
        </div>
        """
        st.markdown(filters_html, unsafe_allow_html=True)
        
        if result.relaxations:
            st.info("💡 Note: To find the best options, we relaxed some filters: " + ", ".join(result.relaxations))
            

        # Display AI Summary
        if result.response.summary:
            render_ai_summary(result.response.summary)
            
        # Display Cards
        for rec in result.response.recommendations:
            render_recommendation_card(rec)
