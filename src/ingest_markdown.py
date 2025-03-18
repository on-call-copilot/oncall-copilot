import os
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import glob

from langchain_text_splitters import MarkdownTextSplitter

# Step 1: Load the Markdown file
def load_markdown_file(file_path):
    loader = UnstructuredMarkdownLoader(file_path)
    documents = loader.load()
    return documents

# Step 2: Split the document into chunks
def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
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
        persist_directory="/Users/akshaykumarthakur/personal-projects/rippling-llm/chroma_db"  # Specify where to store the database
    )
    
    # Persist the database to disk
    vectordb.persist()
    
    return vectordb

# Main function to process a markdown file
def process_markdown_and_create_db(collection_name="markdown_collection"):
    markdown_file_path = "/Users/akshaykumarthakur/personal-projects/rippling-llm/confluence-doc-markdowns"
    # Load
    markdown_files = glob.glob(f"{markdown_file_path}/**/*.md", recursive=True)
    all_documents = []
    for file_path in markdown_files:
        documents = load_markdown_file(file_path)
        all_documents.extend(documents)
    # Split
    chunks = split_documents(all_documents)
    print(f"Split into {len(chunks)} chunks")
    
    # Embed and store
    vectordb = create_and_store_embeddings(chunks, collection_name)
    print(f"Created Chroma DB with {vectordb._collection.count()} vectors")
    
    return vectordb

# Example usage
if __name__ == "__main__":
    db = process_markdown_and_create_db()