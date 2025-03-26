# OnCall Copilot

A Python-based application for managing on-call operations and documentation.

## Project Structure

```
.
├── src/                    # Source code directory
│   ├── api.py             # Main API server
│   ├── bartender.py       # Main processing script
│   └── index.html         # Frontend interface
├── requirements.txt       # Python dependencies
├── input.txt             # Input file for local testing
└── .env                   # Environment variables
```

## Setup Instructions

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:

   - Copy the `.env.example` file to `.env` (if not already present)
   - Add necessary environment variables in the `.env` file

3. Start the application:
   - Open `src/index.html` in your web browser
   - Run the API server:
     ```bash
     python src/api.py
     ```

## Running Locally Without Jira Integration

To run the application locally without Jira integration:

1. Comment out line 14 in `src/bartender.py` to disable Jira functionality:
   ```python
   # jira_client = JiraIntegrator()
   ```
2. Paste your input (Jira description) in the `input.txt` file
3. Run the processing script:
   ```bash
   python src/bartender.py
   ```

## Requirements

- Python 3.x
- Modern web browser
- Required Python packages (listed in requirements.txt)

## Additional Notes

- Make sure all required environment variables are properly set in the `.env` file
- The application requires an active internet connection for certain features
- For development, ensure you have write permissions in the project directory
