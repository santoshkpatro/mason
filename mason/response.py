from starlette.responses import JSONResponse

class MasonResponse(JSONResponse):
    def __init__(self, data=None, status_code=200, message=None, **kwargs):
        content = {
            "status": "success" if 200 <= status_code < 400 else "error",
            "message": message or self._default_message(status_code),
            "data": data
        }
        super().__init__(content=content, status_code=status_code, **kwargs)

    def _default_message(self, status_code):
        if status_code == 200:
            return "OK"
        elif status_code == 201:
            return "Created"
        elif status_code == 400:
            return "Bad Request"
        elif status_code == 404:
            return "Not Found"
        elif status_code == 500:
            return "Internal Server Error"
        return "Unknown Status"
