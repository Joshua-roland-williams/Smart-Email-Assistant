from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from .models import EmailProcessRequest, EmailSummaryResponse, ExportRequest, HealthCheckResponse, ErrorResponse
from ..main import SmartEmailAssistant
from ..config.settings import Settings
import os
import logging
from typing import List
from datetime import datetime # Import datetime

router = APIRouter()
smart_assistant = SmartEmailAssistant()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@router.get("/health", response_model=HealthCheckResponse, summary="Health Check")
async def health_check():
    """
    Performs a health check to ensure the API is running.
    """
    return HealthCheckResponse(status="ok", message="API is running")

@router.post("/process_emails", response_model=List[EmailSummaryResponse], summary="Process Emails")
async def process_emails_endpoint(request: EmailProcessRequest):
    """
    Fetches, processes, summarizes, and generates reply drafts for emails.
    """
    try:
        # Temporarily override settings for this request if different from defaults
        original_days_to_process = Settings.DAYS_TO_PROCESS
        original_enable_reply_generation = Settings.ENABLE_REPLY_GENERATION
        
        Settings.DAYS_TO_PROCESS = request.days_to_process
        Settings.ENABLE_REPLY_GENERATION = request.enable_reply_generation

        processed_data = smart_assistant.process_emails()
        smart_assistant.processed_data = processed_data # Store for export

        # Restore original settings
        Settings.DAYS_TO_PROCESS = original_days_to_process
        Settings.ENABLE_REPLY_GENERATION = original_enable_reply_generation

        # Convert list of dicts to list of Pydantic models
        return [EmailSummaryResponse(**item) for item in processed_data]
    except Exception as e:
        logging.error(f"Error processing emails: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process emails: {e}"
        )

@router.post("/export_data", summary="Export Processed Data to CSV")
async def export_data_endpoint(request: ExportRequest):
    """
    Exports the last processed email data to a CSV file.
    Note: This endpoint assumes `process_emails` has been run previously
    and `smart_assistant.processed_data` holds the data.
    A more robust solution would pass data directly or fetch from a cache.
    """
    if not hasattr(smart_assistant, 'processed_data') or not smart_assistant.processed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed data found to export. Please run /process_emails first."
        )
    
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(Settings.CSV_OUTPUT_PATH.format(timestamp="")) # Get base dir
        # This path needs to be relative to the project root or an absolute path
        # For now, let's make it relative to the backend directory
        output_dir_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'output')
        os.makedirs(output_dir_full_path, exist_ok=True)

        # Generate a unique filename for the export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Settings.CSV_OUTPUT_PATH.format(timestamp=timestamp)
        full_path = os.path.join(output_dir_full_path, os.path.basename(filename))
        
        smart_assistant.export_results(smart_assistant.processed_data, full_path)
        
        return {"message": f"Data exported successfully to {full_path}"}
        # If you want to return the file directly:
        # return FileResponse(path=full_path, filename=os.path.basename(full_path), media_type="text/csv")

    except Exception as e:
        logging.error(f"Error exporting data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {e}"
        )

# Add a route for authentication initiation (for frontend)
@router.get("/auth/google", summary="Initiate Google OAuth2 Flow")
async def auth_google():
    """
    Initiates the Google OAuth2 authentication flow.
    This will redirect the user to Google's authentication page.
    """
    # This is a placeholder. The actual OAuth flow for a web app
    # would involve redirecting the user to Google's auth URL
    # and then handling the callback. For a desktop app, it opens a browser.
    # For FastAPI, you'd typically handle this on the frontend or
    # use a library that manages the redirect.
    # For now, we'll just return a message.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth2 flow initiation for web frontend is not yet fully implemented via this endpoint. "
               "Please refer to the backend's main.py for desktop app authentication flow."
    )
