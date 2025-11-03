from typing import Optional, Type, TypeVar
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel

import logging


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

T = TypeVar("T", bound=BaseModel)


class SecurityService:
    _registry: dict[str, Type[BaseModel]] = {}

    @staticmethod
    def create_token(
        data: T,
        expires_delta: Optional[timedelta] = None
    ) -> dict:
        model = SecurityService._registry.get(data.__class__.__name__)
        token_type = getattr(model, "__token_type__", None)
        if not token_type:
            raise ValueError(f"Model {model.__name__} is not registered")

        expire = datetime.now() + (
            expires_delta or timedelta(minutes=model.__token_minutes__)
        )
        payload = {"exp": expire, "type": token_type, **data.model_dump()}
        token = jwt.encode(
            payload,
            key=model.__token_secret_key__,
            algorithm=model.__token_algorithm__
        )
        return {f"{token_type}": token, "exp": expire}

    @staticmethod
    def decode_token(
        token: str, model_cls: Type[T] = None, token_type: str = None
    ) -> Optional[T]:
        if model_cls is not None:
            model = SecurityService._registry.get(model_cls.__name__)

        if token_type is not None:
            model = SecurityService._get_registered_models_by_type(token_type)

        if not model:
            raise ValueError(f"Model {model_cls.__name__} is not registered")

        token_type = getattr(model, "__token_type__", None)
        if not token_type:
            raise ValueError(
                f"Model {model.__name__} is not registered"
            )

        payload = jwt.decode(
            token, key=model.__token_secret_key__,
            algorithms=[model.__token_algorithm__]
        )
        return payload

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logging.error(f"Unexpected error in password verification: {e}")
            return False

    @classmethod
    def _get_registered_models_by_type(
            cls, token_type: str) -> list[Type[BaseModel]]:
        result = [
            model for model in cls._registry.values()
            if getattr(model, "__token_type__", None) == token_type
        ]

        return result[0] if result else None
