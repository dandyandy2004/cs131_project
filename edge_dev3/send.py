import os
import mimetypes
from datetime import datetime

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load variables from edge_dev3/.env (same folder as this file)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _build_drive_service():
    if not DRIVE_FOLDER_ID:
        raise RuntimeError("DRIVE_FOLDER_ID is not set — check edge_dev3/.env")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account file not found: {SERVICE_ACCOUNT_FILE}"
        )
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def upload_snapshot(local_path, label="event"):
    """Upload a single image file to the configured Google Drive folder."""
    service = _build_drive_service()
    filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    file_metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    mime = mimetypes.guess_type(local_path)[0] or "image/jpeg"
    media = MediaFileUpload(local_path, mimetype=mime)

    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id, webViewLink"
    ).execute()

    print(f"[send] uploaded {filename} -> {uploaded.get('webViewLink')}")
    return uploaded
