"""
Google Search Console Indexing API
Pings Google to request immediate crawling of newly published URLs.

Setup:
1. Create a service account in Google Cloud Console
2. Enable the "Web Search Indexing API"
3. Add service account as an owner in GSC
4. Download the JSON key file
5. Set GOOGLE_SERVICE_ACCOUNT_JSON env var to the JSON content
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/indexing"]

def get_service():
    """Build authenticated GSC service."""
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON env var not set")
    
    service_account_info = json.loads(sa_json)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    return build("indexing", "v3", credentials=credentials)

def ping_url(url: str, notification_type: str = "URL_UPDATED"):
    """
    Ping GSC to index/update a URL.
    notification_type: URL_UPDATED or URL_DELETED
    """
    service = get_service()
    service.urlNotifications().publish(
        body={"url": url, "type": notification_type}
    ).execute()
