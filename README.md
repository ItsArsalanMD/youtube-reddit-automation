# YouTube-Reddit Automation MVP

An automated pipeline to fetch Reddit stories and turn them into viral YouTube Shorts.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Fill in your Reddit API credentials, Gemini API key, and YouTube settings.

3. **External Assets**:
   - Place a vertical background video (e.g., Minecraft parkour) at `assets/minecraft_parkour.mp4`.
   - Download your Google Cloud `client_secrets.json` for YouTube API and place it in the root directory.

4. **FFmpeg**:
   - Ensure `ffmpeg` is installed on your system and added to your PATH.

## Running the App

```bash
py -m streamlit run app.py
```

## Workflow

1. **Fetch**: Pull top posts from any subreddit (e.g., `r/AmItheAsshole`).
2. **Generate**: Use Gemini to rewrite the post into a viral narration script.
3. **Review**: Edit the script, title, or description in the UI.
4. **Render**: Automatically generate TTS, transcribe captions, and render the final video using FFmpeg.
5. **Upload**: Authentic via OAuth and upload the video directly to your YouTube channel as Private.
