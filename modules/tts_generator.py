import asyncio
import edge_tts
import os
from modules.config import DATA_DIR
import re
import subprocess
import tempfile
import shutil

class TTSGenerator:
    def __init__(self, voice="en-US-GuyNeural", rate="+20%"):
        self.voice = voice
        self.rate = rate

    async def generate_audio(self, text, output_path):
        """
        Generates audio for the entire text at once for stable and natural pacing.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(output_path)
        return output_path
            
        return output_path

def run_tts(text, output_path, voice="en-US-GuyNeural", rate="+20%"):
    """
    Sync wrapper for the async generate_audio function.
    """
    generator = TTSGenerator(voice, rate)
    asyncio.run(generator.generate_audio(text, output_path))
    return output_path

if __name__ == "__main__":
    # Test generator
    test_text = "So here's what happened. My sister got engaged last month and suddenly expected me to pay for everything."
    test_output = os.path.join(DATA_DIR, "audio", "test_narration.mp3")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(test_output), exist_ok=True)
    
    run_tts(test_text, test_output)
    print(f"Audio saved to {test_output}")
