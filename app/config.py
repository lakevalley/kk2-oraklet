import os
from dotenv import load_dotenv

load_dotenv()

MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "200"))

# HuggingFace API-nyckel (behövs bara om du kör via API, inte lokalt)
HF_TOKEN = os.getenv("HF_TOKEN", "")

MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"