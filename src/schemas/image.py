from typing import Union
from uuid import UUID

from pydantic import BaseModel


class ImageModel(BaseModel):
    current_plate: str
    url: str
    cloudinary_public_id: str
    history: Union[UUID, int]
