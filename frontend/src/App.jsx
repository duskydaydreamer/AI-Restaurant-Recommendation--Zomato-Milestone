import React, { useState, useEffect, useRef } from 'react';
import RecommendationCard from './components/RecommendationCard';
import EmptyState from './components/EmptyState';
import logoPath from './assets/logo.png';

const ClocheIllustration = () => (
  <div className="relative w-24 h-24 flex-shrink-0 flex items-center justify-center">
    <svg viewBox="0 0 120 100" className="w-full h-full" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Sparkles */}
      <path d="M 20 40 Q 25 40 25 35 Q 25 40 30 40 Q 25 40 25 45 Q 25 40 20 40 Z" fill="#FDBA74" />
      <path d="M 15 25 Q 18 25 18 22 Q 18 25 21 25 Q 18 25 18 28 Q 18 25 15 25 Z" fill="#FED7AA" />
      <path d="M 90 25 Q 95 25 95 20 Q 95 25 100 25 Q 95 25 95 30 Q 95 25 90 25 Z" fill="#FDBA74" />
      <path d="M 100 40 Q 103 40 103 37 Q 103 40 106 40 Q 103 40 103 43 Q 103 40 100 40 Z" fill="#FED7AA" />

      {/* Dome Base Plate */}
      <rect x="15" y="80" width="90" height="8" rx="4" fill="#9CA3AF" />
      <ellipse cx="60" cy="80" rx="43" ry="5" fill="#D1D5DB" />
      
      {/* Dome Cover */}
      <path d="M 23 80 C 23 45 40 40 60 40 C 80 40 97 45 97 80 Z" fill="#E5E7EB" />
      
      {/* Dome handle base */}
      <rect x="56" y="36" width="8" height="4" fill="#D1D5DB" />
      
      {/* Shine/Reflection */}
      <path d="M 33 70 C 31 55 40 48 50 45" stroke="#FFFFFF" strokeWidth="4" strokeLinecap="round" fill="none" opacity="0.8" />
    </svg>
    {/* Heart Handle */}
    <div className="absolute top-[28px] text-primary">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
    </div>
  </div>
);

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function App() {
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedBudget, setSelectedBudget] = useState('medium');
  const [selectedCuisines, setSelectedCuisines] = useState([]);
  

  const [minRating, setMinRating] = useState(4.5);
  const [extraPrefs, setExtraPrefs] = useState('');
  const [topK, setTopK] = useState(5);
  
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('Discover');
  const [results, setResults] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [showCuisinePopover, setShowCuisinePopover] = useState(false);
  const [savedRestaurants, setSavedRestaurants] = useState([]);
  const cuisineRef = useRef(null);

  const handleToggleSave = (rec) => {
    setSavedRestaurants(prev => {
      const isSaved = prev.some(r => r.restaurant_id === rec.restaurant_id);
      return isSaved 
        ? prev.filter(r => r.restaurant_id !== rec.restaurant_id)
        : [...prev, rec];
    });
  };

  const budgetLabels = {
    low: 'Under ₹500',
    medium: '₹500 - ₹1500',
    high: '₹1500+'
  };

  // Close popover when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (cuisineRef.current && !cuisineRef.current.contains(e.target)) {
        setShowCuisinePopover(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/locations`).then(r => r.json()),
      fetch(`${API_BASE}/cuisines`).then(r => r.json())
    ]).then(([locData, cuiData]) => {
      setLocations(locData.locations || []);
      if (locData.locations?.length > 0) setSelectedLocation(locData.locations[0]);
      const apiCuisines = cuiData.cuisines || [];
      const defaultVibes = ["Romantic", "Casual", "Fine Dining", "Outdoor Seating", "Live Music", "Family Friendly", "Late Night", "Cozy"];
      setCuisines([...new Set([...defaultVibes, ...apiCuisines])]);
    }).catch(err => console.error("Failed to load filter options", err));
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setHasSearched(true);
    
    try {
      const response = await fetch(`${API_BASE}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: selectedLocation,
          budget: selectedBudget,
          cuisine: selectedCuisines.join(', '),
          min_rating: parseFloat(minRating),
          additional_preferences: extraPrefs,
          top_k: parseInt(topK, 10)
        })
      });
      
      if (!response.ok) throw new Error('API Error');
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      setResults({ summary: "Failed to fetch recommendations. Please try again.", recommendations: [] });
    } finally {
      setLoading(false);
    }
  };

  const toggleCuisine = (cuisine) => {
    setSelectedCuisines(prev => 
      prev.includes(cuisine) ? prev.filter(c => c !== cuisine) : [...prev, cuisine]
    );
  };

  const handleLogoClick = () => {
    setActiveTab('Discover');
    setHasSearched(false);
    setResults(null);
  };

  return (
    <div className="bg-background text-on-surface font-body-md h-screen overflow-hidden flex flex-col antialiased selection:bg-primary-container selection:text-on-primary-container">
      {/* Top Navigation */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-lg h-20 max-w-container-max mx-auto bg-surface/80 backdrop-blur-xl border-b border-outline-variant/30 shadow-sm transition-all duration-200">
        <div className="flex items-center cursor-pointer select-none" onClick={handleLogoClick}>
          <img src={logoPath} alt="DineWise" className="h-[37px] w-[37px] object-contain self-center" />
          <span className="text-[22px] font-black text-on-surface tracking-tight leading-none">DineWise</span>
        </div>
        <nav className="hidden md:flex items-center gap-md">
          {['Discover', 'Saved', 'Reservations', 'History'].map(tab => (
            <a 
              key={tab}
              onClick={(e) => { e.preventDefault(); setActiveTab(tab); }}
              className={`font-semibold transition-all duration-200 px-md py-sm cursor-pointer active:scale-95 ${
                activeTab === tab 
                  ? 'text-primary font-bold border-b-2 border-primary' 
                  : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-low rounded-lg'
              }`}
              href="#"
            >
              {tab}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-sm">
          <button
            type="button"
            aria-label="Notifications"
            className="h-10 w-10 flex items-center justify-center text-on-surface-variant hover:text-primary transition-colors rounded-full hover:bg-surface-container-low"
          >
            <span className="material-symbols-outlined text-[22px]">notifications</span>
          </button>
          <button
            type="button"
            aria-label="Profile"
            className="h-10 w-10 rounded-full bg-surface-container-highest border border-outline-variant/30 cursor-pointer hover:ring-2 hover:ring-primary transition-all flex items-center justify-center"
          >
            <span className="material-symbols-outlined text-[22px] text-gray-500">person</span>
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 pt-20 h-full w-full max-w-container-max mx-auto bg-background">
        {activeTab === 'Discover' ? (
          <>
            {/* Left Sidebar */}
        <aside className="w-[380px] h-full bg-surface-container-lowest border-r border-outline-variant/20 shadow-sm flex flex-col z-40 relative">
          <div className="p-lg flex flex-col gap-md flex-1 overflow-y-auto no-scrollbar pb-lg">
            {/* Form Elements */}
            <div className="flex flex-col gap-md">
              {/* Location */}
              <div className="space-y-xs">
                <label className="font-label-md text-label-md text-on-surface flex items-center gap-xs"><span className="material-symbols-outlined text-[16px] text-primary">location_on</span> Location</label>
                <div className="relative">
                  <select 
                    className="w-full pl-md pr-[36px] py-sm bg-surface rounded-lg border border-surface-variant hover:border-primary/50 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-sm font-body-md text-body-md appearance-none"
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                  >
                    {locations.map(loc => (
                      <option key={loc} value={loc}>{loc}</option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-0 pr-sm flex items-center pointer-events-none text-on-surface-variant">
                    <span className="material-symbols-outlined text-[20px]">expand_more</span>
                  </div>
                </div>
              </div>

              {/* Budget */}
              <div className="space-y-xs">
                <label className="font-label-md text-label-md text-on-surface flex items-center gap-xs"><span className="material-symbols-outlined text-[16px] text-primary">payments</span> Budget</label>
                <div className="relative">
                  <select 
                    className="w-full pl-md pr-[36px] py-sm bg-surface rounded-lg border border-surface-variant hover:border-primary/50 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-sm font-body-md text-body-md appearance-none"
                    value={selectedBudget}
                    onChange={(e) => setSelectedBudget(e.target.value)}
                  >
                    <option value="low">Normal (Under ₹500)</option>
                    <option value="medium">Medium (₹500 - ₹1500)</option>
                    <option value="high">High (₹1500+)</option>
                  </select>
                  <div className="absolute inset-y-0 right-0 pr-sm flex items-center pointer-events-none text-on-surface-variant">
                    <span className="material-symbols-outlined text-[20px]">expand_more</span>
                  </div>
                </div>
              </div>

              {/* Cuisines & Vibes */}
              <div className="space-y-xs relative" ref={cuisineRef}>
                <label className="font-label-md text-label-md text-on-surface flex items-center gap-xs"><span className="material-symbols-outlined text-[16px] text-primary">restaurant_menu</span> Cuisine & Vibe (Optional)</label>
                <div className="flex flex-wrap gap-sm">
                  {selectedCuisines.map(c => (
                    <button key={c} onClick={() => toggleCuisine(c)} className="px-sm py-xs rounded-full bg-primary/10 text-primary border border-primary/20 font-label-md text-label-md transition-colors hover:bg-primary/20 flex items-center gap-xs">
                      {c} <span className="material-symbols-outlined text-[14px]">close</span>
                    </button>
                  ))}
                  
                  <button type="button" onClick={() => setShowCuisinePopover(!showCuisinePopover)} className="px-sm py-xs rounded-full bg-surface text-primary border border-primary/30 font-label-md text-label-md transition-colors hover:bg-primary/5 flex items-center gap-xs shadow-sm">
                    <span className="material-symbols-outlined text-[14px]">add</span> Add
                  </button>
                </div>
                
                {showCuisinePopover && (
                  <div className="absolute top-full mt-sm left-0 w-full bg-surface-container-lowest border border-surface-variant rounded-xl shadow-xl z-10 flex flex-col max-h-[280px] overflow-hidden">
                    {/* Sticky header — never scrolls, never clashes */}
                    <div className="flex items-center justify-between px-sm py-xs border-b border-surface-variant bg-surface-container-low/50 shrink-0">
                      <span className="font-label-md text-label-md text-on-surface-variant flex items-center gap-xs">
                        <span className="material-symbols-outlined text-[16px]">tune</span>
                        {selectedCuisines.length > 0 
                          ? `${selectedCuisines.length} selected` 
                          : 'Select options'}
                      </span>
                      <button
                        type="button"
                        aria-label="Close cuisine selector"
                        onClick={() => setShowCuisinePopover(false)} 
                        className="text-on-surface-variant hover:text-primary transition-colors p-xs rounded-full hover:bg-surface-container"
                      >
                        <span className="material-symbols-outlined text-[18px]">close</span>
                      </button>
                    </div>
                    {/* Scrollable body */}
                    <div className="overflow-y-auto p-sm flex-1">
                      <div className="grid grid-cols-2 gap-xs">
                        {cuisines.map(c => (
                          <label key={c} className="flex items-center gap-xs text-body-md text-on-surface cursor-pointer hover:bg-surface-container-low px-sm py-xs rounded-lg transition-colors">
                            <input 
                              type="checkbox" 
                              className="rounded border-surface-variant text-primary focus:ring-primary shrink-0"
                              checked={selectedCuisines.includes(c)}
                              onChange={() => toggleCuisine(c)}
                            /> 
                            <span className="truncate">{c}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

              </div>

              {/* Rating */}
              <div className="space-y-xs">
                <div className="flex justify-between items-center mb-xs">
                  <label className="font-label-md text-label-md text-on-surface flex items-center gap-xs"><span className="material-symbols-outlined text-[16px] text-primary">star_rate</span> Minimum Rating</label>
                  <span className="font-label-md text-label-md text-primary flex items-center gap-xs">
                    {parseFloat(minRating).toFixed(1)}+
                  </span>
                </div>
                <div className="relative pt-xs pb-sm">
                  <input 
                    type="range" 
                    className="custom-slider" 
                    min="1" max="5" step="0.1" 
                    value={minRating}
                    onChange={e => setMinRating(e.target.value)}
                  />
                  <div className="flex justify-between text-[10px] text-on-surface-variant/70 px-sm mt-xs font-medium">
                    <span>1</span>
                    <span>5</span>
                  </div>
                </div>
              </div>

              {/* Number of Recommendations */}
              <div className="space-y-xs">
                <label className="font-label-md text-label-md text-on-surface flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px] text-primary">auto_awesome</span> 
                  Number of Recommendations
                </label>
                <div className="flex items-center justify-between bg-surface-container-low rounded-xl p-xs border border-surface-variant/60 w-full shadow-inner">
                  <button 
                    onClick={() => setTopK(Math.max(1, topK - 1))} 
                    className="h-10 w-12 flex items-center justify-center rounded-lg text-on-surface-variant hover:bg-surface hover:shadow hover:text-primary transition-all"
                  >
                    <span className="material-symbols-outlined text-[20px]">remove</span>
                  </button>
                    <span className="font-body-lg text-body-lg text-on-surface font-medium">
                    {topK}
                  </span>
                  <button 
                    onClick={() => setTopK(Math.min(10, topK + 1))} 
                    className="h-10 w-12 flex items-center justify-center rounded-lg text-on-surface-variant hover:bg-surface hover:shadow hover:text-primary transition-all"
                  >
                    <span className="material-symbols-outlined text-[20px]">add</span>
                  </button>
                </div>
              </div>

              {/* Prefs */}
              <div className="space-y-xs">
                <label className="font-label-md text-label-md text-on-surface">Additional Preferences</label>
                <textarea 
                  className="w-full p-sm bg-surface rounded-lg border border-surface-variant hover:border-primary/50 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-sm font-body-md text-body-md resize-none" 
                  placeholder="e.g., Quiet atmosphere, outdoor seating..." 
                  rows="2"
                  value={extraPrefs}
                  onChange={e => setExtraPrefs(e.target.value)}
                ></textarea>
              </div>
            </div>
            
            <div className="mt-auto pt-sm">
              <div className="mb-sm flex flex-wrap gap-xs text-[11px] text-on-surface-variant">
                <span className="rounded-full bg-surface-container px-sm py-xs">{selectedLocation || 'Select location'}</span>
                <span className="rounded-full bg-surface-container px-sm py-xs">{budgetLabels[selectedBudget]}</span>
                <span className="rounded-full bg-surface-container px-sm py-xs">{parseFloat(minRating).toFixed(1)}+ rating</span>
              </div>
              <button 
                onClick={handleSearch}
                disabled={loading}
                className="glow-button w-full bg-primary hover:bg-[#c92e3a] text-on-primary font-label-md text-label-md py-md rounded-lg shadow-md hover:shadow-lg transition-all active:scale-[0.98] flex justify-center items-center gap-sm overflow-hidden disabled:opacity-70 disabled:active:scale-100"
              >
                <span className="material-symbols-outlined">{loading ? 'sync' : 'auto_awesome'}</span>
                {loading ? 'Analyzing...' : 'Get AI Recommendations'}
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 h-full bg-background overflow-y-auto no-scrollbar relative p-lg md:p-xl space-y-xl">
          <div className="max-w-[1180px] mx-auto grid grid-cols-12 gap-xl">
            <div className="col-span-12 space-y-xl">
              
              {!hasSearched && !loading ? (
                <EmptyState onInspirationClick={(text) => {
                  setExtraPrefs(prev => prev ? `${prev}, ${text}` : text);
                }} />
              ) : null}

              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <span className="material-symbols-outlined text-[48px] text-primary animate-spin">sync</span>
                </div>
              ) : null}

              {!loading && results ? (
                results.recommendations?.length === 0 ? (
                  <div className="bg-surface-container-lowest border border-primary/10 rounded-xl px-xl py-lg shadow-sm text-center flex flex-col items-center py-20 mt-xl">
                    <span className="material-symbols-outlined text-[64px] text-surface-variant mb-md">search_off</span>
                    <h3 className="font-headline-md text-headline-md text-on-surface font-bold mb-sm">No spots found</h3>
                    <p className="font-body-md text-on-surface-variant max-w-[400px]">{results.summary || "We couldn't find any restaurants that fit your exact location and budget. Try relaxing them!"}</p>
                  </div>
                ) : (
                <div className="space-y-xl flex flex-col">
                  {/* AI Summary Block */}
                  <div className="bg-surface-container-lowest border border-primary/10 border-l-4 border-l-primary rounded-xl px-xl py-lg shadow-sm flex flex-row items-center gap-xl mb-sm">
                    <ClocheIllustration />
                    <div className="flex flex-col gap-md max-w-[860px]">
                      <div>
                        <p className="font-label-md text-label-md text-primary uppercase tracking-wide mb-xs">Curated shortlist</p>
                        <h3 className="font-headline-md text-headline-md text-on-surface font-medium m-0 leading-tight">
                          I've handpicked {Math.min(results.recommendations?.length || 0, topK)} great spots for you in <span className="capitalize">{selectedLocation || 'your area'}</span>
                        </h3>
                      </div>
                      <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed m-0">
                        {results.summary}
                      </p>
                      <div className="flex flex-wrap gap-xs">
                        <span className="rounded-full bg-primary/10 px-sm py-xs text-[12px] font-semibold text-primary">{budgetLabels[selectedBudget]}</span>
                        <span className="rounded-full bg-surface-container px-sm py-xs text-[12px] font-semibold text-on-surface-variant">{parseFloat(minRating).toFixed(1)}+ rating</span>
                        <span className="rounded-full bg-surface-container px-sm py-xs text-[12px] font-semibold text-on-surface-variant">{Math.min(results.recommendations?.length || 0, topK)} picks</span>
                        {selectedCuisines.slice(0, 3).map(cuisine => (
                          <span key={cuisine} className="rounded-full bg-surface-container px-sm py-xs text-[12px] font-semibold text-on-surface-variant">{cuisine}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  {/* Results List */}
                  <div className="space-y-xl">
                    {results.recommendations?.slice(0, topK).map(rec => (
                      <RecommendationCard 
                        key={rec.restaurant_id} 
                        rec={rec} 
                        isSaved={savedRestaurants.some(r => r.restaurant_id === rec.restaurant_id)}
                        onToggleSave={() => handleToggleSave(rec)}
                      />
                    ))}
                  </div>
                </div>
                )
              ) : null}

            </div>
          </div>
        </main>
          </>
        ) : activeTab === 'Saved' && savedRestaurants.length > 0 ? (
          <div className="flex-1 flex flex-col pt-xs pb-md px-md overflow-y-auto">
            <div className="max-w-[1150px] mx-auto w-full">
              <h2 className="text-[32px] font-bold text-on-surface mb-lg tracking-tight">Saved Restaurants</h2>
              <div className="space-y-xl">
                {savedRestaurants.map(rec => (
                  <RecommendationCard 
                    key={rec.restaurant_id} 
                    rec={rec} 
                    isSaved={true}
                    onToggleSave={() => handleToggleSave(rec)}
                    allowSwipeDelete={true}
                  />
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-xl">
            <span className="material-symbols-outlined text-[80px] text-surface-variant/50 mb-lg">
              {activeTab === 'Saved' ? 'bookmark' : activeTab === 'Reservations' ? 'calendar_month' : 'history'}
            </span>
            <h2 className="text-headline-md font-bold text-on-surface mb-sm">
              {activeTab === 'Saved' ? 'Saved Restaurants' : activeTab === 'Reservations' ? 'Upcoming Reservations' : 'Search History'}
            </h2>
            <p className="text-on-surface-variant font-body-md max-w-[400px]">
              {activeTab === 'Saved' 
                ? 'You haven\'t saved any restaurants yet. Click the bookmark icon on any recommendation to save it here.' 
                : activeTab === 'Reservations' 
                  ? 'You have no upcoming reservations. Find a great spot in Discover and book a table!' 
                  : 'Your search history is empty. Start exploring restaurants in Discover!'}
            </p>
            <button 
              onClick={() => setActiveTab('Discover')}
              className="mt-xl bg-primary text-on-primary px-lg py-md rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-all hover:-translate-y-[1px]"
            >
              Explore Discover
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
