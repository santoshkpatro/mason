from mason.routing import mount, get
from mason.controller import MasonController
from mason.response import MasonResponse

@mount("/{{ name }}")
class {{ class_name }}Controller(MasonController):
    @get("/")
    def index(self, **context):
        return MasonResponse(data={"message": "Welcome to {{ class_name }} Controller"})

    @get("/about")
    def about(self, **context):
        return MasonResponse(data={"message": "About {{ class_name }}"})
