import os
import dotenv
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import glob
import json
from langchain_core.documents import Document

from langchain_text_splitters import MarkdownHeaderTextSplitter

HEADERS_TO_SPLIT_ON = [
    ("##", "Header 2"),
]

# Step 1: Load the Markdown file
def load_markdown_file(file_path):
    # loader = UnstructuredMarkdownLoader(file_path)
    # documents = loader.load()
    # return documents

    with open(file_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    document = Document(page_content=markdown_text)
    return document



# Step 2: Split the document into chunks
def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    markdown_splitter = MarkdownHeaderTextSplitter(HEADERS_TO_SPLIT_ON, strip_headers=False)
    chunks = markdown_splitter.split_text(documents.page_content)
    return chunks

# Step 3: Create embeddings and store in Chroma DB
def create_and_store_embeddings(chunks, collection_name="markdown_collection"):
    # Initialize the OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get("OPENAI_API_KEY")  # Set your API key as an environment variable
    )
    
    # Create a new Chroma collection and add documents
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory="chroma-confluence-doc-markdowns"  # Specify where to store the database
    )
    
    # Persist the database to disk
    vectordb.persist()
    return vectordb

# Main function to process a markdown file
def process_markdown_and_create_db(collection_name="markdown_collection"):
    # Load JSON file with markdown file mappings
    with open("src/confluence_markdown_docs_json.json", "r") as f:
        markdown_mappings = json.load(f)
    
    all_documents = []
    for page_id, page_info in markdown_mappings.items():
        file_path = page_info["path"]
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
            
        document = load_markdown_file(file_path)
        # Add metadata to each document
        document.metadata["page_id"] = page_info["pageId"]
        document.metadata["page_url"] = page_info["page_link"]
        
        all_documents.append(document)
    
    # print(all_documents[0])

    all_chunks = []
    for doc in all_documents:
        chunks = split_documents(doc)
        for chunk in chunks:
            chunk.metadata["page_id"] = doc.metadata["page_id"]
            chunk.metadata["page_url"] = doc.metadata["page_url"]
        all_chunks.extend(chunks)

    # Split the documents into chunks
    print(f"Split into {len(all_chunks)} chunks")
    # print(all_chunks[2])
    # return
    
    # Embed and store
    vectordb = create_and_store_embeddings(all_chunks, collection_name)
    print(f"Created Chroma DB with {vectordb._collection.count()} vectors")
    
    return vectordb

# Example usage
if __name__ == "__main__":
    dotenv.load_dotenv()
    db = process_markdown_and_create_db()