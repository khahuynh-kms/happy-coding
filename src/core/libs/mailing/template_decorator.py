from typing import Type
from fastapi import HTTPException, status
from .template_factory import TemplateFactory


def register_template(template_name: str, default_subject: str = None):
    if not template_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide template name for this model"
        )

    """Decorator to auto-register a model with a template"""
    def decorator(model_cls: Type):
        TemplateFactory.register(model_cls, template_name, default_subject)
        return model_cls
    return decorator
