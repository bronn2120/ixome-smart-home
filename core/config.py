import os
import getpass
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path='/home/vincent/ixome/.env', override=True)

def _set_env(var: str) -> None:
    """Prompt for and set environment variable if not already set."""
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please enter {var}: ")
        logger.info(f"Set environment variable {var}")

# Set required API keys
_set_env("PINECONE_API_KEY")
_set_env("GOOGLE_CREDENTIALS_PATH")

# Export variables for use in other modules
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
GOOGLE_CREDENTIALS_PATH = os.environ["GOOGLE_CREDENTIALS_PATH"]