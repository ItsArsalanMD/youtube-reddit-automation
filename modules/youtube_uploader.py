import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE file specifies the client ID and client secret of the app.
CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")

# This scope allows for full YouTube account access.
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

class YouTubeUploader:
    def __init__(self, credentials=None):
        self.youtube = None
        if credentials:
            self.youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    def authenticate(self):
        """
        Authenticates the user and returns a YouTube service object.
        """
        if not os.path.exists(CLIENT_SECRETS_FILE):
            print(f"Error: {CLIENT_SECRETS_FILE} not found.")
            return None

        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        self.youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        return credentials

    def get_channel_info(self):
        """
        Fetches the authenticated user's channel information.
        """
        if not self.youtube:
            return None
        
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            return response['items'][0]
        return None

    def upload_video(self, video_path, title, description, tags=None, category_id="22", privacy_status="private", publish_at=None):
        """
        Uploads a video to YouTube.
        """
        if not self.youtube:
            if not self.authenticate():
                return False

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }

        if publish_at:
            # publishAt requires privacyStatus to be 'private'
            body['status']['publishAt'] = publish_at
            body['status']['privacyStatus'] = 'private'

        # Call the API's videos.insert method to create and upload the video.
        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )

        print(f"Uploading file: {video_path}")
        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        
        print(f"Video id '{response['id']}' was successfully uploaded.")
        return response['id']

if __name__ == "__main__":
    # Test uploader (will require browser interaction)
    uploader = YouTubeUploader()
    # uploader.upload_video("path/to/video.mp4", "Test Title", "Test Description")
    print("YouTube uploader module initialized. Run authentication manually.")
