import streamlit as st
import os
import re
import glob
import random
from modules.reddit_fetcher import RedditFetcher
from modules.script_generator import ScriptGenerator
from modules.tts_generator import run_tts
from modules.caption_generator import CaptionGenerator
from modules.video_renderer import VideoRenderer
from modules.title_generator import TitleGenerator

st.header("🎬 Video Generation")

# 1. Fetch Posts
if st.button("🔍 Fetch Top Posts"):
    subreddit = st.session_state.get('subreddit', 'AmItheAsshole')
    limit = st.session_state.get('limit', 10)
    timeframe = st.session_state.get('timeframe', 'day')
    
    with st.spinner(f"Fetching posts from r/{subreddit}..."):
        fetcher = RedditFetcher()
        st.session_state.posts = fetcher.fetch_top_posts(subreddit, limit=limit, timeframe=timeframe)
        st.success(f"Found {len(st.session_state.posts)} text posts.")

# 2. Display Posts
if st.session_state.get('posts'):
    post_titles = [f"{p['score']} | {p['title'][:50]}..." for p in st.session_state.posts]
    selected_idx = st.selectbox("Select a post to process", range(len(post_titles)), format_func=lambda i: post_titles[i], key="post_selector")
    st.session_state.selected_post = st.session_state.posts[selected_idx]
    
    st.markdown(f"### Selected: {st.session_state.selected_post['title']}")
    with st.expander("Show Post Body"):
        st.write(st.session_state.selected_post['body'])

# 3. Generate Script
if st.session_state.get('selected_post'):
    if st.button("📝 Generate Script & Metadata"):
        with st.spinner("Generating script with Gemini..."):
            gen = ScriptGenerator()
            st.session_state.script = gen.generate_script(
                st.session_state.selected_post['title'], 
                st.session_state.selected_post['body']
            )
            st.session_state.metadata = gen.generate_metadata(st.session_state.script)
            
            # Extract first sentence for visual hook
            sentences = re.split(r'(?<=[.!?]) +', st.session_state.script)
            if sentences:
                st.session_state.visual_hook_title = sentences[0].strip()
            
            st.success("Script and Metadata generated!")

if st.session_state.get('script'):
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
if st.session_state.get('script'):
    if st.button("🚀 Render Final Video"):
        with st.spinner("Processing... This involves TTS, Captions, and FFmpeg rendering."):
            base_dir = "d:/Automation/data"
            
            raw_title = st.session_state.metadata.get('title', 'final_short')
            safe_title = re.sub(r'[^\w\-_\. ]', '', raw_title).strip().replace(' ', '_')
            if not safe_title:
                safe_title = "final_short"
                
            audio_dir = os.path.join(base_dir, "audio")
            captions_dir = os.path.join(base_dir, "captions")
            scripts_dir = os.path.join(base_dir, "scripts")
            videos_dir = os.path.join(base_dir, "videos")
            overlays_dir = os.path.join(base_dir, "overlays")
            
            for d in [audio_dir, captions_dir, scripts_dir, videos_dir, overlays_dir]:
                os.makedirs(d, exist_ok=True)

            audio_path = os.path.join(audio_dir, f"{safe_title}.mp3")
            ass_path = os.path.join(captions_dir, f"{safe_title}.ass")
            script_path = os.path.join(scripts_dir, f"{safe_title}.txt")
            video_path = os.path.join(videos_dir, f"{safe_title}.mp4")
            overlay_path = os.path.join(overlays_dir, f"{safe_title}.png")
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.script)
            
            # Save metadata for the upload page
            import json
            meta_path = video_path.replace(".mp4", ".json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(st.session_state.metadata, f, indent=4)
            
            # Step A: TTS
            st.write("Step 1/3: Generating Narration...")
            run_tts(st.session_state.script, audio_path)
            
            # Step B: Captions
            st.write("Step 2/3: Generating Word-Level Animated Captions...")
            renderer = VideoRenderer()
            actual_font, _ = renderer._get_font_info("Titan One")
            
            cap_gen = CaptionGenerator(model_size="base")
            cap_gen.generate_subtitle_file(audio_path, ass_path, format="ass", font_name=actual_font)
            
            # Step B2: Title Overlay
            st.write("Step 2.5/3: Generating Hook Overlay...")
            title_gen = TitleGenerator()
            subreddit_label = f"r/{st.session_state.get('subreddit', 'Reddit')}"
            title_gen.generate_title_image(st.session_state.visual_hook_title, overlay_path, subreddit=subreddit_label)
            
            # Step C: Render
            st.write("Step 3/3: Rendering Video (FFmpeg)...")
            
            assets_dir = "d:/Automation/assets"
            mp4_files = glob.glob(os.path.join(assets_dir, "*.mp4"))
            
            if mp4_files:
                renderer.background_video = random.choice(mp4_files)
            else:
                renderer.background_video = "d:/Automation/assets/placeholder.mp4"
                
            success = renderer.render_video(audio_path, ass_path, video_path, overlay_path=overlay_path, font_name=actual_font)
            
            if success:
                st.session_state.video_ready = True
                st.session_state.current_video = video_path
                st.success("Video Rendered Successfully!")
                st.video(video_path)
            else:
                st.error("Video Rendering Failed. Check console for FFmpeg logs.")
