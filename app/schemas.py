from pydantic import BaseModel, Field, field_validator


class ProductInput(BaseModel):
    product_name: str = Field(..., min_length=1)


class CampaignBrief(BaseModel):
    campaign_name: str = Field(..., min_length=1)
    market: str = Field(..., min_length=1)
    audience: str = Field(..., min_length=1)
    campaign_message: str = Field(..., min_length=1)
    products: list[ProductInput]

    @field_validator("products")
    @classmethod
    def validate_products(cls, value: list[ProductInput]) -> list[ProductInput]:
        if len(value) < 2:
            raise ValueError("products must contain at least two items")
        return value
