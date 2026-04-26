from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from google.genai.errors import ClientError

from app.pipeline import run_campaign
from app.schemas import CampaignBrief
from app.storage import (
    create_campaign_folders,
    get_campaign_dir,
    list_output_files,
    save_brief,
    save_uploaded_files,
)

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/campaigns")
async def create_campaign(request: Request, brief: CampaignBrief) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise HTTPException(status_code=415, detail="Content-Type must be application/json")

    campaign_id = create_campaign_folders()
    save_brief(campaign_id, brief)
    return {"campaign_id": campaign_id}


@app.post("/campaigns/{campaign_id}/assets")
async def upload_assets(campaign_id: str, files: list[UploadFile] = File(...)) -> dict:
    campaign_dir = get_campaign_dir(campaign_id)
    if not campaign_dir.exists():
        raise HTTPException(status_code=404, detail="Campaign not found")

    saved_files = await save_uploaded_files(campaign_id, files)
    return {"campaign_id": campaign_id, "saved_files": saved_files}


@app.post("/campaigns/{campaign_id}/run")
def run_campaign_endpoint(campaign_id: str) -> dict:
    campaign_dir = get_campaign_dir(campaign_id)
    if not campaign_dir.exists():
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        return run_campaign(campaign_id)
    except ClientError as exc:
        status_code = 429 if exc.code == 429 else 502
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/campaigns/{campaign_id}/outputs")
def get_outputs(campaign_id: str) -> dict:
    campaign_dir = get_campaign_dir(campaign_id)
    if not campaign_dir.exists():
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {"campaign_id": campaign_id, "outputs": list_output_files(campaign_id)}
