from ...core.services.base import BaseService
from .models import Category


class CategoryService(BaseService[Category]):
    def __init__(self):
        super().__init__(Category)


category_service = CategoryService()
