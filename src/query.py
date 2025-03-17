import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import subprocess

def main():
    persist_directory = "chroma-db"  # adjust if needed
    embeddings_model_name = "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    # Load the existing Chroma store
    vectorstore = Chroma(
        collection_name="docs",  
        embedding_function=embeddings,
        persist_directory=persist_directory
    )

    query = "Find where the employee hr data file is being created for selerix and suggest improvements in the code"
    docs = vectorstore.similarity_search(query, k=10)

    print(len(docs))

    seen = set()
    unique_docs = []
    for doc in docs:
        content_hash = hash(doc.page_content)
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)

    if not unique_docs:
        print("No documents found.")
        exit()

    context = "\n".join([f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}" for doc in docs])

    prompt = (
        f"You are an AI assistant designed to help software engineers understand Rippling's codebase. "
        f"Here are some relevant pieces of code and context retrieved from the source files:\n\n"
        f"{context}\n\n"
        f"Based on this information, answer the following question as clearly as possible: "
        f"{query}\n\n"
        f"If you do not have enough information from the context to answer the question, say: "
        f"\"I don't have enough context to answer this.\""
    )

    # Remove null bytes (most likely cause of the error)
    prompt = prompt.replace("\x00", "")

    result = subprocess.run(
        ['ollama', 'run', 'llama3:8b', prompt],
        capture_output=True, text=True, check=True
    )

    print("\n=== LLaMA 3's Answer ===")
    print(result.stdout)

if __name__ == "__main__":
    main()
