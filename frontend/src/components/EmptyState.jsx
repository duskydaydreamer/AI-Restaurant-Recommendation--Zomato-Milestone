import React from 'react';
import dinnerHeroImg from '../assets/dinner-hero-connected.png';

const StepItem = ({ step, icon, title, subtitle }) => (
  <div className="flex flex-col items-center text-center gap-[6px] relative z-10">
    <div className="relative">
      <div className="absolute -top-[2px] -left-[6px] w-[22px] h-[22px] bg-primary text-white rounded-full flex items-center justify-center font-bold text-[12px] border-2 border-white z-20 shadow-sm">
        {step}
      </div>
      <div className="w-[64px] h-[64px] bg-primary/5 border border-primary/10 rounded-full flex items-center justify-center text-primary overflow-hidden">
        {icon === 'location' ? (
          <span className="material-symbols-outlined text-[32px] filled text-primary">location_on</span>
        ) : icon === 'cloche' ? (
          <div className="w-[46px] h-[46px] relative flex items-center justify-center mt-[2px]">
            <svg viewBox="0 0 120 100" className="w-full h-full" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="15" y="80" width="90" height="8" rx="4" fill="#9CA3AF" />
              <ellipse cx="60" cy="80" rx="43" ry="5" fill="#D1D5DB" />
              <path d="M 23 80 C 23 45 40 40 60 40 C 80 40 97 45 97 80 Z" fill="#E5E7EB" />
              <rect x="56" y="36" width="8" height="4" fill="#D1D5DB" />
            </svg>
            <div className="absolute top-[30%] text-primary">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </div>
          </div>
        ) : (
          <span className="material-symbols-outlined text-[32px] filled text-primary">favorite</span>
        )}
      </div>
    </div>
    <div>
      <h4 className="text-on-surface font-bold text-[14px]">{title}</h4>
      <p className="text-on-surface-variant text-[11px]">{subtitle}</p>
    </div>
  </div>
);

const StepConnector = () => (
  <div className="flex-1 flex items-center justify-center opacity-15 px-2 mt-[32px] -translate-y-1/2">
    <div className="border-t-2 border-dashed border-on-surface-variant flex-1 max-w-[60px]"></div>
    <span className="material-symbols-outlined text-on-surface-variant text-[18px] mx-1 flex items-center justify-center leading-none">chevron_right</span>
    <div className="border-t-2 border-dashed border-on-surface-variant flex-1 max-w-[60px]"></div>
  </div>
);

export default function EmptyState({ onInspirationClick }) {
  return (
    <div className="flex flex-col items-center w-full max-w-[1150px] mr-auto pt-xs pb-md px-md">
      
      {/* Hero Card */}
      <div className="w-full bg-white border border-outline-variant/40 rounded-2xl px-xl md:px-[48px] py-md shadow-[0_2px_24px_-12px_rgba(0,0,0,0.1)] flex flex-row items-center justify-center gap-x-10 md:gap-x-12 overflow-hidden relative" style={{ minHeight: '268px', maxHeight: '286px' }}>
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary/[0.05] via-primary/[0.15] to-primary/[0.05]"></div>
        {/* Left: Illustration */}
        <div className="flex-shrink-0 flex items-start justify-center w-[280px] md:w-[300px] relative -mt-[30px] md:-mt-[36px]">
          <img src={dinnerHeroImg} alt="Dinner Table" className="relative z-10 w-full h-full object-contain mix-blend-multiply scale-[1.08] origin-top" />
        </div>
        
        {/* Right: Content */}
        <div className="flex flex-col justify-center max-w-[640px] text-left -mt-[14px]">
          <span className="mb-[12px] w-fit rounded-full bg-primary/[0.04] border border-primary/10 px-[10px] py-[3px] text-[11px] font-medium uppercase tracking-wider text-primary/80 shadow-sm">
            AI dining concierge
          </span>
          <h2 className="text-[32px] leading-[1.06] font-bold text-[#1A1A1A] tracking-tight mb-[18px] flex flex-col gap-[4px]">
            <span>Let's find your <span className="text-primary">perfect</span></span>
            <span>dining experience</span>
          </h2>
          <div className="text-[#5A6173] text-[15px] leading-snug flex flex-col gap-[2px]">
            <span>Share what you're craving, and DineWise will handpick</span>
            <span>restaurants tailored to your taste, budget, and mood.</span>
          </div>
        </div>
      </div>

      {/* How it works section */}
      <div className="w-full max-w-[980px] mx-auto mt-[32px]">
        <h3 className="text-on-surface font-bold text-[18px] mb-md text-left pl-md">How it works</h3>
        
        <div className="flex flex-row items-start justify-between w-full px-md">
          <StepItem 
            step="1" 
            icon="location" 
            title="Choose" 
            subtitle="Location • Budget • Cuisine" 
          />
          <StepConnector />
          <StepItem 
            step="2" 
            icon="cloche" 
            title="We curate" 
            subtitle="Personalized recommendations" 
          />
          <StepConnector />
          <StepItem 
            step="3" 
            icon="heart" 
            title="Explore" 
            subtitle="Compare • Save • Book" 
          />
        </div>
      </div>

      {/* Need inspiration section */}
      <div className="w-full max-w-[980px] mx-auto mt-[40px]">
        <h3 className="text-on-surface font-bold text-[18px] mb-md text-left pl-md">Need inspiration?</h3>
        
        <div className="flex flex-wrap gap-[22px] px-md">
          <button onClick={() => onInspirationClick('Romantic dinner')} className="flex items-center gap-[6px] px-md py-sm bg-white hover:bg-[#FFF5F6] border border-primary/20 rounded-full transition-all text-on-surface text-[14px] hover:border-primary/40 shadow-sm">
            <span className="material-symbols-outlined text-[16px] text-primary">favorite</span> Romantic dinner
          </button>
          <button onClick={() => onInspirationClick('Quiet café')} className="flex items-center gap-[6px] px-md py-sm bg-white hover:bg-[#FFF5F6] border border-primary/20 rounded-full transition-all text-on-surface text-[14px] hover:border-primary/40 shadow-sm">
            <span className="material-symbols-outlined text-[16px] text-primary">local_cafe</span> Quiet café
          </button>
          <button onClick={() => onInspirationClick('Family outing')} className="flex items-center gap-[6px] px-md py-sm bg-white hover:bg-[#FFF5F6] border border-primary/20 rounded-full transition-all text-on-surface text-[14px] hover:border-primary/40 shadow-sm">
            <span className="material-symbols-outlined text-[16px] text-primary">group</span> Family outing
          </button>
          <button onClick={() => onInspirationClick('Late-night cravings')} className="flex items-center gap-[6px] px-md py-sm bg-white hover:bg-[#FFF5F6] border border-primary/20 rounded-full transition-all text-on-surface text-[14px] hover:border-primary/40 shadow-sm">
            <span className="material-symbols-outlined text-[16px] text-primary">dark_mode</span> Late-night cravings
          </button>
          <button onClick={() => onInspirationClick('Budget-friendly')} className="flex items-center gap-[6px] px-md py-sm bg-white hover:bg-[#FFF5F6] border border-primary/20 rounded-full transition-all text-on-surface text-[14px] hover:border-primary/40 shadow-sm">
            <span className="material-symbols-outlined text-[16px] text-primary">account_balance_wallet</span> Budget-friendly
          </button>
        </div>
      </div>
    </div>
  );
}
