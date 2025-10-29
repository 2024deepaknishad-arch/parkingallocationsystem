# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Put your Hugging Face token in environment var HF_API_KEY or paste here (not recommended)
HF_API_KEY = os.getenv("HF_API_KEY", "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")

# Optional: IPINFO token (for nicer location). If not available, backend returns "Unknown".
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "fa841e5852c8b7")

# Parking fee rate (per minute)
RATE_PER_MINUTE = 0.5  # ₹0.5 per minute => ₹30 per hour

# Total parking slots (default)
TOTAL_SLOTS = 20