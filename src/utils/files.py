import json


def read_markdown_file(file_path: str) -> str:
    """
    Read a markdown file and return its contents as a string.
    
    Args:
        file_path (str): Path to the markdown file
        
    Returns:
        str: The contents of the markdown file as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading markdown file {file_path}: {e}")
        return "" 
    
def read_json_file(file_path: str) -> dict:
    """
    Read a JSON file and return its contents as a dictionary.
    
    Args:
        file_path (str): Path to the JSON file

    Returns:
        dict: The contents of the JSON file as a dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)  
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return {}