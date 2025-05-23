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

2. Create environment file:

   - Create a `.env` file in the root directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

3. Download the Chroma DB SQLite file:

   - Download the Chroma DB SQLite file from [Google Drive](https://drive.google.com/file/d/1gg_1P2g3_gz6QLWCb794lG0Bh1JmhgMB/view?usp=drive_link)
   - Place the downloaded file in the `chroma-db` directory
   - Note: This file is too large for GitHub. Ideally for production use, we would be storing it in S3.

## Running with Jira Integration

1. Configure environment variables:

   - Copy the `.env.example` file to `.env` (if not already present)
   - Add necessary environment variables in the `.env` file

2. Start the application:
   - Open `src/index.html` in your web browser
   - Run the API server:
     ```bash
     python src/api.py
     ```

## Running Locally Without Jira Integration

To run the application locally without Jira integration:

1. Paste your input ticket details with description in the `input.txt` file
2. Run the processing script:
   ```bash
   python src/bartender_local.py
   ```
3. For additional analysis or follow-up questions:
   - Write your follow-up question in `next_input.txt`
   - Enter 'Y' to continue
   - The first analysis and final analysis will be printed and saved to `response.md`
   - You can preview the formatted response using Cmd+Shift+V in VSCode (with cursor on the file)

## Requirements

- Python 3.x
- Modern web browser
- Required Python packages (listed in requirements.txt)

## Additional Notes

- Make sure all required environment variables are properly set in the `.env` file
- The application requires an active internet connection for certain features
- For development, ensure you have write permissions in the project directory
