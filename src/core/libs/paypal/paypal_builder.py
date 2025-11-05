from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar


T = TypeVar("T", bound="PayPalRequestInterface")


class PayPalRequestInterface(ABC):
    """Abstract base for PayPal request conversion."""

    @classmethod
    @abstractmethod
    def from_raw(cls: Type[T], raw_data: Dict[str, Any]) -> T:
        """Convert raw data into a PayPal-compatible request object."""
        raise NotImplementedError


class PayPalRequestBuilder:
    """Generic builder that maps raw order data to PayPal request interfaces."""

    @staticmethod
    def build(raw_data: Dict[str, Any], destination_class: Type[T]) -> T:
        """Convert raw order data into the target destination type."""
        return destination_class.from_raw(raw_data)

