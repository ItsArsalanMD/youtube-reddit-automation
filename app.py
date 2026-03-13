import streamlit as st
import os
import asyncio
from modules.reddit_fetcher import RedditFetcher
from modules.script_generator import ScriptGenerator
from modules.tts_generator import run_tts
from modules.caption_generator import CaptionGenerator
from modules.video_renderer import VideoRenderer
from modules.title_generator import TitleGenerator
from modules.youtube_uploader import YouTubeUploader
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Reddit-to-Shorts Automation", layout="wide")

st.title("🎥 Reddit-to-Shorts Automation")
st.markdown("Generate viral YouTube Shorts from Reddit stories automatically.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    subreddit = st.text_input("Subreddit", value="AmItheAsshole")
    timeframe = st.selectbox("Timeframe", ["day", "week", "month", "all"], index=0)
    limit = st.slider("Posts to fetch", 1, 50, 10)
    
    st.divider()
    st.info("Ensure your .env file is configured with API keys.")

# Initialize session state
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

# 1. Fetch Posts
if st.button("🔍 Fetch Top Posts"):
    with st.spinner(f"Fetching posts from r/{subreddit}..."):
        fetcher = RedditFetcher()
        st.session_state.posts = fetcher.fetch_top_posts(subreddit, limit=limit, timeframe=timeframe)
        st.success(f"Found {len(st.session_state.posts)} text posts.")

# 2. Display Posts
if st.session_state.posts:
    post_titles = [f"{p['score']} | {p['title'][:50]}..." for p in st.session_state.posts]
    selected_idx = st.selectbox("Select a post to process", range(len(post_titles)), format_func=lambda i: post_titles[i])
    st.session_state.selected_post = st.session_state.posts[selected_idx]
    
    st.markdown(f"### Selected: {st.session_state.selected_post['title']}")
    with st.expander("Show Post Body"):
        st.write(st.session_state.selected_post['body'])

# 3. Generate Script
if st.session_state.selected_post:
    if st.button("📝 Generate Script & Metadata"):
        with st.spinner("Generating script with Gemini..."):
            gen = ScriptGenerator()
            st.session_state.script = gen.generate_script(
                st.session_state.selected_post['title'], 
                st.session_state.selected_post['body']
            )
            st.session_state.metadata = gen.generate_metadata(st.session_state.script)
            
            # Extract first sentence for visual hook
            import re
            sentences = re.split(r'(?<=[.!?]) +', st.session_state.script)
            if sentences:
                st.session_state.visual_hook_title = sentences[0].strip()
            
            st.success("Script and Metadata generated!")

if st.session_state.script:
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Edit Script")
        st.session_state.script = st.text_area("Narration Script", value=st.session_state.script, height=300)
    
    with col2:
        st.subheader("YouTube Metadata")
        st.session_state.metadata['title'] = st.text_input("YouTube Title (Marketing)", value=st.session_state.metadata['title'])
        st.session_state.visual_hook_title = st.text_input("Visual Hook Title (On-screen)", value=st.session_state.visual_hook_title)
        st.session_state.metadata['description'] = st.text_area("Description", value=st.session_state.metadata['description'], height=150)

# 4. Render Video
if st.session_state.script:
    if st.button("🎬 Render Final Video"):
        with st.spinner("Processing... This involves TTS, Captions, and FFmpeg rendering."):
            # Paths
            base_dir = "d:/Automation/data"
            
            import re
            raw_title = st.session_state.metadata.get('title', 'final_short')
            safe_title = re.sub(r'[^\w\-_\. ]', '', raw_title).strip().replace(' ', '_')
            if not safe_title:
                safe_title = "final_short"
                
            audio_path = os.path.join(base_dir, "audio", f"{safe_title}.mp3")
            srt_path = os.path.join(base_dir, "captions", f"{safe_title}.srt")
            script_path = os.path.join(base_dir, "scripts", f"{safe_title}.txt")
            video_path = os.path.join(base_dir, "videos", f"{safe_title}.mp4")
            
            # Save the script text as well for reference
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.script)
            
            # Step A: TTS
            st.write("Step 1/3: Generating Narration...")
            run_tts(st.session_state.script, audio_path)
            
            # Step B: Captions
            st.write("Step 2/3: Generating Captions...")
            cap_gen = CaptionGenerator(model_size="base")
            cap_gen.generate_srt(audio_path, srt_path)
            
            # Step B2: Title Overlay
            st.write("Step 2.5/3: Generating Hook Overlay...")
            title_gen = TitleGenerator()
            overlay_path = os.path.join(base_dir, "overlays", f"{safe_title}.png")
            title_gen.generate_title_image(st.session_state.visual_hook_title, overlay_path, subreddit=f"r/{subreddit}")
            
            # Step C: Render
            st.write("Step 3/3: Rendering Video (FFmpeg)...")
            
            # Pick a random background video from assets
            import random
            import glob
            assets_dir = "d:/Automation/assets"
            mp4_files = glob.glob(os.path.join(assets_dir, "*.mp4"))
            
            if mp4_files:
                random_bg = random.choice(mp4_files)
                st.write(f"Using background: {os.path.basename(random_bg)}")
                renderer = VideoRenderer(background_video=random_bg)
            else:
                st.warning("No .mp4 files found in 'assets/'. Using placeholder.")
                renderer = VideoRenderer(background_video="d:/Automation/assets/placeholder.mp4")
                
            success = renderer.render_video(audio_path, srt_path, video_path, overlay_path=overlay_path)
            
            if success:
                st.session_state.video_ready = True
                st.session_state.current_video = video_path
                st.success("Video Rendered Successfully!")
            else:
                st.error("Video Rendering Failed. Check console for FFmpeg logs.")

# 5. Preview and Upload
if st.session_state.video_ready:
    st.divider()
    st.subheader("Final Preview")
    st.video(st.session_state.current_video)
    
    if st.button("🚀 Upload to YouTube"):
        with st.spinner("Uploading... Authenticate in the browser if prompted."):
            uploader = YouTubeUploader()
            video_id = uploader.upload_video(
                st.session_state.current_video,
                st.session_state.metadata['title'],
                st.session_state.metadata['description'],
                tags=["reddit", "shorts", "story"],
                privacy_status="private" # Default to private for safety
            )
            if video_id:
                st.balloons()
                st.success(f"Video uploaded successfully! ID: {video_id}")
                st.markdown(f"Check it here: https://youtube.com/watch?v={video_id}")
