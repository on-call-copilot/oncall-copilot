import os
from sentence_transformers import SentenceTransformer
import chromadb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JsonQuerier:
    def __init__(self, persist_directory: str = "./chroma-db"):
        """Initialize the querier with ChromaDB client and embedding model."""
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collections = {
            "jira": self.client.get_collection(name="jira_documents"),
            "other": self.client.get_collection(name="other_documents")
        }
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Initialized JsonQuerier with ChromaDB and SentenceTransformer")

    def query(self, query_text: str, collection_name: str = None, n_results: int = 5):
        """Query the database for similar documents."""
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Determine which collection(s) to query
        collections_to_query = [collection_name] if collection_name else self.collections.keys()
        
        # Print results
        print(f"\nQuery: {query_text}")
        print("\nResults:")
        print("-" * 80)
        
        for collection_name in collections_to_query:
            collection = self.collections[collection_name]
            print(f"\nResults from {collection_name} collection:")
            
            # Search in ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
                print(f"\n{i+1}. Source: {metadata['source']}")
                print(f"   Key/Index: {metadata.get('key', metadata.get('index', 'N/A'))}")
                print(f"   Content: {doc}")
                print(f"   Similarity Score: {1 - distance:.4f}")
                print("-" * 80)

def main():
    # Initialize the querier
    querier = JsonQuerier()

    # Example queries demonstrating different use cases
    queries = [
        # Query all collections
        {
            "query": "Find all documents about employee benefits",
            "collection": None,
            "description": "Searching across all collections for employee benefits information"
        },
        
        # Query only Jira collection
        {
            "query": "Show me high priority bug reports from the last month",
            "collection": "jira",
            "description": "Searching only Jira tickets for recent high priority issues"
        },
        
        # Query specific collection with technical focus
        {
            "query": "Find integration issues with insurance carriers",
            "collection": "jira",
            "description": "Searching Jira tickets for carrier integration problems"
        },
        
        # Query all collections with specific focus
        {
            "query": "Show me all documents related to data processing errors",
            "collection": None,
            "description": "Searching all collections for data processing issues"
        }
    ]

    # Run queries
    for query_info in queries:
        print(f"\n{'='*80}")
        print(f"Query Description: {query_info['description']}")
        print(f"{'='*80}")
        
        querier.query(
            query_text=query_info['query'],
            collection_name=query_info['collection']
        )
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main() 