import hashlib
from time import perf_counter



from app.storage import (
    find_logo,
    find_product_asset,
    get_campaign_dir,
    get_outputs_dir,
    load_brief,
)
from app.vertex import generate_campaign_image
OUTPUT_SPECS = {
    "1x1": {"aspect_ratio": "1:1"},
    "9x16": {"aspect_ratio": "9:16"},
    "16x9": {"aspect_ratio": "16:9"},
}


def _build_style_guide(brief) -> str:
    return (
        f"Campaign name: {brief.campaign_name}. "
        f"Market: {brief.market}. "
        f"Audience: {brief.audience}. "
        f"Campaign message: {brief.campaign_message}. "
        "Use a polished modern advertising style with strong consistency across all products in this campaign. "
        "Keep the layout premium, minimal, and social-ready."
    )


def _campaign_seed(campaign_id: str) -> int:
    return int(hashlib.sha256(campaign_id.encode("utf-8")).hexdigest()[:8], 16) % 2147483647


def run_campaign(campaign_id: str) -> dict:
    brief = load_brief(campaign_id)
    campaign_dir = get_campaign_dir(campaign_id)
    outputs_dir = get_outputs_dir(campaign_id)
    logo_path = find_logo(campaign_id)
    style_guide = _build_style_guide(brief)
    seed = _campaign_seed(campaign_id)

    reused_assets: dict[str, str] = {}
    outputs: dict[str, list[str]] = {}

    for product in brief.products:
        product_name = product.product_name
        product_image_path = find_product_asset(campaign_id, product_name)
        if product_image_path:
            reused_assets[product_name] = str(product_image_path.relative_to(campaign_dir))

        product_output_dir = outputs_dir / product_name
        outputs[product_name] = []

        square_output_path = product_output_dir / "1x1.png"
        print(f"Running image generation for {product_name} at 1x1 aspect ratio")
        start = perf_counter()
        generate_campaign_image(
            product_name=product_name,
            campaign_message=brief.campaign_message,
            output_path=square_output_path,
            aspect_ratio=OUTPUT_SPECS["1x1"]["aspect_ratio"],
            product_image_path=product_image_path,
            logo_path=logo_path,
            style_guide=style_guide,
            seed=seed,
        )
        print(f"Time taken: {perf_counter() - start:.6f} seconds")
        outputs[product_name].append(str(square_output_path.relative_to(campaign_dir)))

        for ratio_name in ("9x16", "16x9"):
            output_path = product_output_dir / f"{ratio_name}.png"
            print(f"running image generation for {product_name} at {ratio_name} aspect ratio")
            start = perf_counter()
            generate_campaign_image(
                product_name=product_name,
                campaign_message=brief.campaign_message,
                output_path=output_path,
                aspect_ratio=OUTPUT_SPECS[ratio_name]["aspect_ratio"],
                logo_path=logo_path,
                reference_creative_path=square_output_path,
                style_guide=style_guide,
                seed=seed,
            )
            print(f"Time taken: {perf_counter() - start:.6f} seconds")
            outputs[product_name].append(str(output_path.relative_to(campaign_dir)))

    return {
        "reused_assets": reused_assets,
        "outputs": outputs,
    }
