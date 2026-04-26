# Creative Automation

Small FastAPI backend that accepts a campaign brief, stores uploaded assets locally, and uses Gemini 3 Pro Image on Vertex AI to create a branded `1x1` master creative and then derive the other aspect ratios from it.

## Design Considerations

TThe primary design goal was to keep the implementation simple, focused, and easy to reason about. Rather than building a fully featured production system, I prioritized a lightweight workflow that satisfies the core requirements of the brief while avoiding unnecessary infrastructure and complexity.

GCP was selected because it provides straightforward access to Gemini through Vertex AI. Using the Vertex API kept the model integration relatively direct and avoided adding additional abstraction layers or third-party orchestration tools. This also made the implementation easier to configure, test, and extend if more model functionality is needed later.

For the brief itself, I intentionally limited the data model to a small set of core fields. This helped prevent scope creep and kept the application centered on the most important information required to generate and manage a brief. Additional metadata, validation rules, user permissions, or workflow states could be added in the future, but they were left out of the initial design to keep the project manageable.

The application does not use a database or any robust persistence layer. Instead, it relies on simple file operations for storing and retrieving data. This is sufficient for a small prototype or local workflow, but it does come with tradeoffs. File-based storage is easier to inspect and debug, but it does not provide the reliability, concurrency handling, query capabilities, or access controls that a database would offer.

The asset upload flow was also kept intentionally simple. The system does not handle base64-encoded uploads or multipart upload streams. Instead, assets are “uploaded” by passing in a file path and moving the file into the appropriate directory. This approach works well for a controlled local environment, but it would need to be redesigned for a production deployment where users upload files through a web interface or API.

Overall, the design favors clarity and minimalism over scalability. The current structure is appropriate for demonstrating the core workflow, but future iterations could introduce stronger storage, better upload handling, validation, authentication, and more robust error handling as the system requirements become more complex.

## Environment variables

- `GCP_PROJECT_ID`
- `GCP_LOCATION`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `DATA_ROOT`
- `VERTEX_IMAGE_MODEL` (optional)

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a
source .env
set +a
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Example curl flow

1. Create campaign

```bash
curl -X POST http://localhost:8000/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Summer Push",
    "market": "US",
    "audience": "Young professionals",
    "campaign_message": "Refresh your routine this summer",
    "products": [
      { "product_name": "Product A" },
      { "product_name": "Product B" }
    ]
  }'
```

2. Upload files

```bash
curl -X POST http://localhost:8000/campaigns/{campaign_id}/assets \
  -F "files=@examples/product_a.jpg" \
  -F "files=@examples/logo.png"
```

3. Run pipeline

```bash
curl -X POST http://localhost:8000/campaigns/{campaign_id}/run
```

4. View outputs

```bash
curl http://localhost:8000/campaigns/{campaign_id}/outputs
```

## Example files

An end-to-end fake campaign example lives under `examples/fake_campaign/`.

Run the steps with:

```bash
bash examples/fake_campaign/scripts/1_create_campaign.sh
bash examples/fake_campaign/scripts/2_upload_assets.sh
bash examples/fake_campaign/scripts/3_run_campaign.sh
bash examples/fake_campaign/scripts/4_get_outputs.sh
```

To force a brand-new example campaign after one already exists:

```bash
FORCE_CREATE=1 bash examples/fake_campaign/scripts/1_create_campaign.sh
```

## Outputs

Generated files are saved under `data/campaigns/{campaign_id}/outputs/`.

## Limitations

Happy-path only. No database, auth, frontend, cloud storage, advanced template system, or deterministic text rendering.
