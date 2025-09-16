import inspect
from typing import Callable

def public(func: Callable):
    # Code: https://github.com/jongracecox/auto-all/blob/master/auto_all.py#L195
    """Decorator that adds a function to the modules __all__ list."""

    local_stack = inspect.stack()[1][0]

    global_vars = local_stack.f_globals

    if '__all__' not in global_vars:
        global_vars['__all__'] = []

    all_var = global_vars['__all__']

    all_var.append(func.__name__)

    return func

__all__ = ['public']