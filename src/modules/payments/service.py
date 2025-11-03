from .models import Payment
from ...core.services.base import BaseService


class PaymentService(BaseService[Payment]):
    def __init__(self):
        super().__init__(Payment)


payment_service = PaymentService()
