def get_market_standards(clause_type: str):
    """Dictionary of Market Standards"""
    standards = {
        "liability": "Standard: Liability is capped at 12 months fees.",
        "termination": "Standard: Mutual termination (30 days notice).",
        "ip": "Standard: Client owns 'Work Made for Hire' upon payment.",
        "non-compete": "Standard: Non-competes are rarely enforceable.",
        "auto-renewal": "Standard: Contracts expire automatically.",
        "payment": "Standard: Net-30 is industry norm.",
        "security": "Standard: Vendors must have SOC2/ISO certs.",
        "subcontracting": "Standard: Vendor requires consent to subcontract."
    }
    clause_type = clause_type.lower()
    for key in standards:
        if key in clause_type: return standards[key]
    return "No specific standard found."