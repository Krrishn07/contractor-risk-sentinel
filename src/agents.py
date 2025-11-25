import google.generativeai as genai
import os
from dotenv import load_dotenv
from src.config import MODEL_ID
from src.tools import get_market_standards

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Graceful error handling in UI, but good to check here
if not api_key: print("⚠️ WARNING: GOOGLE_API_KEY not found in env")

genai.configure(api_key=api_key)

# 1. ANALYST (Extraction - Temp 0 for consistency)
analyst_model = genai.GenerativeModel(
    MODEL_ID,
    system_instruction="You are a strict legal AI. Output ONLY JSON data.",
    generation_config={"temperature": 0.0}
)

# 2. CONSULTANT (Chat)
consultant_model = genai.GenerativeModel(
    MODEL_ID,
    tools=[get_market_standards],
    system_instruction="You are a legal consultant. Verify clauses against market standards."
)

# 3. HELPERS
negotiator_model = genai.GenerativeModel(MODEL_ID)
reporter_model = genai.GenerativeModel(MODEL_ID)