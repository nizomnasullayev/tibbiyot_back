import io
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import cloudinary.uploader
from app.config import CLOUDINARY_CLOUD_NAME

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../assets/certificate_template.png")
SIGNATURE_PATH = os.path.join(os.path.dirname(__file__), "../assets/signature.png")
FONT_PATH = os.path.join(os.path.dirname(__file__), "../assets/font.ttf")  # put any .ttf font here


def get_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


def generate_qr_code(data: str) -> Image.Image:
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGBA")


def generate_certificate(
    user_full_name: str,
    accuracy: float,
    certificate_uid: str,
    certificate_number: int,
) -> bytes:
    # Load template
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(template)
    width, height = template.size

    # Fonts
    font_large = get_font(36)
    font_medium = get_font(28)
    font_small = get_font(22)

    # ── Certificate number (top center) ──────────────────────
    cert_no = f"No. {certificate_number:03d}"
    draw.text((width // 2, 38), cert_no, font=font_small, fill="black", anchor="mm")

    # ── User's full name (first blank line) ──────────────────
    name_y = int(height * 0.35)
    draw.text((width // 2, name_y), user_full_name, font=font_large, fill="black", anchor="mm")

    # ── Accuracy percentage (second blank line) ───────────────
    accuracy_text = f"{accuracy:.1f}%"
    accuracy_y = int(height * 0.44)
    draw.text((width // 2, accuracy_y), accuracy_text, font=font_medium, fill="black", anchor="mm")

    # ── QR code (bottom left) ────────────────────────────────
    verify_url = f"https://yourapp.com/verify/{certificate_uid}"
    qr_img = generate_qr_code(verify_url)
    qr_size = int(height * 0.18)
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = int(width * 0.06)
    qr_y = int(height * 0.76)
    template.paste(qr_img, (qr_x, qr_y), qr_img)

    # ── Date (below QR code) ─────────────────────────────────
    date_str = datetime.now().strftime("%d.%m.%Y")
    date_x = qr_x + qr_size // 2
    date_y = qr_y + qr_size + 8
    draw.text((date_x, date_y), date_str, font=font_small, fill="black", anchor="mm")

    # ── Signature (bottom right) ──────────────────────────────
    try:
        signature = Image.open(SIGNATURE_PATH).convert("RGBA")
        sig_width = int(width * 0.18)
        sig_ratio = signature.height / signature.width
        sig_height = int(sig_width * sig_ratio)
        signature = signature.resize((sig_width, sig_height))
        sig_x = int(width * 0.72)
        sig_y = int(height * 0.76)
        template.paste(signature, (sig_x, sig_y), signature)
    except:
        pass

    # ── Signer name (below signature) ────────────────────────
    signer_y = int(height * 0.92)
    draw.text(
        (int(width * 0.80), signer_y),
        "Maxmurova Mavjuda Halimovna",
        font=font_small,
        fill="black",
        anchor="mm"
    )

    # ── Save to bytes ─────────────────────────────────────────
    output = io.BytesIO()
    template.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output.read()


def upload_certificate(image_bytes: bytes, certificate_uid: str) -> str:
    result = cloudinary.uploader.upload(
        image_bytes,
        folder="tibbiyot/certificates",
        public_id=certificate_uid,
        resource_type="image",
    )
    return result["secure_url"]