def mount(base_path: str):
    def decorator(cls):
        setattr(cls, "__mount_path__", base_path)
        return cls
    return decorator

def route(method, path):
    def decorator(func):
        if not hasattr(func, "__routes__"):
            func.__routes__ = []
        func.__routes__.append((method.upper(), path))
        return func
    return decorator

def get(path): return route("GET", path)
def post(path): return route("POST", path)
def put(path): return route("PUT", path)
def delete(path): return route("DELETE", path)
def patch(path): return route("PATCH", path)