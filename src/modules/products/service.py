from .models import Product
from ...core.services.base import BaseService


class ProductService(BaseService[Product]):
    def __init__(self):
        super().__init__(Product)


product_service = ProductService()
