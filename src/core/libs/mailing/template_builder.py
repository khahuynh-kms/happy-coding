from typing import Generic
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .mailing_type import BuilderModel


class TemplateBuilder(Generic[BuilderModel]):
    template_env = Environment(
        loader=FileSystemLoader(
            Path(__file__).resolve().parent / "templates"),
        autoescape=select_autoescape(["html", "xml"])
    )

    def __init__(self, template_name: str, default_subject: str = None):
        self.template_name = template_name
        self.default_subject = default_subject

    def render(self, payload: BuilderModel) -> str:
        """Render template with flexible payload types."""
        template = self.template_env.get_template(self.template_name)

        # normalize payload to dict
        if hasattr(payload, "dict"):  # Pydantic
            data = payload.dict()
        elif hasattr(payload, "__dataclass_fields__"):  # dataclass
            from dataclasses import asdict
            data = asdict(payload)
        elif isinstance(payload, dict):  # plain dict
            data = payload
        else:  # generic object
            data = vars(payload)

        return template.render(**data)
