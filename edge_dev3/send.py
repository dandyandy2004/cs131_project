import os
from datetime import datetime

from dotenv import load_dotenv
from google.cloud import storage

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def upload_snapshot(local_path, label="event"):
    if not BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME is not set — check edge_dev3/.env")

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    blob = bucket.blob(filename)

    blob.upload_from_filename(local_path)


    image_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    print("User can view image here:", image_url)   
    return filename