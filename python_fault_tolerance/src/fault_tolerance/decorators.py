#MIT License
#
#Copyright (c) 2022 I-and-D-Got-Accelerators
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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
        raise IncorrectFaultToleranceSpecificationError(f"The parameter max_no_of_retries is not an int, but a {type(max_no_of_retries)}"
                                                        f" or the value is beneath zero (max_no_of_retries={max_no_of_retries})")

    # check exc_lst
    if not isinstance(exc_lst, list) or len(exc_lst) < 1 or any(map(lambda element: not _is_subclass(element, Exception), exc_lst)):
        raise IncorrectFaultToleranceSpecificationError(f"The parameter exc_lst is incorrect, expected a list of exceptions, but got '{exc_lst}'")

    if backoff_duration_fn is not None:
        if not isinstance(backoff_duration_fn, PT.Callable):
            raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but got '{backoff_duration_fn}'")
        fas: inspect.FullArgSpec = inspect.getfullargspec(backoff_duration_fn)
        if len(fas.args) != 1:
            raise IncorrectFaultToleranceSpecificationError(f"The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, "
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
        class DummyException(Exception):
            pass
        def backoff(attempt: int) -> float:
            return attempt*0.1


        @forward_err_recovery_by_retry(max_no_of_retries= 3, exc_lst=[DummyException], backoff_duration_fn= backoff)
        def dummy():
            raise DummyException()
        print("Incorrect")
    except IncorrectFaultToleranceSpecificationError:
        print("Incorrect")
    except FailedToRecoverError:
        print("Correct")
    dummy()
    print("And done")
    

