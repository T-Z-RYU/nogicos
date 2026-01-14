import PIL.Image
import base64
from io import BytesIO


def image_to_base64(image: PIL.Image.Image, format="png"):
    image = image.convert("RGB")
    image_io = BytesIO()
    image.save(image_io, format=format)
    png_data = image_io.getvalue()
    base64_image = base64.b64encode(png_data).decode("utf-8")
    return base64_image


def image_to_data_url(image: PIL.Image.Image, format="png"):
    return f"data:image/png;base64,{image_to_base64(image, format=format)}"
