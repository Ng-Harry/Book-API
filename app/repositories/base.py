from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        db_obj = await self.get_by_id(id)
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            await self.db.commit()
            await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False