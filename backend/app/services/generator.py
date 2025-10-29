from PIL import Image, ImageDraw, ImageFont
import os
from ..models.certificates import CertificateBase

def generate_certificate_from_model(cert_data: CertificateBase, output_path="certificate.png"):
    # Now you can access cert_data.name, cert_data.event, cert_data.date
    return generate_certificate(cert_data.participant_name, cert_data.event_name, cert_data.date_issued, output_path)

def generate_certificate(name, event, date, output_path="certificate.png", certificate_type="participation"):
    """
    Generate a certificate by overlaying text on a predefined template image.
    
    Args:
        name: Participant's full name
        event: Event name
        date: Date in format YYYY-MM-DD or display format
        output_path: Where to save the generated certificate
        certificate_type: "participation" or "completion" to select template
    
    Returns:
        output_path: Path to the generated certificate
    """
    # Debug: show where it will save
    print("Saving certificate at:", os.path.abspath(output_path))
    
    # Determine template path based on certificate type
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Get backend root
    if certificate_type == "completion":
        template_path = os.path.join(base_dir, "templates", "completion_template.png")
    else:  # default to participation
        template_path = os.path.join(base_dir, "templates", "participation_template.png")
    
    # Verify template exists
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Certificate template not found at: {template_path}")
    
    # Load the template image
    certificate = Image.open(template_path)
    draw = ImageDraw.Draw(certificate)
    
    # Get image dimensions
    width, height = certificate.size
    
    # Load Google Sans fonts
    fonts_dir = os.path.join(base_dir, "fonts")
    try:
        # Font sizes based on Figma specifications
        font_name = ImageFont.truetype(os.path.join(fonts_dir, "GoogleSans-Bold.ttf"), 39)  # 29.07pt ≈ 39px
        font_event = ImageFont.truetype(os.path.join(fonts_dir, "GoogleSans-Bold.ttf"), 22)  # 16.15pt ≈ 22px
        font_date = ImageFont.truetype(os.path.join(fonts_dir, "GoogleSans-Bold.ttf"), 15)  # 16px
        font_small = ImageFont.truetype(os.path.join(fonts_dir, "GoogleSans-Regular.ttf"), 24)
    except IOError as e:
        print(f"⚠️ Error loading Google Sans fonts: {e}")
        print("Using fallback fonts...")
        # Fallback to default if Google Sans not found
        font_name = ImageFont.load_default()
        font_event = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Helper function to center text horizontally
    def center_text(text, y, font, color="#000000"):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)
    
    # Helper function to draw text at specific position (left-aligned)
    def draw_text_at(text, x, y, font, color="#000000"):
        draw.text((x, y), text, font=font, fill=color)
    
    # Text color - dark for visibility on light background
    text_color = "#1a1a1a"
    
    # Position text based on Figma coordinates
    # These coordinates match the official GDG certificate templates
    
    # Participant Name - X: 45, Y: 279 (moved 1px up)
    # Font: Google Sans Bold, 29.07pt (≈39px)
    draw_text_at(name, 45, 279, font_name, text_color)
    
    # Event Name - X: 46, Y: 354, W: 148, H: 22
    # Font: Google Sans Bold, 16.15pt (≈22px)
    draw_text_at(event, 46, 354, font_event, text_color)
    
    # Date - X: 160, Y: 380 (moved 1px up, size reduced to 20px)
    # Font: Google Sans Bold, slightly smaller
    draw_text_at(date, 160, 375, font_date, text_color)
    
    # Save the final certificate
    certificate.save(output_path, "PNG")
    print(f"✅ Certificate generated successfully: {output_path}")
    
    return output_path

if __name__ == "__main__":
    # Test with sample data
    data = CertificateBase(
        participant_name="Jane Doe",
        event_name="Hacktoberfest 2025",
        date_issued="2025-10-03"
    )

    file_path = generate_certificate_from_model(data, "test_certificate.png")
    print("✅ Certificate generated at:", file_path)