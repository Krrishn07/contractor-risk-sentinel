from src.config import RISK_CONFIG

def calculate_health_score(risks):
    """
    Deterministic scoring logic.
    Input: List of raw risk objects from AI.
    Output: Score (int), Enriched Risks (list), Counts (tuple).
    """
    health_score = 100
    high_count = 0
    med_count = 0
    enriched_risks = []
    
    for r in risks:
        raw_id = r.get("risk_id", "").upper().strip()
        
        # Robust Matching: 
        # 1. Direct match
        # 2. Key contained in ID (e.g. "LIABILITY_RISK" -> "LIABILITY")
        matched_key = None
        
        if raw_id in RISK_CONFIG:
            matched_key = raw_id
        else:
            for config_key in RISK_CONFIG:
                if config_key in raw_id:
                    matched_key = config_key
                    break
        
        if matched_key:
            config = RISK_CONFIG[matched_key]
            health_score -= config["penalty"]
            
            if config["risk_level"] == "HIGH": 
                high_count += 1
            else: 
                med_count += 1
                
            enriched_risks.append({
                "label": config["label"],
                "level": config["risk_level"],
                "icon": config["icon"],
                "explanation": r["explanation"],
                "exact_text": r["exact_text"]
            })
            
    health_score = max(0, health_score)
    return health_score, enriched_risks, high_count, med_count