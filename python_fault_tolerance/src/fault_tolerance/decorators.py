import functools
import inspect
import time
import typing as PT

from fault_tolerance.Exceptions import IncorrectFaultToleranceSpecificationError, FailedToRecoverError

def _is_subclass(obj: PT.Any, cls: type) -> bool:

    """Replicating issubclass function, but hides 'TypeError' exception"""

    try:
        return issubclass(obj, cls)
    except TypeError:
        return False

def forward_err_recovery_by_retry(max_no_of_retries: int = 1, 
                                  exc_lst: PT.List[Exception] = [], 
                                  backoff_duration_fn: PT.Callable[[int], float] = None) -> PT.Callable:

    # check max_no_of_retries
    if not isinstance(max_no_of_retries, int) or max_no_of_retries < 1:
        raise IncorrectFaultToleranceSpecificationError(f"The parameter max_no_of_retries is not an int, but a {type(max_no_of_retries)}")

    # check exc_lst
    if not isinstance(exc_lst, list) or len(exc_lst) < 1 or any(map(lambda element: not _is_subclass(element, Exception), exc_lst)):
        raise IncorrectFaultToleranceSpecificationError(f"The parameter exc_lst is incorrect, expected a list of exceptions, but got '{exc_lst}'")

    if backoff_duration_fn is not None:
        if not isinstance(backoff_duration_fn, PT.Callable):
            raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but got '{backoff_duration_fn}'")
        fas: inspect.FullArgSpec = inspect.getfullargspec(backoff_duration_fn)
        if len(fas.args) != 1:
            raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float,"
                                                            f"but it takes {len(fas.args)} arguments")
        try:
            if not _is_subclass(fas.annotations[fas.args[0]], int):
                raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the argument is an {fas.annotations[fas.args[0]]}")
        except KeyError:
            raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the argument has no type annotation")

        try:
            if not _is_subclass(fas.annotations['return'], float):
                raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the functions returns an {fas.annotations['return']} instead")
        except KeyError:
                raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the functions returns None instead")



                                                                                                                                                                                                                                                                                                           
    def decorator(fx: PT.Callable) -> PT.Callable:
        functools.wraps(fx)
        def wrapper(*args, **kwargs):
            attempts_left: int = max_no_of_retries
            completed: bool = False
            while not completed:
                try:
                    return fx(*args, **kwargs)
                except Exception as e:
                    if any(map(lambda exc: isinstance(e, exc), exc_lst)):

                        attempts_left -= 1
                    else:
                        raise
                    time.sleep(backoff_duration_fn(max_no_of_retries - attempts_left) if backoff_duration_fn is not None else 0)
                finally:
                    if attempts_left < 1:
                        raise FailedToRecoverError(f"Failed to recover from exceptions after {max_no_of_retries} attempts")
        return wrapper
    return decorator

if __name__ == "__main__":
    print("Off we go")
    try:
        @forward_err_recovery_by_retry()
        def dummy():
            pass
        print("Incorrect")
    except IncorrectFaultToleranceSpecificationError:
        print("Correct")
    print("And done")

