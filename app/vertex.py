import mimetypes
import os
from pathlib import Path

from google import genai
from google.genai import types


GEMINI_IMAGE_MODEL = os.getenv("VERTEX_IMAGE_MODEL", "gemini-3-pro-image-preview")


def _get_client() -> genai.Client:
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise RuntimeError("GCP_PROJECT_ID is not set")

    return genai.Client(
        vertexai=True,
        project=project_id,
        location=os.getenv("GCP_LOCATION", "global"),
    )


def _part_from_file(image_path: str | Path) -> types.Part:
    path = Path(image_path)
    mime_type, _ = mimetypes.guess_type(path.name)
    return types.Part.from_bytes(
        data=path.read_bytes(),
        mime_type=mime_type or "image/png",
    )


def _extract_image_bytes(response) -> bytes:
    for candidate in response.candidates or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            inline_data = getattr(part, "inline_data", None)
            if inline_data and inline_data.data:
                return inline_data.data
    raise ValueError("No image bytes returned from Gemini")


def _write_image_bytes(image_bytes: bytes, output_path: str | Path) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_bytes)
    return str(path)


def generate_campaign_image(
    product_name: str,
    campaign_message: str,
    output_path: str | Path,
    aspect_ratio: str,
    product_image_path: str | Path | None = None,
    logo_path: str | Path | None = None,
    reference_creative_path: str | Path | None = None,
    style_guide: str = "",
    seed: int | None = None,
) -> str:
    prompt = (
        f"{style_guide} "
        f"Generate a finished campaign image for {product_name}. "
        f"Include the exact campaign text '{campaign_message}' in the image. "
        "The text should be clean, readable, and professionally integrated into the design. "
        f"Target aspect ratio: {aspect_ratio}. "
        "No boarders around the image."
        "If a logo reference is provided, use the brand colors and overall feel from the logo and place it subtly and cleanly. "
        "Keep the overall campaign system visually consistent across all products."
        "Consider best practices for ad compaigns, the campaign should highlight and complement the product."
        
    )

    if reference_creative_path:
        prompt += (
            " Use the provided square campaign image as the main reference and adapt it to this new aspect ratio "
            "while preserving the same visual language, typography treatment, composition logic, and brand feel."
            "Make sure the logo is PRESERVED. NO CHANGES to the logo."
            
        )
    else:
        prompt += (
            " Build the master square campaign look now. Create a premium, modern 1:1 ad composition with clean branding, "
            "a polished product-forward aesthetic, tasteful logo integration, and a strong but minimal visual system."
        )

    contents: list[str | types.Part] = [prompt]
    if product_image_path and Path(product_image_path).exists():
        contents.append(_part_from_file(product_image_path))
    if logo_path and Path(logo_path).exists():
        contents.append(_part_from_file(logo_path))
    if reference_creative_path and Path(reference_creative_path).exists():
        contents.append(_part_from_file(reference_creative_path))

    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=[types.Modality.TEXT, types.Modality.IMAGE],
            seed=seed,
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                output_mime_type="image/png",
            ),
        ),
    )
    return _write_image_bytes(_extract_image_bytes(response), output_path)
