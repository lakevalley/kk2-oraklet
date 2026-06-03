import os
from dotenv import load_dotenv

load_dotenv()

# HuggingFace API-nyckel (behövs bara om du kör via API, inte lokalt)
HF_TOKEN = os.getenv("HF_TOKEN", "")

MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"