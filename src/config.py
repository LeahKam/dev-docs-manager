import os

from dotenv import load_dotenv

load_dotenv()

PINECONE_INDEX_NAME = "devdocs-manager"
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"
COHERE_MODEL = "embed-english-v3.0"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
