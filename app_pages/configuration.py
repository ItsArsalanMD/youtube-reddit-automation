import streamlit as st
import subprocess
import os

def get_ffmpeg_version():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return result.stdout.splitlines()[0]
    except Exception:
        return "FFmpeg not found or not in PATH"

st.header("⚙️ Global Configuration")

# Content Type Selection
st.subheader("📚 Content Type")
st.session_state.content_type = st.radio(
    "Select the type of content you want to generate:",
    ["Reddit Stories", "Psychological Facts"],
    index=["Reddit Stories", "Psychological Facts"].index(st.session_state.get('content_type', 'Reddit Stories')),
    horizontal=True
)

st.divider()

if st.session_state.content_type == "Reddit Stories":
    # Reddit Configuration Section
    st.subheader("🤖 Reddit Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.subreddit = st.text_input("Subreddit", value=st.session_state.get('subreddit', 'AmItheAsshole'))
    with col2:
        st.session_state.timeframe = st.selectbox("Timeframe", ["day", "week", "month", "all"], index=["day", "week", "month", "all"].index(st.session_state.get('timeframe', 'day')))
    with col3:
        st.session_state.limit = st.slider("Posts to fetch", 1, 50, st.session_state.get('limit', 10))
    
    st.divider()

# YouTube Configuration Section
st.subheader("📺 YouTube Settings")
from modules.youtube_uploader import YouTubeUploader

if 'yt_credentials' not in st.session_state:
    st.session_state.yt_credentials = None

if st.button("🔐 Authenticate with YouTube", help="Click to log in with your YouTube account using the client_secrets.json file."):
    with st.spinner("Authenticating... A browser window should open."):
        uploader = YouTubeUploader()
        creds = uploader.authenticate()
        if creds:
            st.session_state.yt_credentials = creds
            st.success("Authenticated successfully!")
        else:
            st.error("Authentication failed. Check if client_secrets.json exists and is valid.")

# Display Channel Info if authenticated
if st.session_state.yt_credentials:
    try:
        uploader = YouTubeUploader(credentials=st.session_state.yt_credentials)
        channel_info = uploader.get_channel_info()
        if channel_info:
            col_info1, col_info2 = st.columns([1, 4])
            with col_info1:
                st.image(channel_info['snippet']['thumbnails']['default']['url'], width=80)
            with col_info2:
                st.info(f"✅ Connected to: **{channel_info['snippet']['title']}**")
        else:
            st.warning("Connected, but could not fetch channel info.")
    except Exception as e:
        if "YouTube Data API v3 has not been used" in str(e) or "accessNotConfigured" in str(e):
            st.error("🚨 **YouTube Data API is disabled!**")
            st.markdown("""
            Please enable the YouTube Data API v3 in your Google Cloud Console:
            1. [Click here to enable the API](https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=715909416411)
            2. Click the **Enable** button.
            3. Wait a few minutes and try authenticating again.
            """)
        else:
            st.error(f"Error fetching channel info: {e}")

st.divider()

# FFmpeg Configuration Section
st.subheader("🛠️ System Configuration")
ffmpeg_info = get_ffmpeg_version()
st.code(ffmpeg_info, language="text")

if "FFmpeg not found" in ffmpeg_info:
    st.error("FFmpeg is missing! Please install it and add it to your system PATH.")
else:
    st.success("FFmpeg is correctly configured.")

st.info("These settings are global and will be used by the video generation and upload pages.")
