from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import asyncio
import json
from datetime import datetime
import uuid
from contextlib import asynccontextmanager
import sys
import io
from threading import Thread, Lock
import queue
import time
import os

# Import your jira integration
from jira_integration import JiraIntegrator

# Global dictionary to store active connections and their message queues
active_connections: Dict[str, asyncio.Queue] = {}

# Global print queue with a lock for thread safety
print_queue = queue.Queue()
queue_lock = Lock()

# Store original print function
original_print = print

# Create a patched print function that adds to our queue
def patched_print(*args, **kwargs):
    # Call the original print first
    result = original_print(*args, **kwargs)
    
    # Format the message string
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    message = sep.join(str(arg) for arg in args) + end
    
    # Add to our global queue if it's not empty
    if message.strip():
        try:
            with queue_lock:
                print_queue.put(message)
        except:
            pass  # Fail silently if queue operations fail
    
    return result

# Replace the global print function
sys.modules['builtins'].print = patched_print

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown - Close all connections and restore print
    for queue in active_connections.values():
        await queue.put(None)  # Signal to close connection
    # Restore original print function
    sys.modules['builtins'].print = original_print

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request models
class IssueRequest(BaseModel):
    jiraLink: str
    connection_id: Optional[str] = None

class IssueResponse(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None

jira_client = JiraIntegrator()

# Debug print function that sends to SSE
async def debug_print(connection_id: str, message: Any, level: str = "info"):
    """Send debug messages to the SSE stream"""
    if connection_id in active_connections:
        queue = active_connections[connection_id]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if isinstance(message, dict) or isinstance(message, list):
            message_text = json.dumps(message)
        else:
            message_text = str(message)
            
        data = {
            "timestamp": timestamp,
            "level": level,
            "message": message_text
        }
        
        await queue.put(json.dumps(data))
    else:
        original_print(f"Warning: Connection {connection_id} not found in active_connections")

@app.get("/api/events")
async def events(request: Request):
    """SSE endpoint to stream logs to the client"""
    connection_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    active_connections[connection_id] = queue
    
    # Function to clean up when client disconnects
    async def cleanup():
        if connection_id in active_connections:
            del active_connections[connection_id]
    
    # Register cleanup handler
    request.state.connection_id = connection_id
    
    async def event_generator():
        try:
            # Send the connection ID first so the client can use it
            yield f"data: {json.dumps({'type': 'connection', 'id': connection_id})}\n\n"
            
            # Send an immediate test message
            test_message = json.dumps({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "level": "info",
                "message": "Connection established successfully"
            })
            yield f"data: {test_message}\n\n"
            
            while True:
                # Wait for messages
                data = await queue.get()
                if data is None:  # Signal to close
                    break
                    
                # Send to client with SSE format
                yield f"data: {data}\n\n"
                
        except asyncio.CancelledError:
            # Client disconnected
            await cleanup()
        except Exception as e:
            await cleanup()
        finally:
            await cleanup()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Connection-ID": connection_id,
        },
    )

# Task to monitor print queue and send to client
async def monitor_print_queue(connection_id: str):
    """Monitor the print queue and forward to the client"""
    while connection_id in active_connections:
        try:
            # Check if there's anything in the queue
            if not print_queue.empty():
                with queue_lock:
                    if not print_queue.empty():
                        message = print_queue.get_nowait()
                        if message and message.strip():
                            # Send to client
                            await debug_print(connection_id, message.strip(), "output")
        except Exception as e:
            original_print(f"Error processing print queue: {e}")
        
        # Small delay to avoid CPU overuse
        await asyncio.sleep(0.1)

@app.post("/api/process-issue")
async def process_issue(request: IssueRequest):
    try:
        # Get issue details from Jira
        issue_details = jira_client.get_issue_details(request.jiraLink)

        return IssueResponse(
            status="success",
            message="Issue processed successfully",
            data={
                "jiraLink": request.jiraLink,
                "companyId": issue_details.get('companyId', ''),
                "label": issue_details.get('labels', []),
                "roleId": issue_details.get('roleId', ''),
            }
        )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/process-with-stream")
async def process_with_stream(request: IssueRequest):
    """Run normal processing with streaming"""
    connection_id = request.connection_id
    
    # Check if the connection exists
    if connection_id not in active_connections:
        # Create a new queue for this connection
        queue = asyncio.Queue()
        active_connections[connection_id] = queue
    
    # Start processing in background task
    async def background_processing():
        try:
            await debug_print(connection_id, "Starting issue processing...", "info")
            
            # Get the issue details
            await debug_print(connection_id, "Fetching issue details from Jira...", "info")
            try:
                issue_details = jira_client.get_issue_details(request.jiraLink)
                await debug_print(connection_id, "Issue details retrieved successfully", "success")
                await debug_print(connection_id, issue_details, "data")
                
                # Final result
                result = {
                    "jiraLink": request.jiraLink,
                    "companyId": issue_details.get('companyId', ''),
                    "label": issue_details.get('labels', []),
                    "roleId": issue_details.get('roleId', ''),
                    "processed": True
                }
                
                await debug_print(connection_id, "Processing completed successfully", "success") 
                await debug_print(connection_id, result, "result")
                
            except Exception as e:
                await debug_print(connection_id, f"Error fetching issue: {str(e)}", "error")
                
        except Exception as e:
            await debug_print(connection_id, f"Error during processing: {str(e)}", "error")
        finally:
            # Signal end of processing
            await debug_print(connection_id, "Stream complete", "end")
    
    # Start the background task
    asyncio.create_task(background_processing())
    
    # Return the connection ID to the client
    return {"status": "processing", "connection_id": connection_id}

@app.post("/api/triage-issue")
async def triage_issue(request: IssueRequest):
    """Run the triage_ticket function and stream its output"""
    from bartender import triage_ticket  # Import here to avoid circular imports
    
    # Use existing connection ID
    connection_id = request.connection_id
    
    # Check if the connection exists
    if connection_id not in active_connections:
        # Create a new queue for this connection
        queue = asyncio.Queue()
        active_connections[connection_id] = queue
    
    # Start monitoring the print queue
    queue_monitor = asyncio.create_task(monitor_print_queue(connection_id))
    
    # Start processing in background task
    async def background_processing():
        try:
            await debug_print(connection_id, "Starting ticket triage...", "info")
            
            # Get the issue details first
            await debug_print(connection_id, "Fetching issue details from Jira...", "info")
            try:
                issue_details = jira_client.get_issue_details(request.jiraLink)
                await debug_print(connection_id, "Issue details retrieved successfully", "success")
                
                # Create a detailed string with issue information
                issue_text = f"""
                Title: {issue_details.get('summary', 'N/A')}
                Description: {issue_details.get('description', 'N/A')}
                """
                
                await debug_print(connection_id, "Starting ticket analysis... Sit tight for but a minute or two...", "info")
                
                # Run the triage function in an executor to not block the event loop
                loop = asyncio.get_event_loop()
                
                def run_triage():
                    try:
                        # When triage_ticket runs, it will use our patched print
                        # which already puts output in the global queue
                        result = triage_ticket(issue_text, request.jiraLink)
                        return result
                    except Exception as e:
                        original_print(f"Error in triage: {e}")
                        return None
                
                # Run in executor to not block
                await loop.run_in_executor(None, run_triage)
                
                # Make sure we've processed all the prints
                await asyncio.sleep(1)
                
                # Process complete
                await debug_print(connection_id, "Ticket triage completed", "success")
                
            except Exception as e:
                await debug_print(connection_id, f"Error during triage: {str(e)}", "error")
                
        except Exception as e:
            await debug_print(connection_id, f"Error during processing: {str(e)}", "error")
        finally:
            # Wait a moment to process any final prints
            await asyncio.sleep(1)
            # Signal end of processing
            await debug_print(connection_id, "Stream complete", "end")
            # Cancel the queue monitor
            queue_monitor.cancel()
    
    # Start the background task
    asyncio.create_task(background_processing())
    
    # Return the connection ID to the client
    return {"status": "processing", "connection_id": connection_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)