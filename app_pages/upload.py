import streamlit as st
import os
import glob
import datetime
from modules.youtube_uploader import YouTubeUploader

st.header("📤 Video Upload & Management")

video_dir = "d:/Automation/data/videos"
if not os.path.exists(video_dir):
    os.makedirs(video_dir)

# List videos
video_files = glob.glob(os.path.join(video_dir, "*.mp4"))

if not video_files:
    st.info("No videos found in the output directory. Go to the 'Generate' page to create one.")
else:
    # Sort by creation time
    video_data = []
    for f in video_files:
        stats = os.stat(f)
        video_data.append({
            "path": f,
            "filename": os.path.basename(f),
            "created": datetime.datetime.fromtimestamp(stats.st_ctime),
            "size_mb": round(stats.st_size / (1024 * 1024), 2)
        })
    
    video_data.sort(key=lambda x: x['created'], reverse=True)
    
    # Highlight the last created video
    latest_video = video_data[0]
    st.success(f"🌟 **Latest Video Created:** {latest_video['filename']} (at {latest_video['created'].strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Selection
    options = [v['filename'] for v in video_data]
    selected_filename = st.selectbox("Select a video to preview or upload", options, index=0)
    selected_video = next(v for v in video_data if v['filename'] == selected_filename)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Preview")
        st.video(selected_video['path'])
        st.write(f"**Created:** {selected_video['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Size:** {selected_video['size_mb']} MB")
        
    with col2:
        st.subheader("YouTube Upload")
        # In a real app, we might store metadata in a DB, here we'll use session state or just defaults
        # If the user just generated it, metadata might be in session_state
        default_title = ""
        default_desc = ""
        
        # Try to load persisted metadata from JSON
        import json
        meta_path = selected_video['path'].replace(".mp4", ".json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    saved_meta = json.load(f)
                    default_title = saved_meta.get('title', '')
                    default_desc = saved_meta.get('description', '')
            except Exception:
                pass
        
        # Fallback to session state if JSON is missing or empty
        if not default_title and st.session_state.get('metadata') and st.session_state.get('current_video') == selected_video['path']:
            default_title = st.session_state.metadata.get('title', selected_video['filename'])
            default_desc = st.session_state.metadata.get('description', '')
        
        if not default_title:
            default_title = selected_video['filename'].replace('.mp4', '').replace('_', ' ')
        
        title = st.text_input("YouTube Title", value=default_title)
        description = st.text_area("YouTube Description", value=default_desc, height=150)
        
        # 1. Tags and Hashtags
        st.markdown("### 🏷️ Optimization & Tags")
        tags_raw = st.text_input("YouTube Tags (Internal)", value="shorts, redditshorts, reddit")
        hashtag_options = ["#shorts", "#redditshorts"]
        selected_hashtags = st.multiselect("Append Hashtags to Title/Description", hashtag_options, default=hashtag_options)
        
        # 2. Audience & 3. Privacy
        col_aud, col_priv = st.columns(2)
        with col_aud:
            st.radio("Audience", ["Not Made for Kids", "Made for Kids"], index=0, help="By default, videos are set to 'Not Made for Kids'.")
        with col_priv:
            privacy = st.selectbox("Privacy Status", ["unlisted", "private", "public"], index=0)
        
        # 4. Scheduling
        st.markdown("### 📅 Scheduling")
        should_schedule = st.checkbox("Schedule this upload?")
        publish_at = None
        if should_schedule:
            col_date, col_time = st.columns(2)
            with col_date:
                sched_date = st.date_input("Publish Date", value=datetime.date.today())
            with col_time:
                sched_time = st.time_input("Publish Time", value=datetime.datetime.now().time())
            
            # combine and format for YouTube: YYYY-MM-DDThh:mm:ssZ
            dt_combined = datetime.datetime.combine(sched_date, sched_time)
            publish_at = dt_combined.strftime('%Y-%m-%dT%H:%M:%SZ')
            st.info(f"Video will be scheduled for: {dt_combined.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")

        if st.button("🚀 Upload to YouTube"):
            # Process title/description with hashtags
            final_title = title
            final_desc = description
            for tag in selected_hashtags:
                if tag not in final_title:
                    final_title = f"{final_title} {tag}"
                if tag not in final_desc:
                    final_desc = f"{final_desc}\n\n{tag}"

            with st.spinner("Uploading to YouTube... Authenticate if prompted."):
                try:
                    # Use credentials from session state if available
                    creds = st.session_state.get('yt_credentials')
                    uploader = YouTubeUploader(credentials=creds)
                    video_id = uploader.upload_video(
                        selected_video['path'],
                        final_title,
                        final_desc,
                        tags=[t.strip() for t in tags_raw.split(',') if t.strip()],
                        privacy_status=privacy,
                        publish_at=publish_at
                    )
                    if video_id:
                        st.balloons()
                        st.success(f"Video uploaded successfully! ID: {video_id}")
                        st.markdown(f"Check it here: https://youtube.com/watch?v={video_id}")
                    else:
                        st.error("Upload failed. Check console for logs.")
                except Exception as e:
                    if "YouTube Data API v3 has not been used" in str(e) or "accessNotConfigured" in str(e):
                        st.error("🚨 **YouTube Data API is disabled!**")
                        st.info("Please go to the **Configuration** page for instructions on how to enable it.")
                    else:
                        st.error(f"Upload failed: {e}")
