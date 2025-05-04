import os
     from dotenv import load_dotenv
     import logging
     import json
     import tempfile

     # Set up logging
     logging.basicConfig(level=logging.INFO)
     logger = logging.getLogger(__name__)

     # Load environment variables from .env file for local development
     load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'), override=True)

     # Pinecone API key
     PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

     # Google credentials
     GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
     if GOOGLE_CREDENTIALS:
         # Use environment variable (Heroku)
         GOOGLE_CREDENTIALS_INFO = json.loads(GOOGLE_CREDENTIALS)
         # For libraries requiring a file path, create a temporary file
         with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
             temp_file.write(GOOGLE_CREDENTIALS.encode('utf-8'))
             GOOGLE_CREDENTIALS_PATH = temp_file.name
     else:
         # Fallback for local development
         GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
         GOOGLE_CREDENTIALS_INFO = None
         if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
             logger.error(f"Google credentials file not found at {GOOGLE_CREDENTIALS_PATH}")
             raise ValueError(f"Google credentials file not found at {GOOGLE_CREDENTIALS_PATH}")

     # Validate required variables
     if not PINECONE_API_KEY:
         logger.error("PINECONE_API_KEY environment variable is not set")
         raise ValueError("PINECONE_API_KEY environment variable is not set")

     logger.info("Environment variables loaded successfully")