import logging
import inspect

class CRYSTALSBase:
    """ Base class, currently offers debug logs interface."""

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(message)s'
        )

    def debug(self, message):
        method_name = inspect.currentframe().f_back.f_code.co_name
        class_name = self.__class__.__name__
        logging.debug(f"{class_name}.{method_name}: {message}")