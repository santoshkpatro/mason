from mason.routing import mount, get
from mason.controller import MasonController
from mason.response import MasonResponse

@mount("/")
class HomeController(MasonController):
    @get("/")
    def index(self, **context):
        return MasonResponse(data={"message": "Welcome to Mason Project"})

    @get("/about")
    def about(self, **context):
        return MasonResponse(data={"message": "About"})
