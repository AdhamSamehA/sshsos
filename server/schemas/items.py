from pydantic import BaseModel
from typing import List

# Response model for categories
class CategoryResponse(BaseModel):
    id: int
    name: str

# Response model for items
class ItemResponse(BaseModel):
    id: int
    name: str
    photo_url: str
    price: float
    description: str
    supermarket_id: int

# Response model for items by category
class ItemListResponse(BaseModel):
    category_id: int
    category_name: str
    items: List[ItemResponse]

