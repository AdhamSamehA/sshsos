from pydantic import BaseModel
from typing import List, Optional

class Supermarket(BaseModel):
    id: int
    name: str
    address: str
    phone_number: str
    photo_url: Optional[str] = None

class SupermarketFeedResponse(BaseModel):
    success: bool
    supermarkets: List[Supermarket]


class AddSupermarketRequest(BaseModel):
    name: str
    photo_url: str
    address: str
    phone_number: str

class SupermarketResponse(BaseModel):
    id: int
    name: str
    photo_url: str
    address: str
    phone_number: str



