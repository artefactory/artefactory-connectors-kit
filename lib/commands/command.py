from functools import update_wrapper


def processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """
    def new_func(*args, **kwargs):
        def processor():
            return f(*args, **kwargs)

        return update_wrapper(processor, f)
    return update_wrapper(new_func, f)
