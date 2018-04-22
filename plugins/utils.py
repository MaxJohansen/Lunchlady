import logging
import sys
from os import path, listdir
from importlib import import_module
logger = logging.getLogger(f"doris.{__name__}")

dirname = path.dirname(__file__)
sys.path.insert(0, dirname)
files = listdir(dirname)
plugin_paths = [x for x in files if path.isdir(
    path.join(dirname, x)) and x != '__pycache__']
if 'core' in plugin_paths:
    plugin_paths.remove('core')
    plugin_paths.insert(0, 'core')


def plugin_loader():
    logger.debug(f"Importing plugins: {plugin_paths}")

    plugins = []

    for plugin in plugin_paths:
        dotted_path = f"{plugin}.{plugin}"
        class_name = plugin.capitalize()

        logger.info(f"Importing {class_name} from {dotted_path}")

        try:
            mod = import_module(dotted_path)
        except ImportError:
            logger.warning(
                f"Unable to import plugin '{plugin}'. Ensure that it contains a file with the same name as the directory.")
            continue

        try:
            klass = getattr(mod, class_name)
        except AttributeError:
            logger.warning(
                f"Unable to find class {class_name} in {mod.__file__}")
            continue
        plugins.append(klass)
    return plugins
