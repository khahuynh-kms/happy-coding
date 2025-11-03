from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from beanie import Document, PydanticObjectId, Link
import asyncio


T = TypeVar("T", bound=Document)


class BaseService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, data) -> T:
        data = self._serializer(data)
        item = self.model(**data)
        return await item.insert()

    async def find_one(self, id: PydanticObjectId) -> Optional[T]:
        item = await self.model.get(id)
        if item:
            await self._fetch_nested_links(item)
        return item

    async def find_all(self) -> List[T]:
        result = await self.model.find_all().to_list()
        await asyncio.gather(*[
            self._fetch_nested_links(item) for item in result])
        return result

    async def update(
        self,
        id: PydanticObjectId,
        data
    ) -> Optional[T]:
        data = self._serializer(data)

        await self.model.find(
            self.model.id == id).update({"$set": data})

        item = await self.find_one(id)
        if item:
            await self._fetch_nested_links(item)
        return item

    async def delete(self, id: PydanticObjectId) -> bool:
        item = await self.model.get(id)
        if not item:
            return False
        await item.delete()
        return True

    async def increase(
        self,
        id: PydanticObjectId,
        expression: Dict[Any, Any]
    ) -> Optional[T]:
        await self.model.find(self.model.id == id).inc(expression=expression)

    def _serializer(self, data):
        """Create a new document from dict or Pydantic model."""
        if hasattr(data, "model_dump"):  # ✅ Handle Pydantic models
            data = data.model_dump(
                exclude_unset=True, exclude_none=True
            )
        elif hasattr(data, "dict"):      # ✅ Handle BaseModel (pydantic v1)
            data = data.dict()
        elif not isinstance(data, dict):
            raise TypeError("Data must be a dict or Pydantic model")

        return data

    async def _fetch_nested_links(self, document: Document):
        """
        Recursively fetches all nested links in a Beanie document.
        """
        tasks = []
        for field_name, field_value in document.model_dump().items():
            # Use getattr to inspect the actual field types on the model
            field = getattr(document, field_name)

            # Check if the field is a Link
            if isinstance(field, Link):
                tasks.append(self._fetch_link(document, field_name))

            elif isinstance(field, list) and field:
                # Check if the list contains Links or other
                # documents/models to recurse into
                if isinstance(field[0], Link):
                    tasks.append(self._fetch_link_list(document, field_name))
                # If it's a list of Pydantic models (like OrderItem),
                # recurse into each
                elif hasattr(field[0], 'model_fields'):
                    for item in field:
                        tasks.append(self._fetch_nested_links(item))
            # If the field is a single Pydantic model, recurse into it
            elif hasattr(field, 'model_fields'):
                tasks.append(self._fetch_nested_links(field))

        if tasks:
            await asyncio.gather(*tasks)

    async def _fetch_link(self, document: Document, field_name: str):
        link = getattr(document, field_name)
        # The calling function ensures this is a Link,
        # so we can fetch directly.
        fetched_doc = await link.fetch()
        setattr(document, field_name, fetched_doc)
        # Recursively fetch links within the newly fetched document.
        await self._fetch_nested_links(fetched_doc)

    async def _fetch_link_list(self, document: Document, field_name: str):
        # The calling function ensures this is a list of Links.
        fetched_docs = await document.fetch_link(field_name)
        # Concurrently and recursively fetch links for each document
        # in the list.
        await asyncio.gather(*[
            self._fetch_nested_links(doc) for doc in fetched_docs])
