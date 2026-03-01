import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SES_SENDER   = os.getenv("SES_SENDER", "")       # Verified sender email in AWS SES
EMAIL_TO     = os.getenv("EMAIL_TO", "")          # Fallback recipient (local dev / single user)
