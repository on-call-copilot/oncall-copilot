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
    

def format_json_to_string(json_data):
    """
    Formats a list of JSON objects into a string where each key-value pair is formatted as "key = value".

    Args:
        json_data (list): A list of dictionaries representing JSON objects.

    Returns:
        str: A formatted string representing the JSON data.
    """
    formatted_strings = []
    for item in json_data:
        item_strings = []
        for key, value in item.items():
            item_strings.append(f"{key} = {value}")
        x = "\n".join(item_strings)
        formatted_strings.append("{" + x + "}")
    return "\n\n".join(formatted_strings)
