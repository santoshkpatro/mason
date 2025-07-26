import importlib
from pathlib import Path
from mason.globals import get_settings

__all__ = []  # Will hold all model class names

def _scan_models():
    """Yield all module names under app/models."""
    settings = get_settings()
    models_dir = Path(settings.BASE_DIR) / "app" / "models"

    for file in models_dir.rglob("*.py"):
        if file.name == "__init__.py":
            continue
        yield f"app.models.{file.stem}"

def __getattr__(name):
    for module_name in _scan_models():
        module = importlib.import_module(module_name)
        if hasattr(module, name):
            return getattr(module, name)

    raise AttributeError(f"Model '{name}' not found")

# Populate __all__ dynamically
for module_name in _scan_models():
    module = importlib.import_module(module_name)
    for attr in dir(module):
        if not attr.startswith("_"):
            obj = getattr(module, attr)
            if isinstance(obj, type):  # Only include classes
                __all__.append(attr)
