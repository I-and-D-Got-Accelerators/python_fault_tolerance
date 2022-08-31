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

import pytest
import contextlib
import datetime
import inspect
import re
import sys
import typing as PT
import pprint

# this should not be here, resolve search path configuration in tools!
sys.path.append('c:/Users/fsveide/Documents/gitresp/python_fault_tolerance-1/python_fault_tolerance/src')
pprint.pprint(sys.path)

import fault_tolerance

def _expected_exception_str(expected: bool, exc: Exception) -> str:
    """Transforms if behavior is expected or not and the exception to a string
       representing the result. There are four options"""
    if expected:

        if exc is not None:
            return f"Expected exception = {type(exc)}('{exc}') occurred"

        return f"Unexpectedly, no exception occurred"
    
    if exc is not None:
        return f"Unexpected exception = {type(exc)}('{exc}') occurred"

    return f"As expected, no exception occurred"

def _is_subclass(cls: type, sup_cls: type) -> bool:
    try:
        return issubclass(cls, sup_cls)
    except TypeError:
        return False

def par(txt_str, v):
    print(f"{txt_str}={v}")
    return v

@contextlib.contextmanager
def assert_and_report_expectation_status(expected_exc_lst: PT.List[Exception] = [], 
                                         report_fn = lambda expected_behavior, exc: print(_expected_exception_str(expected_behavior, exc)),
                                         expected_exc_re: re.Pattern = None) -> PT.NoReturn:

    # check types and constraints of input parameters

    # expected_exc_lst is a list
    assert isinstance(expected_exc_lst, list)
    
    # all elements in expected_exc_lst is an Exception
    assert all(map(lambda exc_el: _is_subclass(exc_el, Exception), expected_exc_lst))

    # check if report_fn is a function
    assert isinstance(report_fn, PT.Callable)

    #check that report_fn takes two arguments
    fas: inspect.FullArgSpec = inspect.getfullargspec(report_fn)
    assert len(fas.args) == 2

    # check that expected_exc_re is a re.Pattern
    assert expected_exc_re is None or isinstance(expected_exc_re, re.Pattern)

    try:

        # this is where the code enclosed in the "with" statement is executed
        yield

        # after the code enclosed in the with statement has been executed without any exception, 
        # the programe execution ends up here:

        # check if we expected an exception or not, report and assert accordingly

        if len(expected_exc_lst) > 0:
            report_fn(True, None)
            assert False
        else:
            report_fn(False, None)
            assert True

    except Exception as exc:

        # an exception occurred, check if it is an expected exception
        # and if it is an expected exception, check if it matches the regular exception, 
        # if any. Report and assert accordingly.

        if any(map(lambda exc_el: isinstance(exc, exc_el), expected_exc_lst)):

            # check if expected_exc_re is not None and a re.Pattern, if it is, then we 
            # have a regular expression that should be matched

            if isinstance(expected_exc_re, re.Pattern):
                if expected_exc_re.match(str(exc)):
                    report_fn(True, exc)
                    assert True
                else:
                    report_fn(False, exc)
                    assert False
            else:
                report_fn(True, exc)
                assert True
        else:
            report_fn(False, exc)
            assert False




class TestSuite:


    def test_basic_fault(self):

        """Tests the error-detection concerning the specification,
           basic case, no arguments passed to the decorator. This implies
           that defaults are used, but defaults are incorrect since the decorator
           must be used with care."""

        exc_lst_err_msg_basic_fault_re: re.Pattern = re.compile(r"^The parameter exc_lst is incorrect, expected a list of exceptions, but got '\[\]'$")

        try:

            @fault_tolerance.forward_err_recovery_by_retry()
            def dummy():
                pass

            assert False

        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:

            if not exc_lst_err_msg_basic_fault_re.match(str(e)):
                assert False

    def test_basic_fault2(self):

        """Replication of test_basic_fault, to demonstrate effect of contextmanager"""

        exc_lst_err_msg_basic_fault_re: re.Pattern = re.compile(r"^The parameter exc_lst is incorrect, expected a list of exceptions, but got '\[\]'$")

        with assert_and_report_expectation_status(expected_exc_lst = [fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                  expected_exc_re = exc_lst_err_msg_basic_fault_re):

            @fault_tolerance.forward_err_recovery_by_retry()
            def dummy():
                pass

    def test_faulty_retries_beneath_zero(self):
        """Tests the error-detection concerning the specification,
           basic case, incorrect max_no_of_retries"""

        exc_lst_err_msg_retries_beneath_zero_re: re.Pattern = re.compile(r"^The parameter max_no_of_retries is not an int, but a .* or the value is beneath zero \(max_no_of_retries=.*\)$")

        correct = False

        try:

            @fault_tolerance.forward_err_recovery_by_retry(max_no_of_retries=0)
            def dummy2():
                pass

            assert correct

        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:

            if exc_lst_err_msg_retries_beneath_zero_re.match(str(e)):
                correct = True

        finally:

            assert correct

    def test_faulty_retries_beneath_zero2(self):

        """Replication of test_faulty_retries_beneath_zero"""

        exc_lst_err_msg_retries_beneath_zero_re: re.Pattern = re.compile(r"^The parameter max_no_of_retries is not an int, but a .* or the value is beneath zero \(max_no_of_retries=.*\)$")

        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                            expected_exc_re = exc_lst_err_msg_retries_beneath_zero_re):

            @fault_tolerance.forward_err_recovery_by_retry(max_no_of_retries=0)
            def dummy2():
                pass



    def test_faulty_exc_lst_spec1(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, but incorrect empty
           list of exceptions. """

        exc_lst_err_msg_faulty_exc_lst_spec1_re: re.Pattern = re.compile(r"^The parameter exc_lst is incorrect, expected a list of exceptions, but got '\[.*1.*\]'$")

        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                            expected_exc_re = exc_lst_err_msg_faulty_exc_lst_spec1_re):


            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[1])
            def dummy2():
                pass



    def test_faulty_exc_lst_spec2(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, but incorrect 
           list of exceptions that includes a non-exception value. """

        exc_lst_err_msg_faulty_exc_lst_spec2_re: re.Pattern = re.compile(r"^The parameter exc_lst is incorrect, expected a list of exceptions, but got '\[.*,.*1.*\]'$")

        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                   expected_exc_re = exc_lst_err_msg_faulty_exc_lst_spec2_re):

            class DummyException(Exception):
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException,1])
            def dummy2():
                pass


    def test_correct_exc_lst_spec_and_default_backoff_duration_fn(self):

        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, but correct 
           list of exceptions. """

        with assert_and_report_expectation_status():

            class DummyException(Exception):
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException])
            def dummy3():
                pass


    def test_incorrect_backoff_as_integer_spec1(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, correct 
           list of exceptions, but incorrect backoff_duration_fn. 
           
           Providing a non-function to the argument. """

        incorrect_backoff_as_integer_spec1_re: re.Pattern = re.compile(r"^The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but got '.*'$")


        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                   expected_exc_re = incorrect_backoff_as_integer_spec1_re):


            class DummyException(Exception):
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=1)
            def dummy4():
                pass


    def test_incorrect_backoff_no_args_spec2(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, correct 
           list of exceptions, but incorrect backoff_duration_fn. 
           
           No attempt parameter specified. """

        incorrect_backoff_no_args_spec2_re: re.Pattern = re.compile(r"^The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but it takes \d+ arguments$")

        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                  expected_exc_re = incorrect_backoff_no_args_spec2_re):
            class DummyException(Exception):
                pass

            def incorrect_backoff1() -> float:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff1)
            def dummy5():
                pass


    def test_incorrect_backoff_no_arg_typing_hint_spec3(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, correct 
           list of exceptions, but incorrect backoff_duration_fn. 
           
           No type annotation of the attempt parameter."""

           
        incorrect_backoff_no_arg_typing_hint_spec3_re: re.Pattern = re.compile(r"^The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the argument has no type annotation$")

        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                  expected_exc_re = incorrect_backoff_no_arg_typing_hint_spec3_re):

            class DummyException(Exception):
                pass

            def incorrect_backoff2(attempt) -> float:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff2)
            def dummy6():
                pass

    def test_incorrect_backoff_incorrect_arg_typing_hint_spec4(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, correct 
           list of exceptions, but incorrect backoff_duration_fn. 
           
           Incorrect typing hint on the attempt parameter."""
        
        incorrect_backoff_incorrect_arg_typing_hint_spec4_re: re.Pattern = re.compile(r"^The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the argument is an .*$")

        with assert_and_report_expectation_status(expected_exc_lst=[fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                  expected_exc_re = incorrect_backoff_incorrect_arg_typing_hint_spec4_re):

            class DummyException(Exception):
                pass

            def incorrect_backoff3(attempt: float) -> float:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff3)
            def dummy7():
                pass


    def test_incorrect_backoff_incorrect_return_typing_hint_spec5(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, correct 
           list of exceptions, but incorrect backoff_duration_fn. 
           
           Incorrect typing hint on the return parameter."""

        incorrect_backoff_incorrect_return_typing_hint_spec5_re: re.Pattern = re.compile(r"^The parameter backoff_duration_fn is incorrect, expected a function taking an int returning a float, but the functions returns an .* instead$")
 
        with assert_and_report_expectation_status(expected_exc_lst = [fault_tolerance.IncorrectFaultToleranceSpecificationError],
                                                  expected_exc_re = incorrect_backoff_incorrect_return_typing_hint_spec5_re):
            class DummyException(Exception):
                pass

            def incorrect_backoff4(attempt: int) -> bool:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff4)
            def dummy8():
                pass

    def test_correct_backoff_spec1(self):
        """Tests the error-detection concerning the specification,
           basic case, default max_no_of_retries, correct 
           list of exceptions and an incorrect backoff_duration_fn."""

        with assert_and_report_expectation_status():
            class DummyException(Exception):
                pass

            def incorrect_backoff5(attempt: int) -> float:
                return attempt * 0.1

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff5)
            def dummy8():
                pass
    
class TestBackoffSuite:

    _backoff_count = 0
    _backoff_max_no_of_retries = 10
    _backoff_time_delta = 0.1

    def test_backoff(self):
        """Test that backoff functionality works in the sense that the delays caused are reasonable and that 
           the decorated function is called the specified number of times. """

        with assert_and_report_expectation_status():


            # backoff duration time function for this test case
            def backoff(attempt: int) -> float:
                return TestBackoffSuite._backoff_time_delta

            # the simulated exception use to denote the failure of the instrumented function 
            class DummyException(Exception):
                pass

            # definition of the simulated faulty function
            @fault_tolerance.forward_err_recovery_by_retry(max_no_of_retries=TestBackoffSuite._backoff_max_no_of_retries, 
                                                            exc_lst=[DummyException], 
                                                            backoff_duration_fn=backoff)
            def simulated_faulty_function():
                TestBackoffSuite._backoff_count += 1
                raise DummyException()

            t1 = datetime.datetime.now()
            try:
                simulated_faulty_function()
                assert False
            except fault_tolerance.FailedToRecoverError:
                pass
            t2 = datetime.datetime.now()
            duration_td = t2-t1
            duration_sec = duration_td.seconds+duration_td.microseconds/1000000.0
            print(f'Expected duration = {10*TestBackoffSuite._backoff_time_delta} second, actual duration = {duration_sec} seconds')
            if (duration_sec < TestBackoffSuite._backoff_max_no_of_retries*TestBackoffSuite._backoff_time_delta  or 
                TestBackoffSuite._backoff_count!= 10):
                assert False
            else:
                assert True
