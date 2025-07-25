import importlib
import re
import inspect
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from mason.globals import get_settings

class MasonApplication(Starlette):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._settings = get_settings()
        self.routing_table = {
            "GET": {},
            "POST": {},
            "PUT": {},
            "PATCH": {},
            "DELETE": {},
            "OPTIONS": {},
            "HEAD": {}
        }
        self.templates = Jinja2Templates(directory=str(self.views_dir))
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

    def autoload(self):
        print("📦 Loading controllers...")
        for file in self.controllers_dir.glob("*_controller.py"):
            module_name = f"app.controllers.{file.stem}"
            class_name = self.to_camel_case(file.stem)

            try:
                module = importlib.import_module(module_name)
                controller_class = getattr(module, class_name)
                mount_path = getattr(controller_class, "__mount_path__", None)

                if not mount_path:
                    print(f"⚠️ {class_name} missing @mount")
                    continue

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

            except (ModuleNotFoundError, AttributeError) as e:
                print(f"❌ Error loading {class_name}: {e}")

    def to_camel_case(self, snake_str):
        parts = snake_str.split('_')
        return ''.join([part.capitalize() for part in parts])

    def _normalize_path(self, base, route):
        return f"{base.rstrip('/')}/{route.lstrip('/')}"

    def _convert_path_to_regex(self, path):
        # Converts /users/{id} → ^/users/(?P<id>[^/]+)\/?$
        regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        regex = regex.rstrip('/')  # Ensure we don't double the slash
        return f"^{regex}/?$"

    async def __call__(self, scope, receive, send):
        print('🔍 Incoming request:', scope["method"], scope["path"])

        if scope["type"] != "http":
            await super().__call__(scope, receive, send)
            return

        request = Request(scope, receive)
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
                }
                response = await action(request, **request_context)

                if response is not None:
                    await response(scope, receive, send)
                    return

                # Now render a template if no response was returned
                controller_name = controller_class.__name__.replace("Controller", "").lower()
                template_name = f"{controller_name}/{action_name}.html"
                template_context = {"request": request}
                html_response = self.templates.TemplateResponse(name = template_name, context = template_context)
                await html_response(scope, receive, send)
                return


        response = Response("404 Not Found", status_code=404)
        await response(scope, receive, send)