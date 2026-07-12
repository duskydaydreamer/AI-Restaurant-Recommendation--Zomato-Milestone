"""
UI Components for Streamlit.

Handles custom CSS injection and rendering of HTML/CSS cards
to match the high-end DineWise / Zomato design language.
"""

import streamlit as st
import html as html_lib
import re
from app.models.recommendation import RecommendationItem

def inject_custom_css():
    """Inject global CSS for fonts, typography, and card styling."""
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

        /* Unified App Layout */
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #FAFAFB !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #FAFAFB !important;
            border-right: none !important;
            box-shadow: 1px 0 0 rgba(0, 0, 0, 0.03) !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            background-color: transparent !important;
        }
        
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Global Font Assignments (for markdown elements) */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
            color: #1a1c1c;
        }
        p, span, div {
            font-family: 'Inter', sans-serif;
            color: #1a1c1c;
        }

        /* Custom Card Style */
        .recommender-card {
            background-color: #ffffff;
            border: 1px solid #f3f4f6;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }
        .recommender-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(226, 55, 68, 0.08);
            border-color: #fecdd3;
        }

        /* Card Header Flexbox */
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }

        /* Rank Badge Base */
        .rank-badge {
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 14px;
            width: 28px;
            height: 28px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .rank-badge-1 { background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%); box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3); } /* Gold */
        .rank-badge-2 { background: linear-gradient(135deg, #9CA3AF 0%, #D1D5DB 100%); box-shadow: 0 4px 12px rgba(156, 163, 175, 0.3); } /* Silver */
        .rank-badge-3 { background: linear-gradient(135deg, #B45309 0%, #D97706 100%); box-shadow: 0 4px 12px rgba(180, 83, 9, 0.3); } /* Bronze */
        .rank-badge-4, .rank-badge-5 { background-color: #E23744; box-shadow: 0 4px 12px rgba(226, 55, 68, 0.3); } /* Zomato Red */

        /* Title */
        .card-title {
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            font-weight: 800;
            margin: 0 !important;
            color: #1c1c1c;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }

        /* Metadata Row (Cuisines, Cost) */
        .metadata-line {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }

        /* Cuisine Text */
        .cuisine-text {
            color: #696969;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
        }

        /* Force Primary Button Text to White */
        button[kind="primary"],
        button[kind="primary"] p,
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stFormSubmitButton"] button {
            color: #ffffff !important;
            background: linear-gradient(135deg, #E23744 0%, #b82431 100%) !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(226, 55, 68, 0.2) !important;
            transition: all 0.3s ease !important;
        }
        button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(226, 55, 68, 0.3) !important;
            background: linear-gradient(135deg, #f04754 0%, #d12c38 100%) !important;
        }

        /* Cost Text */
        .cost-text {
            color: #696969;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .dot-separator {
            color: #d1d5db;
            font-size: 12px;
        }

        /* Rating Badge (Authentic Zomato Green) */
        .rating-badge {
            color: #24963f;
            font-size: 14px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Filter Pills for Active Filters */
        .filter-pill {
            background-color: #ffffff;
            color: #4b5563;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            font-family: 'Inter', sans-serif;
        }

        /* AI Explanation Block */
        .ai-explanation {
            background-color: #f9fafb;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            font-family: 'Inter', sans-serif;
            color: #374151;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .ai-explanation-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #1c1c1c;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 14px;
        }

        .ai-explanation-header svg {
            color: #E23744;
            flex-shrink: 0;
        }

        .ai-explanation-text {
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            color: #4b5563;
        }
        
        /* Summary Box */
        .ai-summary-box {
            background: linear-gradient(135deg, #fef2f2 0%, #fff1f2 100%);
            border: 1px solid #fee2e2;
            border-left: 4px solid #E23744;
            border-radius: 12px;
            padding: 24px;
            margin-top: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(226, 55, 68, 0.05);
            position: relative;
            overflow: hidden;
        }
        .ai-summary-box::after {
            content: '';
            position: absolute;
            top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.6) 50%, rgba(255,255,255,0) 100%);
            transform: skewX(-20deg);
            animation: shine 4s infinite;
        }
        @keyframes shine {
            0% { left: -100%; }
            20% { left: 200%; }
            100% { left: 200%; }
        }
        
        .ai-summary-box h3 {
            margin-top: 0;
            color: #b7122a !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def clean_mojibake(text):
    if not isinstance(text, str): return ""
    text = html_lib.unescape(text)
    # Fix extreme dataset corruption manually
    text = re.sub(r'SantÃ.*?©', 'Santé', text)
    text = re.sub(r'CafÃ.*?©', 'Café', text)
    text = text.replace('CafÃƒÂƒÃ‚ÂƒÃƒÂ‚Ã‚ÂƒÃƒÂƒÃ‚Â‚ÃƒÂ‚Ã‚Â©', 'Café')
    text = text.replace('CafÃƒÂ©', 'Café')
    text = text.replace('CafÃ©', 'Café')
    try:
        return html_lib.escape(text.encode('latin1').decode('utf8'))
    except:
        return html_lib.escape(text)

def render_recommendation_card(rec: RecommendationItem):
    """Render a single recommendation item as a custom HTML card."""
    
    # Format cuisines nicely
    cuisines = [c.strip() for c in rec.cuisine.split(",") if c.strip()]
    cuisine_str = ", ".join(cuisines) if cuisines else "Various Cuisines"
    
    tags_html = ""
    if hasattr(rec, 'tags') and rec.tags:
        tag_spans = "".join([f'<span class="filter-pill">{html_lib.escape(tag)}</span>' for tag in rec.tags])
        tags_html = f'<div class="tags-container" style="margin-top: 16px; display: flex; gap: 8px;">{tag_spans}</div>'
    
    # Fix potential HTML entities and Mojibake errors from dataset
    safe_name = clean_mojibake(rec.name)
    safe_explanation = clean_mojibake(rec.explanation)
    
    # Visual Formatting for Ranks (Coherent Circle)
    badge_text = str(rec.rank)
    badge_class = f"rank-badge rank-badge-{rec.rank}"
    
    html = f"""
    <div class="recommender-card">
        <div class="card-header">
            <div style="display: flex; flex-direction: column; align-items: flex-start; width: 100%;">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="{badge_class}">{badge_text}</div>
                        <h2 class="card-title">{safe_name}</h2>
                    </div>
                    <div class="rating-badge">{rec.rating:.1f} <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg></div>
                </div>
                <div class="metadata-line">
                    <span class="cost-text">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px;"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/></svg>
                        {html_lib.escape(str(rec.estimated_cost))}
                    </span>
                    <span class="dot-separator">•</span>
                    <span class="cuisine-text">{html_lib.escape(cuisine_str)}</span>
                </div>
            </div>
        </div>
        <div class="ai-explanation">
            <div class="ai-explanation-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                Why it fits
            </div>
            <p class="ai-explanation-text">{safe_explanation}</p>
        </div>
        {tags_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_ai_summary(summary: str):
    """Render the summary block at the top of results."""
    html = f"""
    <div class="ai-summary-box">
        <h3 style="margin-top: 0; margin-bottom: 0px; font-size: 18px; color: #1c1c1c; display: flex; align-items: center; gap: 8px; font-family: 'Outfit', sans-serif;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E23744" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
            Here's what we found
        </h3>
        <p style="margin:0; margin-top: 4px; font-size: 15px; color: #4b5563; line-height: 1.5; font-family: 'Inter', sans-serif;">{summary}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_suggestions(suggestions: dict):
    """Render clickable suggestions when no results are found."""
    if not suggestions:
        return
        
    st.write("### Try adjusting your search")
    
    cols = st.columns(2)
    with cols[0]:
        if suggestions.get("available_cities"):
            st.write("**Nearby Cities:**")
            cities_html = "".join(f'<span class="filter-pill" style="margin-right: 8px; margin-bottom: 8px; display: inline-block;">{c}</span>' for c in suggestions["available_cities"][:10])
            st.markdown(cities_html, unsafe_allow_html=True)
            
    with cols[1]:
        if suggestions.get("popular_cuisines"):
            st.write("**Popular Cuisines:**")
            cuis_html = "".join(f'<span class="filter-pill" style="margin-right: 8px; margin-bottom: 8px; display: inline-block;">{c}</span>' for c in suggestions["popular_cuisines"][:10])
            st.markdown(cuis_html, unsafe_allow_html=True)
