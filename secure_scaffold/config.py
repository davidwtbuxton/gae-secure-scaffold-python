import os
import importlib

from secure_scaffold import settings as defaults

# It's weird that we have a whole other settings module to configure things
# instead of using Flask's configuration system.
# https://flask.palletsprojects.com/en/1.1.x/config/.
SETTINGS_MODULE_VAR = "SETTINGS_MODULE"

SETTINGS_MODULE = os.getenv(SETTINGS_MODULE_VAR)

if SETTINGS_MODULE:
    settings = importlib.import_module(SETTINGS_MODULE)
else:
    settings = None


def get_setting(name):
    # Bug? What if I want the value of None? The default here should be a
    # sentinel object.
    value = getattr(settings, name, None)

    if value is not None:
        return value
    try:
        return getattr(defaults, name)
    except AttributeError:
        raise AttributeError(f'Setting "{name}"" does not exist, please define it.')
