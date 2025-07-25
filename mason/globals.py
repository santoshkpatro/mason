# mason/globals.py
_settings = None

def set_settings(settings_obj):
    global _settings
    _settings = settings_obj

def get_settings():
    if _settings is None:
        raise RuntimeError("Settings not initialized")
    return _settings
