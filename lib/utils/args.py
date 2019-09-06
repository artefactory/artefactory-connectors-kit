def deprefix(prefix, d):
    return {k.replace(prefix, '', 1): v for k, v in d.iteritems()}


def extract_args(prefix, d, remove_prefix=True):
    args = {k: v for k, v in d.iteritems() if k.startswith(prefix)}

    if remove_prefix:
        args = deprefix(prefix, args)

    return args


def has_arg(arg, kwargs):
    return arg in kwargs and kwargs[arg] is not None


def hasnt_arg(arg, kwargs):
    return not has_arg(arg, kwargs)
