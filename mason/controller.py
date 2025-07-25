class MasonController:
    def __init__(self):
        self._template_context = {}

    def set_data(self, key, data):
        """Set data in the template context."""
        self._template_context[key] = data