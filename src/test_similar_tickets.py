import chromadb
import dotenv
import openai
import os
import logging
import ast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_lists(l1: list, l2: list, similarity_threshold: float = 0.2) -> list:
    # Create a dictionary to store the highest value for each key
    merged_dict = {x['key']: x for x in l1}
    
    # Process second list, keeping higher values
    for x in l2:
        if x['key'] in merged_dict:
            # Keep the higher similarity value while preserving the dictionary
            if merged_dict[x['key']]['similarity'] < x['similarity']:
                merged_dict[x['key']] = x
        else:
            merged_dict[x['key']] = x
    
    # Convert to list
    merged_list = list(merged_dict.values())
    
    # Sort by similarity in descending order
    merged_list = sorted(merged_list, key=lambda x: x.get('similarity', 0), reverse=True)
    # Filter out items with similarity less than or equal to similarity_threshold
    filtered_list = [item for item in merged_list if item.get('similarity', 0) > similarity_threshold]
    
    # If no items meet the threshold, keep the top 4 items
    if len(filtered_list) < 4:
        filtered_list = merged_list[:4]
    
    merged_list = filtered_list
    # Remove similarity values from all items
    for item in merged_list:
        if 'similarity' in item:
            del item['similarity']
    if len(merged_list) > 8:
        return merged_list[:8]
    return merged_list


def get_embedding(text: str) -> list:
    """Get embedding using OpenAI's text-embedding-3-large model."""
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

def find_similar_tickets(query: str, collection_name: str = "issue-summary", n_results: int = 5, similarity_threshold: float = 0.3):
    """Find similar tickets based on a query."""
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="chroma-db")
    
    # Get the collection
    collection = client.get_collection(name=collection_name)
    
    # Get embedding for the query
    query_embedding = get_embedding(query)
    if not query_embedding:
        return
    
    # Search for similar documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    # Print results
    logger.info(f"Searching in collection: {collection_name}")
    logger.info("-" * 80)

    result = []
    
    for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
        similarity = 1 - distance
        if similarity > similarity_threshold:
            result.append({
                **ast.literal_eval(doc),
                'similarity': (1 - distance)
            })
        else:
            logger.info(f"Skipping ticket {metadata['key']} with similarity {similarity}")

    return result

def get_similar_tickets(query: str, similarity_threshold: float = 0.5):
    results_new = [find_similar_tickets(query, collection) for collection in ["issue-summary", "issue"]]
   
    return merge_lists(*results_new, similarity_threshold)

if __name__ == "__main__":
    # Ensure OpenAI API key is set
    dotenv.load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set the OPENAI_API_KEY environment variable")
        exit(1)
    
    # Test queries
    query = '''
        EE Debugger shows no forms were generated and sent to the carrier, despite completing the QLE.
        JIRA (Benefits Employee)
        1. Issue Description: 
        2 employees completed a QLE for marriage but EE Debugger shows no forms were generated and sent to the carrier.
        The event is showing finalised and not processed.
        What is the expected outcome: QLE forms should be generated and sent to the carrier.
        2. Account and EE Details:
        Company ID: 661d8511553828c082e1f0d4
        Country: US
        ARR: $25k+
        Entity Name: Curative AI
        Name & Role IDs of affected employee(s) / admin(s), if applicable: Pamela Policastri/66d0faf7826f4c6cfff3e258, Trung Nguyen/66d0fb1b826f4c6cfff3e834
        Escalated client: No
        PEO Customer: No
        3. Troubleshooting actions taken so far:
        Did you encounter the issue in your demo account in the same setup? Mention the steps taken:
        Found the same in EE Debugger.
        Log rocket session reproducing the issue. Explicitly mention if not available: NA
        Add loom video/screenshot if log rocket session is not available: NA
        Details/screenshots from the spoof session: Screenshot of the event:
        Add any additional troubleshooting performed:
        Event History: NA
        Confluence or Help article or previous case referred? NA
        4. Action required from Eng: Need to understand why the QLE forms were not generated and sent to the carrier.
        5. Product-Specific Issue Details: NA
    '''

    test_queries = [
        query,
    ]
    
    for query in test_queries:

        logger.info(f"\nSimilar tickets for query: '{query}'")
        # Test with issue summary collection

        results = [find_similar_tickets(query, collection) for collection in ["issue-summary", "issue"]]
        print(merge_lists(*results))

