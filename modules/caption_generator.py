import whisper
import os
from datetime import timedelta

class CaptionGenerator:
    def __init__(self, model_size="tiny"):
        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)

    def generate_srt(self, audio_path, output_path):
        """
        Transcribes audio and saves results as an SRT file with two words per frame.
        """
        # If FFMPEG_PATH is set, ensure it's in the PATH for whisper
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        if ffmpeg_path:
            os.environ["PATH"] += os.pathsep + ffmpeg_path

        print(f"Transcribing {audio_path}...")
        # Use word_timestamps=True for granular control
        result = self.model.transcribe(audio_path, verbose=False, word_timestamps=True)
        
        segments = result.get("segments", [])
        all_words = []
        for segment in segments:
            all_words.extend(segment.get("words", []))

        with open(output_path, "w", encoding="utf-8") as f:
            for i in range(0, len(all_words), 2):
                chunk = all_words[i:i+2]
                if not chunk:
                    break
                    
                start_time = chunk[0]["start"]
                end_time = chunk[-1]["end"]
                text = " ".join([w["word"].strip() for w in chunk])
                
                f.write(f"{(i // 2) + 1}\n")
                f.write(f"{self._format_timestamp(start_time)} --> {self._format_timestamp(end_time)}\n")
                f.write(f"{text}\n\n")
        
        return output_path

    def _format_timestamp(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int(td.microseconds / 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

if __name__ == "__main__":
    # Test generator
    # Requires a test audio file to exist
    audio_file = "d:/Automation/data/audio/test_narration.mp3"
    output_srt = "d:/Automation/data/captions/test_captions.srt"
    
    if os.path.exists(audio_file):
        os.makedirs(os.path.dirname(output_srt), exist_ok=True)
        gen = CaptionGenerator()
        gen.generate_srt(audio_file, output_srt)
        print(f"Captions saved to {output_srt}")
    else:
        print(f"Test audio file not found at {audio_file}. Run tts_generator.py first.")
