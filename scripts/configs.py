import os
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPEN_ROUTER_API_KEY = os.environ.get("OPEN_ROUTER_API_KEY")
CLASSIFICATION_THRESHOLD = os.environ.get("CLASSIFICATION_THRESHOLD", 0.85)
