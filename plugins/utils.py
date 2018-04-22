import logging
import sys
from os import path, listdir
from importlib import import_module
logger = logging.getLogger('doris.plugins')

dirname = path.dirname(__file__)
sys.path.insert(0, dirname)
files = listdir(dirname)
plugin_paths = [x for x in files if path.isdir(
    path.join(dirname, x)) and x != '__pycache__']


def plugin_loader():
    logger.debug(f"Importing plugins: {plugin_paths}")

    plugins = []

    for path in plugin_paths:
        dotted_path = f"{path}.{path}"
        class_name = path.capitalize()

        logger.info(f"Importing {class_name} from {dotted_path}")

        try:
            mod = import_module(dotted_path)
        except ImportError:
            raise ImportError(
                f"Unable to import plugin '{path}'. Ensure that it contains a file with the same name as the directory.")

        try:
            klass = getattr(mod, class_name)
        except AttributeError:
            raise ImportError(
                f"Unable to find class {class_name} in {mod.__file__}")
        plugins.append(klass)
    return plugins
