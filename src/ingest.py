from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter, TokenTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Verify API key is available
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    repo_paths = ["/Users/akshaykumarthakur/personal-projects/rippling-llm/confluence-docs"]
    persist_dir = "chroma-db"

    for repo_path in repo_paths:
        loader = DirectoryLoader(repo_path, recursive=True)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=5000, chunk_overlap=0)

        texts = text_splitter.split_documents(documents)

        print(f"Loaded {len(documents)} documents and split into {len(texts)} chunks")

        token_text_splitter = TokenTextSplitter(chunk_size=5000, chunk_overlap=0)

        chunks = token_text_splitter.split_documents(texts)

        vectorstore = Chroma.from_documents(
            collection_name="confluence-docs",
            documents=chunks,
            embedding=OpenAIEmbeddings(model="text-embedding-ada-002"),
            persist_directory=persist_dir)

        print(f"Ingestion Complete! Embeddings stored in {persist_dir}")

     
if __name__ == "__main__":
    main()

