import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import json

# Load environment variables from .env file with override
load_dotenv(dotenv_path='/home/vincent/ixome/.env', override=True)

# Retrieve API keys
openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')

# Verify the loaded keys
print(f"Loaded OpenAI API key: {openai_api_key[:10]}... (hidden for security)")
print(f"Loaded Pinecone API key: {pinecone_api_key[:10]}... (hidden for security)")

# Check if keys are loaded
if not openai_api_key or not pinecone_api_key:
    print("Error: Missing API keys! Check /home/vincent/ixome/.env")
    exit()

# Initialize Pinecone
pinecone = Pinecone(api_key=pinecone_api_key)
index_name = 'lutron-support'
index = pinecone.Index(index_name)

# Initialize OpenAI client
openai_client = OpenAI(api_key=openai_api_key)

# Function to generate embeddings
def get_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Load data from JSON file
json_file_path = '/home/vincent/ixome/scrapy-selenium/lutron_scraper/lutron_data_batch1.json'
with open(json_file_path, 'r') as f:
    data = json.load(f)

# Upsert vectors in batches
batch_size = 100
for i in range(0, len(data), batch_size):
    batch = data[i:i + batch_size]
    vectors = []
    for j, item in enumerate(batch):
        text = item['text']
        embedding = get_embedding(text)
        vector_id = f"batch1_{i + j}"
        vectors.append((vector_id, embedding, {'text': text}))

    index.upsert(vectors)
    print(f"Upserted batch {i // batch_size + 1} with {len(vectors)} vectors.")

print("All data loaded into Pinecone successfully!")