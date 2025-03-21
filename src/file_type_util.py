#!/usr/bin/env python3
import json

def change_file_from_list_to_dict(input_file, output_file):
    print(f"Reading tickets from {input_file}...")
    
    try:
        with open(input_file, 'r') as f:
            all_tickets = json.load(f)
        
        print(f"Loaded {len(all_tickets)} tickets from file")

        tickets_by_key = {ticket['key']: ticket for ticket in all_tickets}

        print(f"Created a dictionary of {len(tickets_by_key)} tickets from file")
        
        with open(output_file, 'w') as f:
            json.dump(tickets_by_key, f, indent=2)
        
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Define the input and output file paths
    input_file = "./jira-exports/jira-beninteg-data-dump.json"
    output_file = "./jira-exports/jira-beninteg-data-dump-by-key.json"
    
    change_file_from_list_to_dict(input_file, output_file)
