import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Reddit-to-Shorts Automation", 
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global session state
def init_state():
    # Configuration
    if 'content_type' not in st.session_state:
        st.session_state.content_type = "Reddit Stories"
    if 'subreddit' not in st.session_state:
        st.session_state.subreddit = "AmItheAsshole"
    if 'timeframe' not in st.session_state:
        st.session_state.timeframe = "day"
    if 'limit' not in st.session_state:
        st.session_state.limit = 10
    if 'youtube_channel' not in st.session_state:
        st.session_state.youtube_channel = "Channel 1"
    if 'upload_style' not in st.session_state:
        st.session_state.upload_style = "Default"
    
    # Generation State
    if 'posts' not in st.session_state:
        st.session_state.posts = []
    if 'selected_post' not in st.session_state:
        st.session_state.selected_post = None
    if 'script' not in st.session_state:
        st.session_state.script = ""
    if 'metadata' not in st.session_state:
        st.session_state.metadata = {"title": "", "description": ""}
    if 'visual_hook_title' not in st.session_state:
        st.session_state.visual_hook_title = ""
    if 'video_ready' not in st.session_state:
        st.session_state.video_ready = False
    if 'current_video' not in st.session_state:
        st.session_state.current_video = None

init_state()

# Define navigation
pages = {
    "Creation": [
        st.Page("app_pages/generate.py", title="Video Generation", icon=":material/video_call:"),
    ],
    "Publishing": [
        st.Page("app_pages/upload.py", title="Upload to Youtube", icon=":material/publish:"),
    ],
    "Settings": [
        st.Page("app_pages/configuration.py", title="Configuration", icon=":material/settings:"),
    ]
}

pg = st.navigation(pages)

# Sidebar information
with st.sidebar:
    st.title("🎥 Reddit-to-Shorts")
    st.markdown("Automate your content creation pipeline.")
    st.divider()
    st.info(f"Subreddit: r/{st.session_state.subreddit}\n\nTimeframe: {st.session_state.timeframe}")

# Run the selected page
pg.run()
