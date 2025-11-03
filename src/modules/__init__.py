import importlib
import inspect
import os
from pathlib import Path

from beanie import Document

base_path = Path(__file__).parent
modules_path = base_path.parent / "modules"


def load_routers():
    routers = []

    for root, _, files in os.walk(modules_path):
        if "router.py" in files:
            relative_path = Path(root).relative_to(base_path.parent)
            module_name_parts = list(relative_path.parts) + ["router"]
            module_name = "src." + ".".join(module_name_parts)
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "router"):
                    routers.append(module.router)
            except ImportError as e:
                print(f"Could not import router from {module_name}: {e}")
    return routers


def load_document_models():
    """
    Dynamically imports all models under src/modules/**/models.py
    and returns Beanie Document subclasses.
    """

    document_models = []
    for root, _, files in os.walk(modules_path):
        if "models.py" in files:
            relative_path = Path(root).relative_to(base_path.parent)
            module_name_parts = list(relative_path.parts) + ["models"]
            module_name = "src." + ".".join(module_name_parts)
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):

                    if (inspect.isclass(obj) and issubclass(obj, Document)
                            and obj != Document):

                        # Ensure it's defined *inside* the module
                        if obj.__module__ == module.__name__:
                            document_models.append(obj)

            except ImportError as e:
                print(f"Could not import module {module_name}: {e}")

    return document_models
