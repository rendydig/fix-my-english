from PIL import Image, ImageDraw, ImageFont

def create_tray_icon_image():
    """Create a modern icon for the system tray and save it as icon.ico"""
    # Create a rounded square icon with gradient
    width = 64
    height = 64
    
    # Create base image with transparency
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw a rounded rectangle
    radius = 15
    color1 = "#3498db"  # Start color - light blue
    color2 = "#2980b9"  # End color - darker blue
    
    # Draw the rounded rectangle (simulated with multiple rectangles and ellipses)
    dc.rectangle([radius, 0, width-radius, height], fill=color1)
    dc.rectangle([0, radius, width, height-radius], fill=color1)
    
    # Draw the four corners
    dc.ellipse([0, 0, radius*2, radius*2], fill=color1)
    dc.ellipse([width-radius*2, 0, width, radius*2], fill=color1)
    dc.ellipse([0, height-radius*2, radius*2, height], fill=color1)
    dc.ellipse([width-radius*2, height-radius*2, width, height], fill=color1)
    
    # Add a "F" letter in the center
    try:
        # Try to use a font if available
        font = ImageFont.truetype("arial.ttf", 32)
        text_width, text_height = dc.textsize("F", font=font)
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        dc.text((text_x, text_y), "F", fill="white", font=font)
    except:
        # Fallback to drawing a simple F shape
        margin = width // 4
        dc.line([margin, margin, margin, height-margin], fill="white", width=3)
        dc.line([margin, margin, width-margin, margin], fill="white", width=3)
        dc.line([margin, height//2, width-margin, height//2], fill="white", width=3)
    
    return image
