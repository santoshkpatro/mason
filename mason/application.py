import importlib
import inspect
import re
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request as StarletteRequest
from starlette.templating import Jinja2Templates

from mason.globals import get_settings


class MasonApplication(Starlette):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._settings = get_settings()
        self.routing_table = {method: {} for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]}
        self.templates = Jinja2Templates(directory=str(self.views_dir))

        # Autoload controllers
        self.autoload()

    @property
    def project_dir(self):
        return Path(self._settings.BASE_DIR).resolve()

    @property
    def app_dir(self):
        return self.project_dir / "app"

    @property
    def controllers_dir(self):
        return self.app_dir / "controllers"

    @property
    def views_dir(self):
        return self.app_dir / "views"

    @property
    def models_dir(self):
        return self.app_dir / "models"

    def autoload(self):
        print("📦 Autoloading resources...")
        self._autoload_controllers()

    def _autoload_controllers(self):
        print("📂 Loading controllers...")

        for file in self.controllers_dir.rglob("*_controller.py"):
            relative_path = file.relative_to(self.controllers_dir).with_suffix("")
            path_parts = relative_path.parts
            module_name = ".".join(["app", "controllers", *path_parts])
            class_name = self.to_camel_case("_".join(path_parts))

            try:
                module = importlib.import_module(module_name)
                controller_class = getattr(module, class_name)
                mount_path = getattr(controller_class, "__mount_path__", None)

                if not mount_path:
                    print(f"⚠️ Skipping {class_name}: missing @mount decorator")
                    continue

                route_count = 0
                for name, method in inspect.getmembers(controller_class, inspect.isfunction):
                    if hasattr(method, "__routes__"):
                        for http_method, route_path in method.__routes__:
                            full_path = self._normalize_path(mount_path, route_path)
                            regex_path = self._convert_path_to_regex(full_path)
                            self.routing_table[http_method][regex_path] = {
                                "controller": controller_class,
                                "action": name,
                            }
                            print(f"🔗 Route registered: [{http_method}] {full_path} → {class_name}.{name}")
                            route_count += 1

                if route_count == 0:
                    print(f"ℹ️ No route-decorated actions found in {class_name}")

            except (ModuleNotFoundError, AttributeError) as e:
                print(f"❌ Error loading {class_name} from {module_name}: {e}")

    def to_camel_case(self, snake_str):
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    def _normalize_path(self, base, route):
        return f"{base.rstrip('/')}/{route.lstrip('/')}"

    def _convert_path_to_regex(self, path):
        regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        regex = regex.rstrip('/')
        return f"^{regex}/?$"

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await super().__call__(scope, receive, send)
            return

        request = StarletteRequest(scope, receive)
        path = request.url.path
        method = request.method.upper()

        for regex, handler in self.routing_table.get(method, {}).items():
            match = re.match(regex, path)
            if match:
                controller_class = handler["controller"]
                action_name = handler["action"]
                controller_instance = controller_class()
                action = getattr(controller_instance, action_name)
                request_context = {
                    "query_params": request.query_params,
                    "path_params": match.groupdict(),
                    "method": method,
                    "_request": request,
                }

                # before_action hook
                if hasattr(controller_instance, "before_action"):
                    controller_instance.before_action(**request_context)

                specific_before = f"before_{action_name}"
                if hasattr(controller_instance, specific_before):
                    getattr(controller_instance, specific_before)(**request_context)

                # Call the controller action
                response = action(**request_context)

                if response is not None:
                    await response(scope, receive, send)
                    return

                # Render template fallback
                controller_file = Path(inspect.getfile(controller_class))
                relative_controller_path = controller_file.relative_to(self.controllers_dir).with_suffix("")
                path_parts = list(relative_controller_path.parts)
                path_parts[-1] = path_parts[-1].replace("_controller", "")
                template_subpath = "/".join(path_parts).lower()
                template_name = f"{template_subpath}/{action_name}.html"

                template_context = {
                    "request": request,
                    **getattr(controller_instance, "_template_context", {})
                }

                html_response = self.templates.TemplateResponse(name=template_name, context=template_context)
                await html_response(scope, receive, send)
                return

        await Response("404 Not Found", status_code=404)(scope, receive, send)
