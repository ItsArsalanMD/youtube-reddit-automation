import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class ScriptGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        
        # Try a list of model names in order of preference
        model_names = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-3.1-flash-lite-preview",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.0-pro",
            "gemini-pro"
        ]
        
        self.model = None
        for name in model_names:
            try:
                temp_model = genai.GenerativeModel(name)
                # Test with a very small prompt to see if it actually works
                temp_model.generate_content("hi", generation_config={"max_output_tokens": 1})
                self.model = temp_model
                print(f"Successfully initialized with model: {name}")
                break
            except Exception as e:
                print(f"Model {name} failed: {e}")
        
        if not self.model:
            # Last resort: try to find anything that works from list_models
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        try:
                            name = m.name.replace('models/', '')
                            temp_model = genai.GenerativeModel(name)
                            temp_model.generate_content("hi", generation_config={"max_output_tokens": 1})
                            self.model = temp_model
                            print(f"Successfully initialized with listed model: {name}")
                            break
                        except:
                            continue
            except Exception as e:
                print(f"Final fallback failed: {e}")

        if not self.model:
            raise ValueError("Could not find any available Gemini models for this API key.")

    def generate_script(self, title, body):
        prompt = f"""
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
{body}

Return only the narration script.
"""
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_metadata(self, script):
        title_prompt = f"""
Create a viral YouTube Shorts title for a Reddit story.

Rules:
- Maximum 60 characters
- Add curiosity
- Use emoji

Story:
{script}

Return only the title.
"""
        desc_prompt = f"""
Write a YouTube description for a Reddit story video.

Rules:
- 2 short paragraphs
- Include keywords: reddit stories, reddit drama

Story:
{script}

Return only the description.
"""
        title_resp = self.model.generate_content(title_prompt)
        desc_resp = self.model.generate_content(desc_prompt)
        
        return {
            "title": title_resp.text.strip(),
            "description": desc_resp.text.strip()
        }

if __name__ == "__main__":
    # Test generator
    gen = ScriptGenerator()
    test_title = "Am I the jerk for refusing to pay for my sister's wedding?"
    test_body = "So here's what happened. My sister got engaged last month and suddenly expected me to pay for everything because I 'make the most money' in the family. I told her no, and now my entire family says I'm selfish."
    
    script = gen.generate_script(test_title, test_body)
    print(f"Script:\n{script}\n")
    
    metadata = gen.generate_metadata(script)
    print(f"Title: {metadata['title']}")
    print(f"Desc: {metadata['description']}")
