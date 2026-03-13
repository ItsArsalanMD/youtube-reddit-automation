import os
import time
from modules.caption_generator import CaptionGenerator
from modules.video_renderer import VideoRenderer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_full_pipeline():
    # Define paths
    audio_path = "d:/Automation/data/audio/narration.mp3"
    srt_path = "d:/Automation/data/captions/test_refined_captions.srt"
    output_path = "d:/Automation/data/videos/test_refined_output.mp4"
    
    # Ensure assets exist
    if not os.path.exists(audio_path):
        print(f"CRITICAL: Audio file not found at {audio_path}")
        return

    print("--- Starting Refined Video Rendering Test ---")
    start_time = time.time()

    # 1. Generate Refined Captions (Two words per frame)
    print("\n--- Step 1: Generating two-word captions ---")
    caption_gen = CaptionGenerator(model_size="base") # Use base for better word timestamps
    caption_gen.generate_srt(audio_path, srt_path)
    
    if os.path.exists(srt_path):
        print(f"SUCCESS: Captions generated at {srt_path}")
        # Preview first few lines of SRT
        with open(srt_path, 'r', encoding='utf-8') as f:
            print("SRT Preview (First 10 lines):")
            for _ in range(10):
                line = f.readline()
                if not line: break
                print(f"  {line.strip()}")
    else:
        print("FAILED: Caption generation failed.")
        return

    # 2. Render Video (Strip background audio, fix duration)
    print("\n--- Step 1.5: Generating Hook Overlay ---")
    from modules.title_generator import TitleGenerator
    title_gen = TitleGenerator()
    overlay_path = "d:/Automation/data/overlays/test_overlay.png"
    title_gen.generate_title_image("AITA for refusing to pay for my sister's extravagant destination wedding even though I make good money?", overlay_path)
    
    print("\n--- Step 2: Rendering video with overlay and audio stripping ---")
    renderer = VideoRenderer(background_video="d:/Automation/assets/minecraft_parkour.mp4")
    success = renderer.render_video(audio_path, srt_path, output_path, overlay_path=overlay_path)
    
    if success:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"\n--- SUCCESS ---")
        print(f"Video rendered to: {output_path}")
        print(f"Total time taken: {elapsed:.2f} seconds")
    else:
        print(f"\n--- FAILED ---")
        print("Video rendering failed.")

if __name__ == "__main__":
    test_full_pipeline()
