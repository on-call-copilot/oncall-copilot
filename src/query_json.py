import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JsonQuerier:
    def __init__(self, persist_directory: str = "chroma-db"):
        """Initialize the querier with ChromaDB client and embedding model."""
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collections = {
            "jira": self.client.get_collection(name="jira_tickets"),
        }
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Initialized JsonQuerier with ChromaDB and SentenceTransformer")

    def query(self, query_text: str, collection_name: str = None, n_results: int = 5):
        """Query the database for similar documents."""
        # Generate embedding for the query
        query_embedding = self.embedding_model.encode(query_text).tolist()
        # Determine which collection(s) to query
        collections_to_query = [collection_name] if collection_name else self.collections.keys()
        ticket_ids = []
        for collection_name in collections_to_query:
            collection = self.collections[collection_name]
            print(f"\nResults from {collection_name} collection:")
            # Search in ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
                ticket_ids.append(metadata.get('key', metadata.get('index', 'N/A')))
                print("-" * 80)
        
        return ticket_ids


def query_jira(queries: list[dict]):
    # Initialize the querier
    querier = JsonQuerier()

    try:
        with open("/Users/akshaykumarthakur/personal-projects/rippling-llm/outputs/jira-summary.json", 'r') as f:
            jira_summary = json.load(f)
    except FileNotFoundError:
        logger.error("Could not find outputs/jira-summary.json")
        jira_summary = {}

    print("got jira summary")

    # Run queries
    for query_info in queries:
        print(f"\n{'='*80}")
        print(f"{'='*80}")        
        print(query_info)
        ticket_ids = querier.query(
            query_text=query_info['query'],
            collection_name="jira"
        )

        print("\n" + "="*80 + "\n")

        prompt = f"""
        summary: {jira_summary[ticket_ids[0]]['summary']}
        rca : {jira_summary[ticket_ids[0]].get('rca', None)}
        steps: {jira_summary[ticket_ids[0]].get('steps', None)}
        data_models: {jira_summary[ticket_ids[0]].get('data_models', None)}
        """

        return prompt

if __name__ == "__main__":
    query_jira([{"query": "What is the status of the ticket BENINTEG-4205?"}])