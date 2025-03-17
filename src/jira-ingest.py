import chromadb
import json
from sentence_transformers import SentenceTransformer

def load_jira_tickets(file_path: str) -> list[dict]:
    """Load Jira tickets from a JSON file."""

    with open(file_path, 'r', encoding='utf-8') as f:
        tickets = json.load(f)
        return tickets.values()
    
def persist_jira_tickets(tickets: list[dict]):

    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma-db")  # Change path if needed
    collection = chroma_client.get_or_create_collection(name="tickets")

    # Initialize embedding model
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight & effective

    for ticket in tickets:

        # Generate embeddings for the summary
        embedding = embedding_model.encode(ticket["summary"]).tolist()

        # Store in ChromaDB
        collection.add(
            ids=[ticket["key"]],  # Unique identifier
            embeddings=[embedding],  # Storing embeddings
            metadatas=[{"key": ticket["key"], "summary": ticket["summary"]}]
        )

        print(f"Ticket {ticket['key']} stored successfully!")

if __name__ == "__main__":
    persist_jira_tickets(load_jira_tickets('./outputs/jira-summary.json'))