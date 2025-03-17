from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def main():
    repo_path = "/Users/akshaykumarthakur/github/flux-apps"
    persist_dir = "chroma-db"


    loader = DirectoryLoader(repo_path, glob="**/*.py", recursive=True)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n\n", "\n", ".", "?", "!", " ", ""])
    split_docs = text_splitter.split_documents(documents)

    print(f"Loaded {len(documents)} documents and split into {len(split_docs)} chunks")

    embeddings_model_name = "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    vectorstore = Chroma.from_documents(
        collection_name="flux_apps_docs",
        documents=split_docs,
        embedding=embeddings,
        persist_directory=persist_dir)

    print(f"Ingestion Complete! Embeddings stored in {persist_dir}")

     
if __name__ == "__main__":
    main()

