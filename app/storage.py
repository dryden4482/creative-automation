import json
import os
import re
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.schemas import CampaignBrief

DATA_ROOT = Path(os.getenv("DATA_ROOT", "data"))
CAMPAIGNS_ROOT = DATA_ROOT / "campaigns"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def normalize_name(value: str) -> str:
    value = value.lower().strip().replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]+", "", value)
    return value


def get_campaign_dir(campaign_id: str) -> Path:
    return CAMPAIGNS_ROOT / campaign_id


def get_assets_dir(campaign_id: str) -> Path:
    return get_campaign_dir(campaign_id) / "assets"


def get_outputs_dir(campaign_id: str) -> Path:
    return get_campaign_dir(campaign_id) / "outputs"


def get_brief_path(campaign_id: str) -> Path:
    return get_campaign_dir(campaign_id) / "brief.json"


def create_campaign_folders() -> str:
    campaign_id = str(uuid.uuid4())
    campaign_dir = get_campaign_dir(campaign_id)
    (campaign_dir / "assets").mkdir(parents=True, exist_ok=True)
    (campaign_dir / "outputs").mkdir(parents=True, exist_ok=True)
    return campaign_id


def save_brief(campaign_id: str, brief: CampaignBrief) -> Path:
    path = get_brief_path(campaign_id)
    path.write_text(json.dumps(brief.model_dump(), indent=2), encoding="utf-8")
    return path


def load_brief(campaign_id: str) -> CampaignBrief:
    path = get_brief_path(campaign_id)
    return CampaignBrief.model_validate_json(path.read_text(encoding="utf-8"))


async def save_uploaded_files(campaign_id: str, files: list[UploadFile]) -> list[str]:
    assets_dir = get_assets_dir(campaign_id)
    assets_dir.mkdir(parents=True, exist_ok=True)
    saved_files: list[str] = []

    for file in files:
        if not file.filename:
            continue
        destination = assets_dir / Path(file.filename).name
        content = await file.read()
        destination.write_bytes(content)
        saved_files.append(destination.name)

    return saved_files


def find_logo(campaign_id: str) -> Path | None:
    for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo.webp"):
        path = get_assets_dir(campaign_id) / name
        if path.exists():
            return path
    return None


def find_product_asset(campaign_id: str, product_name: str) -> Path | None:
    base_name = normalize_name(product_name)
    assets_dir = get_assets_dir(campaign_id)
    for extension in IMAGE_EXTENSIONS:
        path = assets_dir / f"{base_name}{extension}"
        if path.exists():
            return path
    return None


def list_output_files(campaign_id: str) -> dict[str, list[str]]:
    outputs_dir = get_outputs_dir(campaign_id)
    if not outputs_dir.exists():
        return {}

    results: dict[str, list[str]] = {}
    for product_dir in sorted(path for path in outputs_dir.iterdir() if path.is_dir()):
        files = sorted(
            str(file.relative_to(get_campaign_dir(campaign_id)))
            for file in product_dir.iterdir()
            if file.is_file()
        )
        results[product_dir.name] = files
    return results
