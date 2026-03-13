# SPEC-1-YouTube-Reddit-Automation-MVP

## Background

The goal is to build a local desktop application that automatically generates Reddit story videos for YouTube Shorts using only free tools and APIs. The user cannot run large AI models locally, so the system will rely on lightweight scripts and free services.

The workflow:

1. Fetch a Reddit story
2. Convert it into a short narration script
3. Generate voice narration
4. Generate subtitles
5. Combine narration with Minecraft parkour background footage
6. Render a YouTube Shorts video
7. Allow user review
8. Upload to YouTube

Target output: 1–2 Reddit story Shorts per day.

---

## Requirements

### Must Have

* Fetch Reddit posts automatically
* Convert post to short-form script
* Generate narration using free TTS
* Generate captions
* Combine video + captions + narration
* Export vertical video (1080x1920)
* Manual review before upload
* Upload using YouTube API

### Should Have

* Auto-generate title
* Auto-generate description
* Auto-generate tags

### Could Have

* Thumbnail generator
* Multiple subreddit support

### Won't Have (MVP)

* Local LLM models
* Paid AI APIs
* Cloud infrastructure

---

## Method

### High Level Architecture

User -> Desktop App UI -> Reddit Fetcher -> Script Generator -> TTS Generator -> Caption Generator -> Video Renderer -> Review UI -> YouTube Upload

### Components

#### 1. Reddit Fetcher

Library: PRAW

Responsibilities:

* Fetch top posts from selected subreddits
* Filter posts with high engagement

Example data structure:

```
Post {
 id
 title
 body
 subreddit
 score
}
```

Filtering:

* score > 500
* text length > 200

---

#### 2. Script Generator

Purpose: Convert Reddit story into a narration-friendly script (~120 words).

Prompt Template:

```
You are writing scripts for viral YouTube Shorts.

Turn the following Reddit post into a short engaging narration.

Rules:
- Maximum 120 words
- Hook in first sentence
- Conversational tone
- Keep suspense
- End with a question

Reddit Title:
{title}

Reddit Post:
{post}

Return only the narration script.
```

Output example:

```
Reddit user asks:

Am I the jerk for refusing to pay for my sister's wedding?

So here's what happened.

My sister got engaged last month and suddenly expected me to pay for everything...

Now my entire family says I'm selfish.

Am I actually the bad guy here?
```

---

#### 3. Title Generator

Prompt Template:

```
Create a viral YouTube Shorts title for a Reddit story.

Rules:
- Maximum 60 characters
- Add curiosity
- Use emoji

Story:
{script}

Return only the title.
```

Example:

```
I Refused To Pay For My Sister's Wedding 😳
```

---

#### 4. Description Generator

Prompt Template:

```
Write a YouTube description for a Reddit story video.

Rules:
- 2 short paragraphs
- Include keywords: reddit stories, reddit drama

Story:
{script}
```

---

#### 5. Voice Generator

Library: edge-tts

Voice:

```
en-US-GuyNeural
```

Output:

```
audio/narration.mp3
```

---

#### 6. Caption Generator

Approach: Convert script directly to SRT timestamps.

Example:

```
1
00:00:00,000 --> 00:00:03,000
Reddit user asks

2
00:00:03,000 --> 00:00:07,000
Am I the jerk for refusing
```

Alternative:

Whisper timestamp generation.

---

#### 7. Video Renderer

Tool: FFmpeg

Assets:

```
assets/minecraft_parkour.mp4
audio/narration.mp3
captions/captions.srt
```

Command:

```
ffmpeg -stream_loop -1 -i minecraft.mp4 \\
-i narration.mp3 \\
-vf "scale=1080:1920,subtitles=captions.srt" \\
-shortest output.mp4
```

Output:

```
videos/final_video.mp4
```

---

#### 8. Review UI

Framework: Streamlit

Features:

* Display script
* Play narration audio
* Preview video
* Edit script
* Regenerate video
* Approve upload

---

#### 9. YouTube Upload

Library: google-api-python-client

Upload metadata:

```
title
description
tags
category
```

Authentication:

OAuth login.

---

## Implementation

Project Structure

```
youtube-automation/

app.py

modules/
 reddit_fetcher.py
 script_generator.py
 tts_generator.py
 caption_generator.py
 video_renderer.py
 youtube_uploader.py

assets/
 minecraft_parkour.mp4

data/
 scripts/
 audio/
 captions/
 videos/
```

Pipeline:

1. Fetch Reddit post
2. Generate script
3. Generate title and description
4. Generate narration
5. Generate captions
6. Render video
7. Show preview
8. Upload to YouTube

---

## Milestones

Milestone 1

Reddit fetcher working.

Milestone 2

Script generation pipeline.

Milestone 3

TTS generation.

Milestone 4

Video rendering pipeline.

Milestone 5

Streamlit UI.

Milestone 6

YouTube upload automation.

---

## Gathering Results

Measure success using:

* Video generation time (<2 minutes)
* Successful YouTube uploads
* 1–2 videos produced daily

Possible improvements after MVP:

* automated thumbnail generation
* multi-channel posting
* TikTok export
* automatic scheduling

