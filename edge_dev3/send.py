import os
import mimetypes
from datetime import datetime

# Google Drive API imports (skeleton — install with:
#   pip install google-api-python-client google-auth)
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === MANUAL CONFIG (fill these in after you create your API keys) ===
SERVICE_ACCOUNT_FILE = "credentials.json"   # path to your service account JSON
DRIVE_FOLDER_ID = "PUT_YOUR_DRIVE_FOLDER_ID_HERE"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
# ====================================================================


def _build_drive_service():
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
