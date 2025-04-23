import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.chat_agent import ChatAgent
import logging
from asgiref.wsgi import WsgiToAsgi

# Debug: Confirm script is running
print("Starting flask_app.py execution")

# Initialize Flask app
print("Initializing Flask app")
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests, e.g., from WordPress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("Logging configured")

# Initialize ChatAgent instance
print("Initializing ChatAgent")
try:
    agent = ChatAgent()
    logger.info("ChatAgent initialized successfully")
    print("ChatAgent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ChatAgent: {str(e)}")
    print(f"Failed to initialize ChatAgent: {str(e)}")
    raise

# Define the /process route
@app.route('/process', methods=['POST'])
async def process():
    """
    Process incoming POST requests with input_type and input_data.
    Returns a JSON response with the result from ChatAgent or an error message.
    """
    try:
        # Get JSON data from request
        data = request.json
        logger.info(f"Received request data: {data}")
        print(f"Received request data: {data}")
        
        # Validate input data
        if not data or 'input_type' not in data or 'input_data' not in data:
            logger.warning("Invalid input data received")
            print("Invalid input data received")
            return jsonify({'error': 'Invalid input data'}), 400
        
        # Process input using ChatAgent
        result = await agent.process_input(data['input_type'], data['input_data'])
        logger.info(f"ChatAgent result: {result}")
        print(f"ChatAgent result: {result}")
        
        # Return successful response
        return jsonify({'result': result})
    
    except Exception as e:
        # Log and return error response
        logger.error(f"Error processing request: {str(e)}")
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': f"Server error: {str(e)}"}), 500

# Wrap Flask app for ASGI compatibility
print("Wrapping Flask app with WsgiToAsgi")
asgi_app = WsgiToAsgi(app)
print("asgi_app defined successfully")

@app.route('/')
def home():
    return "Flask app is running!"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)