import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

class TitleGenerator:
    def __init__(self):
        # Attempt to load a bold font like Arial Bold, fallback to default
        try:
            self.title_font = ImageFont.truetype("arialbd.ttf", 46)
            self.sub_font = ImageFont.truetype("arialbd.ttf", 24)
            self.user_font = ImageFont.truetype("arial.ttf", 22)
            self.meta_font = ImageFont.truetype("arialbd.ttf", 22)
        except IOError:
            print("Warning: Arial Bold not found. Using default font.")
            self.title_font = ImageFont.load_default()
            self.sub_font = ImageFont.load_default()
            self.user_font = ImageFont.load_default()
            self.meta_font = ImageFont.load_default()

    def create_rounded_rectangle(self, draw, xy, corner_radius, fill=None, outline=None):
        upper_left_point = xy[0]
        bottom_right_point = xy[1]
        draw.rounded_rectangle(
            (upper_left_point, bottom_right_point),
            radius=corner_radius,
            fill=fill,
            outline=outline
        )

    def generate_title_image(self, title, output_path, subreddit="r/AmItheAsshole", author="u/throwaway123"):
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Image dimensions suitable for centered overlay on 1080p
        width, height = 900, 500
        
        # Create transparent canvas
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Word wrap the title
        wrapper = textwrap.TextWrapper(width=34) # Adjust width based on font size
        wrapped_title = wrapper.fill(text=title)
        
        # Calculate bounding box for text to dynamically size the background box
        # Using multiline_bbox if available, else simple math
        try:
            bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=self.title_font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older PIL
            text_w, text_h = draw.multiline_textsize(wrapped_title, font=self.title_font)

        # Base padding
        pad_x = 50
        pad_y = 40
        
        # Header heights (avatar, subreddit, author)
        header_h = 60
        # Footer heights (upvote icons etc)
        footer_h = 60

        box_w = width - 40 # Max width with 20px padding on sides
        box_h = pad_y * 2 + text_h + header_h + footer_h + 30 # Extra 30px spacing

        # Center the box vertically and horizontally
        x1 = (width - box_w) // 2
        y1 = (height - box_h) // 2
        x2 = x1 + box_w
        y2 = y1 + box_h

        # Draw main dark-mode Reddit container
        self.create_rounded_rectangle(draw, [(x1, y1), (x2, y2)], corner_radius=25, fill=(30, 30, 30, 240)) # Slightly transparent dark grey
        
        # --- Draw Header ---
        current_y = y1 + pad_y
        current_x = x1 + pad_x

        # Draw fake avatar circle
        avatar_r = 20
        draw.ellipse((current_x, current_y, current_x + avatar_r*2, current_y + avatar_r*2), fill=(255, 69, 0)) # Reddit Orange

        header_text_x = current_x + avatar_r*2 + 15
        
        # Subreddit Name
        draw.text((header_text_x, current_y), subreddit, font=self.sub_font, fill=(255, 255, 255))
        
        # Author Name
        draw.text((header_text_x, current_y + 28), f"{author} • 5h", font=self.user_font, fill=(150, 150, 150))
        
        # --- Draw Title ---
        title_y = current_y + header_h + 20
        draw.multiline_text((x1 + pad_x, title_y), wrapped_title, font=self.title_font, fill=(240, 240, 240), spacing=10)

        # --- Draw Footer (Fake Upvotes/Comments) ---
        footer_y = title_y + text_h + 30
        
        # Upvote button simulation
        draw.polygon([(x1 + pad_x, footer_y + 15), (x1 + pad_x + 10, footer_y), (x1 + pad_x + 20, footer_y + 15)], fill=(255, 69, 0)) # Up arrow
        draw.text((x1 + pad_x + 30, footer_y - 2), "14.2k", font=self.meta_font, fill=(255, 69, 0))
        draw.polygon([(x1 + pad_x + 95, footer_y), (x1 + pad_x + 105, footer_y + 15), (x1 + pad_x + 115, footer_y)], fill=(150, 150, 150)) # Down arrow
        
        # Comments icon simulation
        c_x = x1 + pad_x + 160
        draw.rounded_rectangle([(c_x, footer_y + 2), (c_x + 20, footer_y + 16)], radius=4, outline=(150, 150, 150), width=2)
        draw.text((c_x + 30, footer_y - 2), "405", font=self.meta_font, fill=(150, 150, 150))

        # Save the image
        img.save(output_path, "PNG")
        return output_path

if __name__ == "__main__":
    test_title = "AITA for refusing to pay for my sister's extravagant destination wedding even though I make good money?"
    generator = TitleGenerator()
    out_path = "d:/Automation/data/overlays/test_overlay_direct.png"
    out = generator.generate_title_image(test_title, out_path)
    print(f"Test overlay generated at: {out}")
