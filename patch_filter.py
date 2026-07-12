import re

with open("app/services/filter.py", "r") as f:
    content = f.read()

# Replace progressive relaxation
old_prog = """    if c_cuisine:
        candidates = c_cuisine
    else:
        # ── Progressive relaxation ──────────────────────────────────────
        # Note: Rating is a HARD constraint and is NEVER relaxed to maintain trust.
        
        # Step 1: Relax cuisine (keep location + rating + budget)
        if c_budget:
            candidates = c_budget
            if prefs.cuisine:
                relaxations.append("Cuisine requirement relaxed")
                logger.info("Relaxed cuisine filter → %d candidates", len(candidates))
        # Step 2: Relax budget (keep location + rating)
        else:
            candidates = c_rated
            if prefs.cuisine or prefs.budget:
                relaxations.append("Cuisine and Budget requirements relaxed")
            logger.info("Relaxed optional filters → %d candidates (location + rating only)", len(candidates))"""

new_prog = """    if c_cuisine:
        candidates = c_cuisine
    else:
        # ── Progressive relaxation ──────────────────────────────────────
        # Step 1: Relax cuisine
        if c_budget:
            candidates = c_budget
            if prefs.cuisine:
                relaxations.append("Cuisine requirement relaxed")
                logger.info("Relaxed cuisine filter → %d candidates", len(candidates))
        # Step 2: Relax budget
        elif c_rated:
            candidates = c_rated
            relaxations.append("Cuisine and Budget requirements relaxed")
            logger.info("Relaxed cuisine + budget → %d candidates", len(candidates))
        # Step 3: Relax rating (keep location-only)
        else:
            # candidates is still location-filtered from step 1
            relaxations.append("Cuisine, Budget, and Rating requirements relaxed")
            logger.info(
                "Relaxed all optional filters → %d candidates (location-only)",
                len(candidates),
            )"""

content = content.replace(old_prog, new_prog)

# Replace padding logic
old_pad = """    if len(candidates) < prefs.top_k:
        relaxations.append(f"Expanded search to meet requested count (within minimum rating)")
        logger.info("Padding candidates to meet top_k=%d", prefs.top_k)
        
        seen_ids = {c.id for c in candidates}
        
        # 1. First, pad with other restaurants from the SAME location that meet MIN RATING
        loc_fallback = sorted(
            [r for r in loc_candidates if r.rating >= prefs.min_rating], 
            key=lambda r: (r.rating, r.votes), 
            reverse=True
        )
        for r in loc_fallback:
            if len(candidates) >= prefs.top_k:
                break
            if r.id not in seen_ids:
                candidates.append(r)
                seen_ids.add(r.id)
                
        # 2. If STILL not enough, fallback to global top-rated restaurants that meet MIN RATING
        if len(candidates) < prefs.top_k:
            global_fallback = sorted(
                [r for r in restaurants if r.rating >= prefs.min_rating], 
                key=lambda r: (r.rating, r.votes), 
                reverse=True
            )
            for r in global_fallback:
                if len(candidates) >= prefs.top_k:
                    break
                if r.id not in seen_ids:
                    candidates.append(r)
                    seen_ids.add(r.id)"""

new_pad = """    if len(candidates) < prefs.top_k:
        relaxations.append(f"Expanded search to meet requested count")
        logger.info("Padding candidates to meet top_k=%d", prefs.top_k)
        
        seen_ids = {c.id for c in candidates}
        
        # 1. First, pad with other restaurants from the SAME location
        loc_fallback = sorted(loc_candidates, key=lambda r: (r.rating, r.votes), reverse=True)
        for r in loc_fallback:
            if len(candidates) >= prefs.top_k:
                break
            if r.id not in seen_ids:
                candidates.append(r)
                seen_ids.add(r.id)
                
        # 2. If STILL not enough, fallback to global top-rated restaurants
        if len(candidates) < prefs.top_k:
            global_fallback = sorted(restaurants, key=lambda r: (r.rating, r.votes), reverse=True)
            for r in global_fallback:
                if len(candidates) >= prefs.top_k:
                    break
                if r.id not in seen_ids:
                    candidates.append(r)
                    seen_ids.add(r.id)"""

content = content.replace(old_pad, new_pad)

with open("app/services/filter.py", "w") as f:
    f.write(content)
