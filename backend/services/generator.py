from PIL import Image, ImageDraw, ImageFont
import os
from backend.app.models.certificates import CertificateBase

def generate_certificate_from_model(cert_data: CertificateBase, output_path="certificate.png"):
    # Now you can access cert_data.name, cert_data.event, cert_data.date
    return generate_certificate(cert_data.participant_name, cert_data.event_name, cert_data.date_issued, output_path)

def generate_certificate(name, event, date, output_path="certificate.png"):
    # Debug: show where it will save
    print("Saving certificate at:", os.path.abspath(output_path))
    
    # Create certificate with a gradient-like background
    width, height = 1200, 850
    certificate = Image.new("RGB", (width, height), color="#f8f9fa")
    draw = ImageDraw.Draw(certificate)
    
    # Draw decorative border
    border_color = "#2c3e50"
    border_width = 15
    # Outer border
    draw.rectangle([20, 20, width-20, height-20], outline=border_color, width=border_width)
    # Inner border (golden accent)
    draw.rectangle([40, 40, width-40, height-40], outline="#d4af37", width=3)
    
    # Add colored header background
    draw.rectangle([60, 60, width-60, 200], fill="#2c3e50")
    
    # Load fonts with fallback
    try:
        font_title = ImageFont.truetype("arial.ttf", 56)
        font_subtitle = ImageFont.truetype("arial.ttf", 32)
        font_name = ImageFont.truetype("arialbd.ttf", 48)  # Bold for name
        font_body = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        print("⚠️ TrueType fonts not found. Using default font.")
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Helper function to center text
    def center_text(text, y, font, color="black"):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)
    
    # Title
    center_text("CERTIFICATE", 90, font_title, "#d4af37")
    center_text("OF PARTICIPATION", 155, font_subtitle, "#ffffff")
    
    # Decorative line
    draw.line([300, 250, width-300, 250], fill="#d4af37", width=2)
    
    # "This is to certify that" text
    center_text("This certificate is proudly presented to", 300, font_small, "#555555")
    
    # Participant name (highlighted)
    name_y = 370
    center_text(name, name_y, font_name, "#2c3e50")
    
    # Underline for name
    bbox = draw.textbbox((0, 0), name, font=font_name)
    name_width = bbox[2] - bbox[0]
    name_x = (width - name_width) // 2
    draw.line([name_x, name_y + 60, name_x + name_width, name_y + 60], fill="#d4af37", width=2)
    
    # Event details
    center_text("For outstanding participation in", 480, font_small, "#555555")
    center_text(event, 530, font_body, "#2c3e50")
    
    # Date
    center_text(f"Dated: {date}", 620, font_small, "#555555")
    
    # Add decorative corner elements
    corner_size = 50
    corner_color = "#d4af37"
    # Top-left corner
    draw.line([60, 60, 60+corner_size, 60], fill=corner_color, width=4)
    draw.line([60, 60, 60, 60+corner_size], fill=corner_color, width=4)
    # Top-right corner
    draw.line([width-60-corner_size, 60, width-60, 60], fill=corner_color, width=4)
    draw.line([width-60, 60, width-60, 60+corner_size], fill=corner_color, width=4)
    # Bottom-left corner
    draw.line([60, height-60, 60+corner_size, height-60], fill=corner_color, width=4)
    draw.line([60, height-60-corner_size, 60, height-60], fill=corner_color, width=4)
    # Bottom-right corner
    draw.line([width-60-corner_size, height-60, width-60, height-60], fill=corner_color, width=4)
    draw.line([width-60, height-60-corner_size, width-60, height-60], fill=corner_color, width=4)
    
    # Signature line
    sig_y = 720
    draw.line([150, sig_y, 400, sig_y], fill="#333333", width=2)
    draw.line([width-400, sig_y, width-150, sig_y], fill="#333333", width=2)
    center_text("Authorized Signature", sig_y + 10, font_small, "#666666")
    
    # Save file
    certificate.save(output_path)
    return output_path

if __name__ == "__main__":
    data = CertificateBase(
        participant_name="Jane Doe",
        event_name="Hacktoberfest 2025",
        date_issued="2025-10-03"
    )

    file_path = generate_certificate_from_model(data)
    print("✅ Certificate generated at:", file_path)