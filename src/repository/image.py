import random
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Image


async def get_random_image_info(session: AsyncSession) -> Tuple[str, int]:
    query = select(Image)
    result = await session.execute(query)
    images = result.scalars().all()
    random_image = random.choice(images)
    return random_image.current_plate, random_image.id


async def create_image(session: AsyncSession, current_plate: str, url: str, cloudinary_public_id: str) -> Image:
    image = Image(current_plate=current_plate, url=url, cloudinary_public_id=cloudinary_public_id)
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image
