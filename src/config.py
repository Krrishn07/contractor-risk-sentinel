import os

# Model Settings
MODEL_ID = "gemini-2.5-flash"

# DETERMINISTIC SCORING RULES
RISK_CONFIG = {
    "LIABILITY": {"label": "Unlimited Liability", "risk_level": "HIGH", "penalty": 25, "icon": "💸"},
    "TERMINATION": {"label": "Asymmetric Termination", "risk_level": "HIGH", "penalty": 25, "icon": "🛑"},
    "IP": {"label": "IP Overreach", "risk_level": "HIGH", "penalty": 15, "icon": "🧠"},
    "NON_COMPETE": {"label": "Non-Compete (>1 yr)", "risk_level": "MEDIUM", "penalty": 10, "icon": "🔗"},
    "PAYMENT": {"label": "Bad Payment Terms (>Net-45)", "risk_level": "MEDIUM", "penalty": 10, "icon": "🐌"},
    "AUTO_RENEWAL": {"label": "Predatory Auto-Renewal", "risk_level": "MEDIUM", "penalty": 10, "icon": "🔄"},
    "SECURITY": {"label": "Missing Security Clauses", "risk_level": "HIGH", "penalty": 20, "icon": "🔓"},
    "SUBCONTRACTING": {"label": "Unrestricted Subcontracting", "risk_level": "MEDIUM", "penalty": 10, "icon": "🏗️"}
}