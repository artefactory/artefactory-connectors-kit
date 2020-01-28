from functools import update_wrapper
import logging


def processor(*sensitive_fields):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """

    def wrapper(f):
        def new_func(*args, **kwargs):

            _kwargs = {}

            for key, value in kwargs.items():
                if key in sensitive_fields:
                    _kwargs[key] = "*****"
                else:
                    _kwargs[key] = value

            logging.info("Calling %s with (%s)", f.__name__, _kwargs)

            def processor():
                return f(*args, **kwargs)

            return update_wrapper(processor, f)

        return update_wrapper(new_func, f)

    return wrapper
