import importlib
import pkgutil

from typing import Dict, Type
from pydantic import BaseModel

from . import payloads

from .template_builder import TemplateBuilder
from .mailing_type import BuilderModel


class TemplateFactory:
    """Maps models to templates and returns a builder."""

    _registry: Dict[Type[BaseModel], object] = {}

    @classmethod
    def register(
        cls, model: Type[BaseModel], template_name: str,
        default_subject: str = None
    ):
        print(
            f"[TemplateFactory] – Loaded template "
            f"({template_name}) for [{model.__name__}]"
            f" with default subject: {default_subject}"
        )
        cls._registry[model] = {
            "template_name": template_name,
            "default_subject": default_subject
        }

    @classmethod
    def get_builder(
        cls,
        model: Type[BuilderModel]
    ) -> TemplateBuilder[BuilderModel]:
        builder = cls._registry.get(model)
        template_name = builder["template_name"] if builder else None
        if not template_name:
            raise ValueError(
                f"No template registered for model {model.__name__}"
            )

        return TemplateBuilder[BuilderModel](
            template_name,
            builder["default_subject"],
        )

    @staticmethod
    def on_load_templates():
        """
        Auto-import all modules in utils.mailing.payloads 
        so that @register_template decorators run.
        """
        package = payloads
        for _, mod_name, _ in pkgutil.iter_modules(package.__path__):
            full_module = f"{package.__name__}.{mod_name}"
            importlib.import_module(full_module)
