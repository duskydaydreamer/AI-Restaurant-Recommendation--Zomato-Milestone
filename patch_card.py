with open("frontend/src/components/RecommendationCard.jsx", "r") as f:
    content = f.read()

old_card = """  return (
    <article className="bg-white rounded-[16px] border border-surface-variant shadow-sm hover:shadow-md hover:-translate-y-1 hover:border-primary/30 transition-all duration-300 flex flex-col sm:flex-row group relative">
      
      {/* Hyperrealistic Image Side */}
      <div className="sm:w-[260px] md:w-[280px] h-[210px] md:h-[230px] flex-shrink-0 relative overflow-hidden sm:rounded-l-[16px] rounded-t-[16px] sm:rounded-tr-none bg-surface-variant/30">
        <img 
          src={imageUrl} 
          alt={`${rec.name} interior`} 
          className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/5 pointer-events-none"></div>
      </div>

      <div className="p-[24px] flex flex-col flex-1 min-w-0 justify-center">
        <div className="flex items-start justify-between gap-4 mb-1">
          <div className="flex-1 min-w-0">
            <h4 className="font-bold text-[20px] text-on-surface truncate">{rec.name}</h4>
          </div>
          <button className="text-on-surface-variant hover:text-primary transition-colors p-2 rounded-full hover:bg-primary/5 -mt-2 -mr-2 flex-shrink-0">
            <span className="material-symbols-outlined">bookmark_border</span>
          </button>
        </div>

        <div className="flex items-center flex-wrap gap-x-2 gap-y-1 mb-4 text-[13px] text-on-surface-variant font-medium">
          <span className="flex items-center text-primary font-bold">
            <span className="text-[14px] mr-1">★</span> 
            {rec.rating ? parseFloat(rec.rating).toFixed(1) : 'N/A'}
          </span>
          <span className="text-surface-variant text-[10px]">•</span>
          <span>
            {rec.estimated_cost || '$$'}
          </span>
          {cuisines.length > 0 && (
            <>
              <span className="text-surface-variant text-[10px]">•</span>
              <span className="truncate max-w-[200px]">
                {cuisines.slice(0, 3).join(' • ')}
              </span>
            </>
          )}
          <span className="text-surface-variant text-[10px]">•</span>
          <span>
            {distanceStr}
          </span>
        </div>

        <div className="bg-[#fef2f2] rounded-[12px] p-[12px] px-[14px] border border-[#fecaca] mb-4">
          <div className="text-[12px] font-bold text-primary mb-1 flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">psychiatry</span> Why it fits
          </div>
          <p className="text-on-surface-variant text-[14px] line-clamp-2">
            {rec.explanation ? rec.explanation.replace(/^"|"$/g, '') : ''}
          </p>
        </div>

        <div className="mt-auto flex gap-[12px] flex-wrap">
          <button className="bg-primary text-white h-[44px] px-6 rounded-lg font-medium shadow-sm hover:bg-[#c92e3a] transition-colors">Book Table</button>
          <button className="bg-white border border-primary text-primary h-[44px] px-6 rounded-lg font-medium hover:bg-primary/5 transition-colors">View Details</button>
        </div>
      </div>
    </article>
  );"""

new_card = """  return (
    <article className="bg-surface-container-lowest border-surface-variant rounded-xl border shadow-sm hover:shadow-md hover:-translate-y-1 hover:bg-primary/5 hover:border-primary/30 transition-all duration-300 flex flex-row overflow-hidden group relative min-h-[220px]">
      
      {/* Hyperrealistic Image Side */}
      <div className="w-1/3 sm:w-48 md:w-64 flex-shrink-0 relative overflow-hidden bg-surface-variant/30">
        <img 
          src={imageUrl} 
          alt={`${rec.name} interior`} 
          className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent to-black/5 pointer-events-none"></div>
      </div>

      <div className="p-lg flex flex-col flex-1 min-w-0 justify-center">
        <div className="flex items-center gap-md mb-xs">
          
          <div className="flex-1 min-w-0">
            <h4 className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface truncate">{rec.name}</h4>
            <p className="font-body-md text-body-md text-on-surface-variant mt-xs truncate">
              {rec.location}
            </p>
          </div>
          <button className="text-on-surface-variant hover:text-primary transition-colors p-sm rounded-full hover:bg-primary/5 -mt-sm -mr-sm flex-shrink-0">
            <span className="material-symbols-outlined">bookmark_border</span>
          </button>
        </div>

        <div className="flex items-center flex-wrap gap-x-sm gap-y-xs mt-xs mb-md text-[13px] font-medium">
          <span className="flex items-center text-primary">
            <span className="material-symbols-outlined filled text-[14px] mr-[2px]">star</span> 
            {rec.rating ? parseFloat(rec.rating).toFixed(1) : 'N/A'}
          </span>
          <span className="text-surface-variant text-[10px]">•</span>
          <span className="text-on-surface-variant">
            {rec.estimated_cost || '$$'}
          </span>
          {cuisines.length > 0 && (
            <>
              <span className="text-surface-variant text-[10px]">•</span>
              <span className="text-on-surface-variant truncate">
                {cuisines.slice(0, 3).join(', ')}
              </span>
            </>
          )}
          <span className="text-surface-variant text-[10px]">•</span>
          <span className="text-on-surface-variant">
            {distanceStr}
          </span>
        </div>

        <div className="bg-primary/5 rounded-lg p-sm border border-primary/10 flex gap-sm items-start relative mb-md mt-md">
          <div className="absolute -top-3 left-sm bg-surface-container-lowest border border-primary/20 px-xs py-0.5 rounded text-[9px] font-bold text-primary uppercase tracking-wider flex items-center gap-0.5">
            <span className="material-symbols-outlined text-[10px]">psychiatry</span> Why it fits
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant text-[14px] leading-relaxed italic mt-xs line-clamp-2">
            "{rec.explanation}"
          </p>
        </div>

        <div className="mt-auto flex gap-sm pt-sm">
          <button className="bg-primary text-on-primary px-md py-sm rounded-lg font-label-md shadow-sm hover:bg-[#c92e3a] transition-colors flex-1 text-center">Book Table</button>
          <button className="bg-white border border-primary text-primary px-md py-sm rounded-lg font-label-md hover:bg-primary/5 transition-colors flex-1 text-center">View Details</button>
        </div>
      </div>
    </article>
  );"""

content = content.replace(old_card, new_card)

with open("frontend/src/components/RecommendationCard.jsx", "w") as f:
    f.write(content)
