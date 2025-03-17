#!/usr/bin/env python3
import json
import os

def filter_tickets(input_file, output_file, ticket_ids):
    """
    Read a JSON file containing Jira tickets, filter for specific ticket IDs,
    and save the filtered tickets to a new JSON file.
    
    Args:
        input_file (str): Path to the JSON file with all tickets
        output_file (str): Path where the filtered tickets will be saved
        ticket_ids (list): List of ticket IDs to filter for
    """
    print(f"Reading tickets from {input_file}...")
    
    try:
        with open(input_file, 'r') as f:
            all_tickets = json.load(f)
        
        print(f"Loaded {len(all_tickets)} tickets from file")
        
        # Filter for the specified ticket IDs
        filtered_tickets = [ticket for ticket in all_tickets if ticket.get('key') in ticket_ids]
        
        print(f"Found {len(filtered_tickets)} matching tickets")
        
        # Check if any tickets are missing
        found_ids = {ticket.get('key') for ticket in filtered_tickets}
        missing_ids = set(ticket_ids) - found_ids
        
        if missing_ids:
            print(f"Warning: Could not find tickets with IDs: {', '.join(missing_ids)}")
        
        # Save the filtered tickets to the output file
        with open(output_file, 'w') as f:
            json.dump(filtered_tickets, f, indent=2)
        
        print(f"Saved filtered tickets to {output_file}")
        
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Define the input and output file paths
    input_file = "jira-beninteg-data-dump.json"
    output_file = "selected_tickets.json"
    
    # Define the ticket IDs to filter for
    ticket_ids = [
        "BENINTEG-3687",
        "BENINTEG-3550",
        "BENINTEG-4092",
        "BENINTEG-2456",
        "BENINTEG-4108",
        "BENINTEG-3997"
    ]
    
    # Run the filter function
    filter_tickets(input_file, output_file, ticket_ids)
