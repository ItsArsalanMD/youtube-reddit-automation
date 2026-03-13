import subprocess
import os
import random

class VideoRenderer:
    def __init__(self, background_video="d:/Automation/assets/minecraft_parkour.mp4"):
        self.background_video = background_video

    def get_video_duration(self, video_path):
        """
        Gets the duration of a video file using ffprobe.
        """
        ffprobe_bin = "ffprobe"
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        if ffmpeg_path:
            ffprobe_bin = os.path.join(ffmpeg_path, "ffprobe.exe")

        command = [
            ffprobe_bin, '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None

    def get_video_dimensions(self, video_path):
        """
        Gets the dimensions of a video file using ffprobe.
        """
        ffprobe_bin = "ffprobe"
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        if ffmpeg_path:
            ffprobe_bin = os.path.join(ffmpeg_path, "ffprobe.exe")

        command = [
            ffprobe_bin, '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0', video_path
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            w_h = result.stdout.strip().split('x')
            return int(w_h[0]), int(w_h[1])
        except Exception as e:
            print(f"Error getting video dimensions: {e}")
            return None, None

    def render_video(self, audio_path, srt_path, output_path, overlay_path=None):
        """
        Renders the final video using FFmpeg, optionally adding an image overlay.
        """
        # Get audio duration first for the -t flag
        audio_duration = self.get_video_duration(audio_path)
        if not audio_duration:
            print("Could not determine audio duration. Using default 60s.")
            audio_duration = 60

        # Base inputs
        input_args = []
        if not os.path.exists(self.background_video):
            # Create a placeholder if not exists (solid color)
            print(f"Background video {self.background_video} not found. Using placeholder.")
            input_args.extend(['-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:d=600']) # 10 min placeholder
            # Base video is stream [0:v]
            vf_base = "scale=1080:1920[bg]"
        else:
            # Pick a random start time
            duration = self.get_video_duration(self.background_video)
            start_time = 0
            if duration is not None and audio_duration is not None and duration > 60:
                max_start = max(0.0, float(duration) - (float(audio_duration) + 5.0))
                start_time = random.uniform(0.0, max_start)
                print(f"Long-form video detected ({duration:.2f}s). Picking random start at {start_time:.2f}s")
            
            # Using -stream_loop -1 to repeat if background is too short
            input_args.extend(['-ss', str(start_time), '-stream_loop', '-1', '-i', self.background_video])
            
            # Auto-crop if horizontal
            w, h = self.get_video_dimensions(self.background_video)
            if w and h and w > h:
                required_w = int(h * (9/16))
                print(f"Horizontal video detected ({w}x{h}). Auto-cropping to {required_w}x{h} (9:16).")
                vf_base = f"crop={required_w}:{h}:(iw-{required_w})/2:0,scale=1080:1920[bg]"
            else:
                vf_base = "scale=1080:1920[bg]"

        input_args.extend(['-i', audio_path])
        
        # Build complex filter
        filter_complex = [vf_base]
        escaped_srt = srt_path.replace("\\", "/").replace(":", "\\:")
        sub_filter = f"[bg]subtitles='{escaped_srt}':force_style='Alignment=10,FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1.5,Bold=1'[sub_out]"
        
        if overlay_path and os.path.exists(overlay_path):
            input_args.extend(['-i', overlay_path])
            # The background is [0:v], audio is [1:a], overlay is [2:v]
            # Overlay [2:v] on top of [sub_out] 
            filter_complex.append(sub_filter)
            filter_complex.append(f"[sub_out][2:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,3)'[final_v]")
        else:
            # Route [sub_out] directly to output
            sub_filter = sub_filter.replace("[sub_out]", "[final_v]")
            filter_complex.append(sub_filter)

        ffmpeg_bin = "ffmpeg"
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        if ffmpeg_path:
            ffmpeg_bin = os.path.join(ffmpeg_path, "ffmpeg.exe")

        command = [
            ffmpeg_bin, '-y'
        ] + input_args + [
            '-filter_complex', ";".join(filter_complex),
            '-map', '[final_v]',   # Mapped video stream
            '-map', '1:a:0',       # Fixed audio index (it's always second input)
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-c:a', 'aac',
            '-t', f"{audio_duration:.3f}",
            output_path
        ]
        
        print(f"Running FFmpeg: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg Error: {result.stderr}")
            return False
        
        return True

if __name__ == "__main__":
    # Test renderer
    audio = "d:/Automation/data/audio/test_narration.mp3"
    srt = "d:/Automation/data/captions/test_captions.srt"
    output = "d:/Automation/data/videos/test_output.mp4"
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    renderer = VideoRenderer()
    success = renderer.render_video(audio, srt, output)
    if success:
        print(f"Video rendered successfully: {output}")
    else:
        print("Video rendering failed.")
