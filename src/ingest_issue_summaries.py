import json
import os
import openai
import chromadb
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_embedding(text: str) -> list:
    """Get embedding using OpenAI's GPT-4 Turbo model."""
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        return None

def ingest_issues(file_path: str, persist_directory: str = "chroma-db"):
    """Ingest issues from JSON file into ChromaDB."""
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Create or get collections
    summary_collection = client.get_or_create_collection(
        name="issue-summary",
        metadata={"hnsw:space": "cosine"}
    )
    
    issue_collection = client.get_or_create_collection(
        name="issue",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Load JSON data
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} records from {file_path}")
    except FileNotFoundError:
        logger.error(f"Could not find file: {file_path}")
        return
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return
    
    # Prepare data for ingestion
    documents, metadata = [], []
    summary_embeddings, issue_embeddings = [], []
    ids = list(data.keys())
    
    # Process each record
    for key, value in tqdm(data.items(), desc="Processing records"):
        metadata.append({"key": key})
        documents.append(str(value))
        summary_embeddings.append(get_embedding(value['issue_summary']))
        issue_embeddings.append(get_embedding(value['issue']))

    # Add to ChromaDB
    logger.info("Adding issue summaries to ChromaDB...")
    summary_collection.add(
        embeddings=summary_embeddings,
        documents=documents,
        metadatas=metadata,
        ids=ids
    )
    
    logger.info("Adding issues to ChromaDB...")
    issue_collection.add(
        embeddings=issue_embeddings,
        documents=documents,
        metadatas=metadata,
        ids=ids
    )

if __name__ == "__main__":
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set the OPENAI_API_KEY environment variable")
        exit(1)
        
    file_path = "./outputs/jira-summary_v2_4o.json"
    ingest_issues(file_path) 