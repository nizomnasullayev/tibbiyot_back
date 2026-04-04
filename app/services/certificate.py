import io
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import cloudinary.uploader
from app.config import CLOUDINARY_CLOUD_NAME, APP_URL

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../assets/certificate_template.png")
SIGNATURE_PATH = os.path.join(os.path.dirname(__file__), "../assets/signature.png")
DEFAULT_FONT_PATH = os.path.join(os.path.dirname(__file__), "../assets/font.ttf")
TIMES_REGULAR = r"C:\Windows\Fonts\times.ttf"
TIMES_BOLD = r"C:\Windows\Fonts\timesbd.ttf"
CERT_BLUE = "#234f93"


def get_font(size: int, font_path: str | None = None):
    for candidate in [font_path, DEFAULT_FONT_PATH]:
        if not candidate:
            continue
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def fit_font(draw: ImageDraw.ImageDraw, text: str, base_size: int, max_width: int, font_path: str | None = None):
    size = base_size
    while size > 18:
        font = get_font(size, font_path)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return font
        size -= 2
    return get_font(18, font_path)


def draw_text_with_bg(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font, *, fill="black", bg="#f8f1e5", padding_x=18, padding_y=8):
    bbox = draw.textbbox(position, text, font=font, anchor="mm")
    rect = (
        bbox[0] - padding_x,
        bbox[1] - padding_y,
        bbox[2] + padding_x,
        bbox[3] + padding_y,
    )
    draw.rounded_rectangle(rect, radius=10, fill=bg)
    draw.text(position, text, font=font, fill=fill, anchor="mm")


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
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(template)
    width, height = template.size

    font_name = fit_font(draw, user_full_name, 60, int(width * 0.58), TIMES_BOLD)
    font_accuracy = get_font(36, TIMES_REGULAR)
    font_small = get_font(24, TIMES_REGULAR)
    font_date = get_font(36, TIMES_BOLD)
    font_signer = get_font(32, TIMES_BOLD)

    cert_no = f"{certificate_number:03d}"
    draw_text_with_bg(
        draw,
        (width // 2, 52),
        cert_no,
        get_font(30, TIMES_BOLD),
        fill=CERT_BLUE,
        bg="white",
        padding_x=20,
        padding_y=8,
    )

    name_y = int(height * 0.325)
    draw.text(
        (width // 2, name_y),
        user_full_name,
        font=font_name,
        fill=CERT_BLUE,
        anchor="mm",
        stroke_width=1,
        stroke_fill=CERT_BLUE,
    )

    accuracy_text = f"{round(accuracy)}%"
    accuracy_y = int(height * 0.41)
    draw.text((width // 2, accuracy_y), accuracy_text, font=font_accuracy, fill=CERT_BLUE, anchor="mm")

    verify_url = f"{APP_URL}/certificates/verify/{certificate_uid}"
    qr_img = generate_qr_code(verify_url)
    qr_size = int(height * 0.20)
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = int(width * 0.11)
    qr_y = int(height * 0.71)
    template.paste(qr_img, (qr_x, qr_y), qr_img)

    date_str = datetime.now().strftime("%d.%m.%Y")
    date_x = qr_x + qr_size + 90
    date_y = qr_y + qr_size - 10
    draw.text((date_x, date_y), date_str, font=font_date, fill=CERT_BLUE, anchor="lm")

    try:
        signature = Image.open(SIGNATURE_PATH).convert("RGBA")
        sig_width = int(width * 0.24)
        sig_ratio = signature.height / signature.width
        sig_height = int(sig_width * sig_ratio)
        signature = signature.resize((sig_width, sig_height))
        sig_x = int(width * 0.66)
        sig_y = int(height * 0.74)
        template.paste(signature, (sig_x, sig_y), signature)
    except Exception:
        pass

    signer_y = int(height * 0.89)
    draw.text(
        (int(width * 0.72), signer_y),
        "Maxmurova Mavjuda Halimovna",
        font=font_signer,
        fill=CERT_BLUE,
        anchor="mm",
    )

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
