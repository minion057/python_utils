import time

from pytoolbox4dev.decorators.public_decorator import *

@public
def measure_execution_time(func, *args, **kwargs):
    """Measures and prints the execution time of a given function.

    This function acts as a wrapper to time another function's execution.
    It captures the start and end times using `time.perf_counter()` for
    high precision. If the wrapped function raises an exception, it prints
    the elapsed time until the exception and then re-raises it.

    Parameters
    ----------
    func : callable
        The function to be executed and timed.
    *args
        Variable length argument list to be passed to `func`.
    **kwargs
        Arbitrary keyword arguments to be passed to `func`.

    Returns
    -------
    Any
        The result returned by the executed function `func`.

    Raises
    ------
    Exception
        Re-raises any exception that occurs during the execution of `func`.
    """
    
    start_time = time.perf_counter()
    error = None
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        error = e
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    error_str = '' if error is None else ' before error'
    print(f'Execution time{error_str}: {execution_time:.6f} seconds')
    if error is not None:
        raise error
    return result