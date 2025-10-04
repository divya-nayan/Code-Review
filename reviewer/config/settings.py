"""
Configuration for code reviewer
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Model Configuration
MODEL_NAME = "llama-3.2-90b-text-preview"
