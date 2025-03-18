import dotenv
import os
from ingest_confluence import ingest_confluence
from json_ingest import ingest_jira


def main():
    dotenv.load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    ingest_type = input("Enter the type of ingestion you want to perform [confluence, jira, all]:")

    print(ingest_type)
    if ingest_type == "confluence":
        ingest_confluence()
    elif ingest_type == "jira":
        ingest_jira()
    elif ingest_type == "all":
        ingest_confluence()
        ingest_jira()
    else:
        raise ValueError("Invalid ingestion type")

if __name__ == "__main__":
    main()