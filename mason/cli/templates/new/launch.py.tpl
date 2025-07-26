# launch.py
from config import settings
from mason.globals import set_settings
from mason.application import MasonApplication

set_settings(settings)
app = MasonApplication()
