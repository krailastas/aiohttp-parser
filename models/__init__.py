import inspect
import pkgutil

from sqlalchemy.ext.declarative import declarative_base


__all__ = ['Base']

Base = declarative_base()

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
