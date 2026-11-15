from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    phone_number: str = Field(min_length=8, max_length=32)
    password: str = Field(min_length=8, max_length=128)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)


class PriceItemInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    duration_minutes: int | None = Field(default=None, ge=0, le=1440)
    price_minor: int = Field(ge=0, le=1000000)
    currency: str = Field(default="GBP", min_length=3, max_length=3)
    category_id: int
    sort_order: int = 0
    is_published: bool = True


class CategoryInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    sort_order: int = 0
    is_published: bool = True


class SiteSettingsUpdate(BaseModel):
    values: dict[str, str] = Field(max_length=30)


class ReorderInput(BaseModel):
    item_ids: list[int] = Field(min_length=1, max_length=1000)


class PriceItemResponse(PriceItemInput):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(CategoryInput):
    id: int
    items: list[PriceItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
