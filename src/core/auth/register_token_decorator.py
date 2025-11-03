
from pydantic import BaseModel

from .security_service import SecurityService


def register_token(
    token_type: str,
    *,
    secret_key: str,
    minutes: int,
    algorithm: str = "HS256",
):
    """
    Decorator: attach token config metadata to model class,
    but don't register until actually used.
    """
    def wrapper(model_cls: type[BaseModel]):
        model_cls.__token_type__ = token_type
        model_cls.__token_secret_key__ = secret_key
        model_cls.__token_minutes__ = minutes
        model_cls.__token_algorithm__ = algorithm
        SecurityService._registry[model_cls.__name__] = model_cls
        return model_cls
    return wrapper
