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

@public
def start_timer():
    """
    Returns the current high-resolution time.

    This function captures the current time using time.perf_counter(),
    which provides the highest available resolution timer on the system,
    suitable for measuring short durations accurately.

    Returns
    -------
    float
        The current time in seconds as a floating point number.
    """
    return time.perf_counter()

@public
def stop_timer(start_time, return_time=False):
    """
    Calculate and output or return elapsed time since the start time.

    Parameters
    ----------
    start_time : float
        The start time obtained from `start_timer()`.
    return_time : bool, optional
        If True, the function returns the elapsed time instead of printing it.
        Default is False.

    Returns
    -------
    float or None
        Returns the elapsed time in seconds if `return_time` is True.
        Otherwise, returns None.
    """
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f'Elapsed time: {elapsed:.6f} seconds')
    if return_time:
        return elapsed