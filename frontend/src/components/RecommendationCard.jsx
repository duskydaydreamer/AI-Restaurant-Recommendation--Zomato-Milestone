import React, { useRef, useState } from 'react';

const SWIPE_THRESHOLD = 80;

const CardContent = ({ rec, isSaved, onToggleSave, cuisines, imageUrl, distanceStr, dragProps, swipeX, startXRef }) => (
  <article
    className="bg-surface-container-lowest border-surface-variant rounded-xl border shadow-sm flex flex-row overflow-hidden group relative min-h-[224px] select-none"
    style={{
      transform: `translateX(-${swipeX}px)`,
      transition: startXRef?.current !== null ? 'none' : 'transform 0.25s cubic-bezier(0.25,0.46,0.45,0.94)',
      cursor: dragProps ? 'grab' : 'default',
    }}
    {...dragProps}
  >
    <div className="w-[260px] flex-shrink-0 relative overflow-hidden bg-surface-variant/30">
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat transform group-hover:scale-105 transition-transform duration-700 ease-out"
        style={{ backgroundImage: `url(${imageUrl})` }}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/5 pointer-events-none" />
    </div>

    <div className="p-lg flex flex-col flex-1 min-w-0 justify-center">
      <div className="flex items-start gap-md mb-sm">
        <div className="flex-1 min-w-0">
          <h4 className="font-headline-md text-headline-md text-on-surface truncate">{rec.name}</h4>
          <p className="font-body-md text-body-md text-on-surface-variant truncate">{rec.location}</p>
        </div>
        <button
          type="button"
          onClick={onToggleSave}
          aria-label={isSaved ? `Unsave ${rec.name}` : `Save ${rec.name}`}
          className={`transition-colors p-sm rounded-full hover:bg-primary/5 -mt-sm -mr-sm flex-shrink-0 ${isSaved ? 'text-primary' : 'text-on-surface-variant hover:text-primary'}`}
        >
          <span
            className="material-symbols-outlined"
            style={{ fontVariationSettings: isSaved ? "'FILL' 1" : "'FILL' 0" }}
          >bookmark</span>
        </button>
      </div>

      <div className="flex items-center flex-wrap gap-x-sm gap-y-xs mb-md text-[13px] font-medium">
        <span className="flex items-center text-[#0B7A53]">
          <span className="material-symbols-outlined filled text-[14px] mr-[2px]">star</span>
          {rec.rating ? parseFloat(rec.rating).toFixed(1) : 'N/A'}
        </span>
        <span className="text-surface-variant text-[10px]">•</span>
        <span className="text-on-surface-variant">{rec.estimated_cost || '$$'}</span>
        {cuisines.length > 0 && (
          <>
            <span className="text-surface-variant text-[10px]">•</span>
            <span className="text-on-surface-variant truncate">{cuisines.slice(0, 3).join(', ')}</span>
          </>
        )}
        <span className="text-surface-variant text-[10px]">•</span>
        <span className="text-on-surface-variant">{distanceStr}</span>
      </div>

      <div className="bg-amber-500/5 rounded-lg px-md py-sm border border-amber-500/10 flex gap-sm items-start relative mb-md mt-md">
        <div className="absolute -top-3 left-sm bg-surface-container-lowest border border-amber-500/10 px-xs py-0.5 rounded text-[9px] font-bold text-amber-700/80 uppercase tracking-wider flex items-center gap-0.5">
          <span className="material-symbols-outlined text-[10px]">psychiatry</span> Why it fits
        </div>
        <p className="font-body-md text-body-md text-on-surface-variant text-[14px] leading-relaxed italic mt-xs line-clamp-2">
          "{rec.explanation}"
        </p>
      </div>

      <div className="mt-auto flex gap-md pt-xs">
        <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer"
          className="bg-primary text-on-primary px-md py-sm rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-colors flex-1 text-center block">
          Book Table
        </a>
        <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer"
          className="bg-white border border-primary text-primary px-md py-sm rounded-lg font-label-md hover:bg-primary/5 transition-colors flex-1 text-center block">
          View Details
        </a>
      </div>
    </div>
  </article>
);

const RecommendationCard = ({ rec, isSaved, onToggleSave, allowSwipeDelete }) => {
  const cuisines = rec.cuisine
    ? rec.cuisine.split(',').map(c => {
        const t = c.trim();
        return t.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
      }).filter(Boolean)
    : [];

  const imageUrl = rec.image_url ||
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80';

  const generateDistance = (name) => {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return `${Math.round((Math.abs(hash) % 80) / 10 + 0.5)} km away`;
  };

  const distanceStr = rec.distance
    ? `${Math.round(parseFloat(rec.distance))} km away`
    : generateDistance(rec.name || 'Unknown');

  // ── Swipe state ──────────────────────────────────────────────────────────
  const startXRef = useRef(null);
  const [swipeX, setSwipeX] = useState(0);
  const [swiped, setSwiped] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const onPointerDown = (clientX) => { startXRef.current = clientX; };

  const onPointerMove = (clientX) => {
    if (startXRef.current === null) return;
    const delta = startXRef.current - clientX;
    if (delta < 0 && !swiped) { setSwipeX(0); return; }
    const base = swiped ? SWIPE_THRESHOLD : 0;
    setSwipeX(Math.max(0, Math.min(base + delta, 130)));
  };

  const onPointerUp = () => {
    if (startXRef.current === null) return;
    startXRef.current = null;
    if (swipeX >= SWIPE_THRESHOLD) { setSwipeX(SWIPE_THRESHOLD); setSwiped(true); }
    else { setSwipeX(0); setSwiped(false); }
  };

  const handleDelete = () => {
    setDeleting(true);
    setTimeout(() => onToggleSave(), 320);
  };

  // ── Non-swipe card (Discover tab) ─────────────────────────────────────────
  if (!allowSwipeDelete) {
    return (
      <article className="bg-surface-container-lowest border-surface-variant rounded-xl border shadow-sm hover:shadow-md hover:-translate-y-0.5 hover:border-primary/30 hover:bg-primary/5 transition-all duration-300 flex flex-row overflow-hidden group relative min-h-[224px]">
        <div className="w-[260px] flex-shrink-0 relative overflow-hidden bg-surface-variant/30">
          <div className="absolute inset-0 bg-cover bg-center bg-no-repeat transform group-hover:scale-105 transition-transform duration-700 ease-out"
            style={{ backgroundImage: `url(${imageUrl})` }} />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/5 pointer-events-none" />
        </div>
        <div className="p-lg flex flex-col flex-1 min-w-0 justify-center">
          <div className="flex items-start gap-md mb-sm">
            <div className="flex-1 min-w-0">
              <h4 className="font-headline-md text-headline-md text-on-surface truncate">{rec.name}</h4>
              <p className="font-body-md text-body-md text-on-surface-variant truncate">{rec.location}</p>
            </div>
            <button type="button" onClick={onToggleSave}
              aria-label={isSaved ? `Unsave ${rec.name}` : `Save ${rec.name}`}
              className={`transition-colors p-sm rounded-full hover:bg-primary/5 -mt-sm -mr-sm flex-shrink-0 ${isSaved ? 'text-primary' : 'text-on-surface-variant hover:text-primary'}`}>
              <span className="material-symbols-outlined"
                style={{ fontVariationSettings: isSaved ? "'FILL' 1" : "'FILL' 0" }}>bookmark</span>
            </button>
          </div>
          <div className="flex items-center flex-wrap gap-x-sm gap-y-xs mb-md text-[13px] font-medium">
            <span className="flex items-center text-[#0B7A53]">
              <span className="material-symbols-outlined filled text-[14px] mr-[2px]">star</span>
              {rec.rating ? parseFloat(rec.rating).toFixed(1) : 'N/A'}
            </span>
            <span className="text-surface-variant text-[10px]">•</span>
            <span className="text-on-surface-variant">{rec.estimated_cost || '$$'}</span>
            {cuisines.length > 0 && (<><span className="text-surface-variant text-[10px]">•</span>
              <span className="text-on-surface-variant truncate">{cuisines.slice(0, 3).join(', ')}</span></>)}
            <span className="text-surface-variant text-[10px]">•</span>
            <span className="text-on-surface-variant">{distanceStr}</span>
          </div>
          <div className="bg-amber-500/5 rounded-lg px-md py-sm border border-amber-500/10 flex gap-sm items-start relative mb-md mt-md">
            <div className="absolute -top-3 left-sm bg-surface-container-lowest border border-amber-500/10 px-xs py-0.5 rounded text-[9px] font-bold text-amber-700/80 uppercase tracking-wider flex items-center gap-0.5">
              <span className="material-symbols-outlined text-[10px]">psychiatry</span> Why it fits
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant text-[14px] leading-relaxed italic mt-xs line-clamp-2">"{rec.explanation}"</p>
          </div>
          <div className="mt-auto flex gap-md pt-xs">
            <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer"
              className="bg-primary text-on-primary px-md py-sm rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-colors flex-1 text-center block">Book Table</a>
            <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer"
              className="bg-white border border-primary text-primary px-md py-sm rounded-lg font-label-md hover:bg-primary/5 transition-colors flex-1 text-center block">View Details</a>
          </div>
        </div>
      </article>
    );
  }

  // ── Swipe-to-delete card (Saved tab) ──────────────────────────────────────
  return (
    <div
      className="relative overflow-hidden rounded-xl"
      style={{
        maxHeight: deleting ? 0 : 300,
        opacity: deleting ? 0 : 1,
        marginBottom: deleting ? 0 : undefined,
        transition: 'max-height 0.35s ease, opacity 0.3s ease, margin 0.35s ease',
      }}
    >
      {/* Red action revealed on swipe */}
      <div className="absolute inset-y-0 right-0 w-[130px] flex items-center justify-center bg-red-500 rounded-r-xl">
        <button onClick={handleDelete} className="flex flex-col items-center gap-1 text-white px-4">
          <span className="material-symbols-outlined text-[26px]">delete</span>
          <span className="text-[11px] font-semibold tracking-wide">Remove</span>
        </button>
      </div>

      {/* Swipeable card */}
      <article
        className="bg-surface-container-lowest border-surface-variant rounded-xl border shadow-sm flex flex-row overflow-hidden group relative min-h-[224px] select-none"
        style={{
          transform: `translateX(-${swipeX}px)`,
          transition: startXRef.current !== null ? 'none' : 'transform 0.25s cubic-bezier(0.25,0.46,0.45,0.94)',
          cursor: 'grab',
        }}
        onTouchStart={(e) => onPointerDown(e.touches[0].clientX)}
        onTouchMove={(e) => onPointerMove(e.touches[0].clientX)}
        onTouchEnd={onPointerUp}
        onMouseDown={(e) => onPointerDown(e.clientX)}
        onMouseMove={(e) => { if (startXRef.current !== null) onPointerMove(e.clientX); }}
        onMouseUp={onPointerUp}
        onMouseLeave={onPointerUp}
      >
        <div className="w-[260px] flex-shrink-0 relative overflow-hidden bg-surface-variant/30">
          <div className="absolute inset-0 bg-cover bg-center bg-no-repeat transform group-hover:scale-105 transition-transform duration-700 ease-out"
            style={{ backgroundImage: `url(${imageUrl})` }} />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/5 pointer-events-none" />
        </div>
        <div className="p-lg flex flex-col flex-1 min-w-0 justify-center">
          <div className="flex items-start gap-md mb-sm">
            <div className="flex-1 min-w-0">
              <h4 className="font-headline-md text-headline-md text-on-surface truncate">{rec.name}</h4>
              <p className="font-body-md text-body-md text-on-surface-variant truncate">{rec.location}</p>
            </div>
            <button type="button" onClick={onToggleSave}
              aria-label="Unsave"
              className="text-primary transition-colors p-sm rounded-full hover:bg-primary/5 -mt-sm -mr-sm flex-shrink-0">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>bookmark</span>
            </button>
          </div>
          <div className="flex items-center flex-wrap gap-x-sm gap-y-xs mb-md text-[13px] font-medium">
            <span className="flex items-center text-[#0B7A53]">
              <span className="material-symbols-outlined filled text-[14px] mr-[2px]">star</span>
              {rec.rating ? parseFloat(rec.rating).toFixed(1) : 'N/A'}
            </span>
            <span className="text-surface-variant text-[10px]">•</span>
            <span className="text-on-surface-variant">{rec.estimated_cost || '$$'}</span>
            {cuisines.length > 0 && (<><span className="text-surface-variant text-[10px]">•</span>
              <span className="text-on-surface-variant truncate">{cuisines.slice(0, 3).join(', ')}</span></>)}
            <span className="text-surface-variant text-[10px]">•</span>
            <span className="text-on-surface-variant">{distanceStr}</span>
          </div>
          <div className="bg-amber-500/5 rounded-lg px-md py-sm border border-amber-500/10 flex gap-sm items-start relative mb-md mt-md">
            <div className="absolute -top-3 left-sm bg-surface-container-lowest border border-amber-500/10 px-xs py-0.5 rounded text-[9px] font-bold text-amber-700/80 uppercase tracking-wider flex items-center gap-0.5">
              <span className="material-symbols-outlined text-[10px]">psychiatry</span> Why it fits
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant text-[14px] leading-relaxed italic mt-xs line-clamp-2">"{rec.explanation}"</p>
          </div>
          <div className="mt-auto flex gap-md pt-xs">
            <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer"
              className="bg-primary text-on-primary px-md py-sm rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-colors flex-1 text-center block">Book Table</a>
            <a href={rec.url || '#'} target="_blank" rel="noopener noreferrer"
              className="bg-white border border-primary text-primary px-md py-sm rounded-lg font-label-md hover:bg-primary/5 transition-colors flex-1 text-center block">View Details</a>
          </div>
        </div>
      </article>
    </div>
  );
};

export default RecommendationCard;
