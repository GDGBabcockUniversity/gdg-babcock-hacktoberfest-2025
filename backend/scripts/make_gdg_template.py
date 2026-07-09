"""
One-off script to generate placeholder GDG-branded certificate templates.

Produces templates/gdg_participation_template.png and
templates/gdg_completion_template.png at the same pixel dimensions as the
existing Hacktoberfest templates, so generator.py's hardcoded text
coordinates still land correctly. Replace these with real designed
templates when available — this script only exists to unblock the
generic-template code path.

Run from the backend/ directory: python3 scripts/make_gdg_template.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SIZE = (842, 595)

GDG_BLUE = (66, 133, 244)
GDG_RED = (234, 67, 53)
GDG_YELLOW = (251, 188, 5)
GDG_GREEN = (52, 168, 83)
BORDER = 18


def make_template(title_text, output_filename):
    img = Image.new("RGBA", SIZE, (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Four-color border band, GDG-style
    band_width = SIZE[0] // 4
    colors = [GDG_BLUE, GDG_RED, GDG_YELLOW, GDG_GREEN]
    for i, color in enumerate(colors):
        draw.rectangle(
            [i * band_width, 0, (i + 1) * band_width, BORDER], fill=color
        )
    draw.rectangle([0, 0, BORDER, SIZE[1]], fill=GDG_BLUE)
    draw.rectangle([SIZE[0] - BORDER, 0, SIZE[0], SIZE[1]], fill=GDG_RED)
    draw.rectangle([0, SIZE[1] - BORDER, SIZE[0], SIZE[1]], fill=GDG_GREEN)

    try:
        title_font = ImageFont.truetype(
            os.path.join(BASE_DIR, "fonts", "GoogleSans-Bold.ttf"), 32
        )
    except IOError:
        title_font = ImageFont.load_default()

    draw.text((45, 60), "GDG BABCOCK", font=title_font, fill=(26, 26, 26))
    draw.text((45, 110), title_text, font=title_font, fill=(90, 90, 90))

    img.convert("RGB").save(os.path.join(TEMPLATES_DIR, output_filename), "PNG")
    print(f"Wrote {output_filename}")


if __name__ == "__main__":
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    make_template("Certificate of Participation", "gdg_participation_template.png")
    make_template("Certificate of Completion", "gdg_completion_template.png")
