from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes)
    credentials = flow.run_local_server(port=8080)  # Open a local server for authentication
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube
