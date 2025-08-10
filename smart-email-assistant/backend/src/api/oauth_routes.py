from fastapi import APIRouter, HTTPException, status, Request, Response
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleAuthRequest
import os
import pickle
import json
import logging
from ..config.settings import Settings

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# OAuth 2.0 scopes for Gmail API
SCOPES = Settings.GMAIL_SCOPES

# Path to credentials.json and token.json
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', Settings.CREDENTIALS_FILE)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', Settings.TOKEN_FILE)

@router.get("/auth/status", summary="Check Authentication Status")
async def auth_status():
    """
    Checks if the backend is authenticated with Google.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(GoogleAuthRequest())
                    with open(TOKEN_FILE, 'wb') as token:
                        pickle.dump(creds, token)
                return {"authenticated": True, "message": "Backend is authenticated."}
            else:
                return {"authenticated": False, "message": "Authentication token invalid or expired. Please re-authenticate."}
        except Exception as e:
            logging.error(f"Error checking auth status: {e}", exc_info=True)
            return {"authenticated": False, "message": f"Error checking authentication status: {e}"}
    return {"authenticated": False, "message": "No authentication token found."}

@router.get("/auth/google/login", summary="Initiate Google OAuth2 Login")
async def google_login():
    """
    Initiates the Google OAuth2 login flow.
    Redirects the user to Google's consent screen.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google client secrets file not found at {CREDENTIALS_FILE}. Please configure your credentials.json."
        )
    
    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=Settings.GOOGLE_REDIRECT_URI # This should match one of your authorized redirect URIs in Google Cloud Console
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        # In a real application, you'd store the 'state' in a session to prevent CSRF.
        # For this example, we'll just redirect.
        return {"authorization_url": authorization_url}
    except Exception as e:
        logging.error(f"Error initiating Google login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate Google login: {e}"
        )

@router.get("/auth/google/callback", summary="Google OAuth2 Callback")
async def google_callback(request: Request):
    """
    Handles the callback from Google after user authentication.
    Exchanges the authorization code for tokens and saves them.
    """
    code = request.query_params.get('code')
    error = request.query_params.get('error')

    if error:
        logging.error(f"OAuth callback error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback error: {error}"
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not found in callback."
        )

    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=Settings.GOOGLE_REDIRECT_URI
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        # Redirect back to the frontend application
        # You might want to pass a success/failure parameter here
        return Response(status_code=status.HTTP_302_FOUND, headers={"Location": Settings.FRONTEND_REDIRECT_URI_AFTER_AUTH})
    except Exception as e:
        logging.error(f"Error during Google OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete Google OAuth: {e}"
        )

@router.post("/auth/logout", summary="Logout and Revoke Google Credentials")
async def logout():
    """
    Revokes the Google access token and deletes the local token file.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.token:
                # Revoke the token
                creds.revoke(GoogleAuthRequest())
                logging.info("Google token revoked.")
            
            os.remove(TOKEN_FILE)
            logging.info("Local token file deleted.")
            return {"message": "Logged out successfully."}
        except Exception as e:
            logging.error(f"Error during logout: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to logout: {e}"
            )
    return {"message": "No active session to log out from."}
