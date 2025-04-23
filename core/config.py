import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path='/home/vincent/ixome/.env', override=True)

# Get environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "/app/credentials.json")

# Validate required variables
if not PINECONE_API_KEY:
    logger.error("PINECONE_API_KEY environment variable is not set")
    raise ValueError("PINECONE_API_KEY environment variable is not set")
if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
    logger.error(f"Google credentials file not found at {GOOGLE_CREDENTIALS_PATH}")
    raise ValueError(f"Google credentials file not found at {GOOGLE_CREDENTIALS_PATH}")

logger.info("Environment variables loaded successfully")