import os
import json
from typing import List, Dict, Any, Union
from sentence_transformers import SentenceTransformer
import chromadb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JsonIngester:
    def __init__(self, persist_directory: str = "./chroma-db"):
        """Initialize the ingester with ChromaDB and SentenceTransformer."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
        
        # Initialize collections for different data types
        self.collections = {
            "jira": self.client.get_or_create_collection(
                name="jira_tickets",
                metadata={"hnsw:space": "cosine"}
            ),
            "summary": self.client.get_or_create_collection(
                name="jira_tickets_summary",
                metadata={"hnsw:space": "cosine"}
            )
        }
        logger.info("Initialized collections for different data types")

    def get_collection_for_file(self, file_path: str) -> str:
        """Determine which collection to use based on the file type."""
        if file_path.endswith('jira-beninteg-data-dump.json'):
            return "jira"
        return "summary"

    def load_json_file(self, file_path: str) -> Any:
        """Load and parse a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Successfully loaded JSON file: {file_path}")
                return data
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            raise

    def format_jira_ticket(self, ticket: Dict[str, Any]) -> str:
        """Format a Jira ticket into a meaningful text representation."""
        if not ticket:
            return ""
            
        parts = []
        
        # Add ticket key and summary
        parts.append(f"Ticket: {ticket.get('key', 'N/A')}")
        parts.append(f"Summary: {ticket.get('summary', 'N/A')}")
        
        # Add description if present
        if ticket.get('description'):
            parts.append(f"Description: {ticket['description']}")
        
        # Add status and priority
        if ticket.get('status'):
            parts.append(f"Status: {ticket['status']}")
        if ticket.get('priority'):
            parts.append(f"Priority: {ticket['priority']}")
        
        # Add RCA information if present
        rca = ticket.get('rca', {})
        if rca and isinstance(rca, dict):
            parts.append("RCA:")
            if rca.get('category'):
                parts.append(f"  Category: {rca['category']}")
            if rca.get('subcategory'):
                parts.append(f"  Subcategory: {rca['subcategory']}")
            if rca.get('description'):
                parts.append(f"  Description: {rca['description']}")
        
        # Add components if present
        components = ticket.get('components', [])
        if components and isinstance(components, list):
            parts.append(f"Components: {', '.join(components)}")
        
        # Add comments if present
        comments = ticket.get('comments', [])
        if comments and isinstance(comments, list):
            parts.append("Comments:")
            for comment in comments:
                if isinstance(comment, dict) and comment.get('content'):
                    parts.append(f"  - {comment['content']}")
        
        return "\n".join(parts)

    def process_jira_tickets(self, tickets: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process Jira tickets in either list or dictionary format."""
        documents = []
        
        # Handle dictionary format (jira-summary.json)
        if isinstance(tickets, dict):
            for key, ticket in tickets.items():
                if not isinstance(ticket, dict):
                    continue
                
                # Ensure the ticket has a key
                if not ticket.get('key'):
                    ticket['key'] = key
                
                # Format the ticket content
                content = self.format_jira_ticket(ticket)
                if not content:
                    continue
                
                # Create metadata
                metadata = {
                    "source": "jira_ticket",
                    "key": ticket.get("key", "unknown"),
                    "priority": ticket.get("priority", "unknown"),
                    "status": ticket.get("status", "unknown"),
                    "components": ", ".join(ticket.get("components", [])) if isinstance(ticket.get("components"), list) else "",
                    "has_rca": bool(ticket.get("rca")),
                    "comment_count": len(ticket.get("comments", []) if isinstance(ticket.get("comments"), list) else []),
                    "has_linked_issues": bool(ticket.get("linked_issues"))
                }
                
                documents.append({
                    "content": content,
                    "metadata": metadata
                })
        
        # Handle list format (jira-beninteg-data-dump.json)
        elif isinstance(tickets, list):
            for ticket in tickets:
                if not isinstance(ticket, dict):
                    continue
                    
                # Format the ticket content
                content = self.format_jira_ticket(ticket)
                if not content:
                    continue
                
                # Create metadata
                metadata = {
                    "source": "jira_ticket",
                    "key": ticket.get("key", "unknown"),
                    "priority": ticket.get("priority", "unknown"),
                    "status": ticket.get("status", "unknown"),
                    "components": ", ".join(ticket.get("components", [])) if isinstance(ticket.get("components"), list) else "",
                    "has_rca": bool(ticket.get("rca")),
                    "comment_count": len(ticket.get("comments", []) if isinstance(ticket.get("comments"), list) else [])
                }
                
                documents.append({
                    "content": content,
                    "metadata": metadata
                })
        else:
            logger.warning("Expected list or dict of tickets but got %s", type(tickets))
        
        return documents

    def process_json_content(self, content: Any, source_file: str) -> List[Dict[str, Any]]:
        """Process JSON content and prepare documents for embedding."""
        documents = []
        
        # Handle Jira ticket files
        if source_file.endswith('jira-beninteg-data-dump.json') or source_file.endswith('jira-summary.json'):
            return self.process_jira_tickets(content)
        
        # Handle other JSON files
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, (str, int, float, bool)):
                    documents.append({
                        "content": f"{key}: {value}",
                        "metadata": {"source": source_file, "key": key}
                    })
                elif isinstance(value, dict):
                    documents.append({
                        "content": json.dumps(value, indent=2),
                        "metadata": {"source": source_file, "key": key}
                    })
        elif isinstance(content, list):
            for i, item in enumerate(content):
                if isinstance(item, (str, int, float, bool)):
                    documents.append({
                        "content": str(item),
                        "metadata": {"source": source_file, "index": i}
                    })
                elif isinstance(item, dict):
                    documents.append({
                        "content": json.dumps(item, indent=2),
                        "metadata": {"source": source_file, "index": i}
                    })
        
        return documents

    def ingest_file(self, file_path: str):
        """Ingest a JSON file into ChromaDB."""
        try:
            logger.info(f"Loading file: {file_path}")
            content = self.load_json_file(file_path)
            
            if not content:
                logger.warning(f"No valid content found in {file_path}")
                return
            
            logger.info(f"Processing content from {file_path}")
            documents = self.process_json_content(content, file_path)
            
            if not documents:
                logger.warning(f"No documents generated from {file_path}")
                return
            
            # Determine which collection to use
            collection_type = self.get_collection_for_file(file_path)
            collection = self.collections[collection_type]
            
            logger.info(f"Generating embeddings for {len(documents)} documents")
            texts = [doc["content"] for doc in documents]
            embeddings = self.model.encode(texts).tolist()
            
            logger.info(f"Adding documents to {collection_type} collection")
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=[doc["metadata"] for doc in documents],
                ids=[f"{file_path}_{i}" for i in range(len(documents))]
            )
            
            logger.info(f"Successfully ingested {len(documents)} documents from {file_path} into {collection_type} collection")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

def ingest_jira():
    """Main function to ingest JSON files."""
    ingester = JsonIngester()
    output_dir = "/Users/akshaykumarthakur/personal-projects/rippling-llm/outputs"
    
    try:
        for filename in os.listdir(output_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(output_dir, filename)
                ingester.ingest_file(file_path)
        
        logger.info("Jira Ingestion complete!")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise

if __name__ == "__main__":
    ingest_jira() 