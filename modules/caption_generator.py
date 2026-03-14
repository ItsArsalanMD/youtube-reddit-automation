import whisper
import os
from modules.config import DATA_DIR
from datetime import timedelta

class CaptionGenerator:
    def __init__(self, model_size="tiny"):
        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)

    def generate_subtitle_file(self, audio_path, output_path, format="ass", font_name="Arial"):
        """
        Transcribes audio and saves results as either SRT or ASS file.
        ASS format supports the 'spring' animation effect.
        """
        ffmpeg_path = os.getenv("FFMPEG_PATH")
        if ffmpeg_path:
            os.environ["PATH"] += os.pathsep + ffmpeg_path

        print(f"Transcribing {audio_path}...")
        result = self.model.transcribe(audio_path, verbose=False, word_timestamps=True)
        
        segments = result.get("segments", [])
        all_words = []
        for segment in segments:
            all_words.extend(segment.get("words", []))

        if format == "ass":
            self._write_ass(all_words, output_path, font_name=font_name)
        else:
            self._write_srt(all_words, output_path)
        
        return output_path

    def _write_ass(self, words, output_path, font_name="Arial"):
        """Writes Advanced Substation Alpha (ASS) file with spring animation."""
        header = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,{font_name},80,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,2,5,10,10,10,1"
        ]
        
        events = [
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        import re
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(header) + "\n")
            f.write("\n".join(events) + "\n")
            
            for word_info in words:
                text = word_info["word"].strip().upper()
                text = re.sub(r'[.,]', '', text)
                
                if not text:
                    continue

                start_v = word_info["start"]
                end_v = word_info["end"]
                
                # Ensure visibility by having at least 0.1s duration
                if end_v < start_v + 0.1:
                    end_v = start_v + 0.1
                
                start = self._format_timestamp_ass(start_v)
                end = self._format_timestamp_ass(end_v)
                
                # Spring Animation: Scale 80% -> 120% -> 100%
                # \t(start, end, acceleration, tags)
                anim = r"{\fscx80\fscy80\t(0,100,\fscx120\fscy120)\t(100,200,\fscx100\fscy100)}"
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{anim}{text}\n")

    def _write_srt(self, words, output_path):
        """Writes standard SRT file with one word per segment."""
        import re
        with open(output_path, "w", encoding="utf-8") as f:
            for i, word_info in enumerate(words):
                text = word_info["word"].strip()
                text = re.sub(r'[.,]', '', text)
                
                if not text:
                    continue

                start_v = word_info["start"]
                end_v = word_info["end"]
                
                if end_v < start_v + 0.1:
                    end_v = start_v + 0.1

                start = self._format_timestamp(start_v)
                end = self._format_timestamp(end_v)
                
                f.write(f"{i + 1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    def _format_timestamp(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int(td.microseconds / 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def _format_timestamp_ass(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        centis = int(td.microseconds / 10000)
        return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"

if __name__ == "__main__":
    # Test generator
    # Requires a test audio file to exist
    audio_file = os.path.join(DATA_DIR, "audio", "test_narration.mp3")
    output_srt = os.path.join(DATA_DIR, "captions", "test_captions.srt")
    
    if os.path.exists(audio_file):
        os.makedirs(os.path.dirname(output_srt), exist_ok=True)
        gen = CaptionGenerator()
        gen.generate_subtitle_file(audio_file, output_srt, format="srt")
        print(f"Captions saved to {output_srt}")
    else:
        print(f"Test audio file not found at {audio_file}. Run tts_generator.py first.")
