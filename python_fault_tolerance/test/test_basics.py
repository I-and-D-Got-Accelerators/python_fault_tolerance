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
import datetime
import sys
import pprint

# this should not be here, resolve search path configuration in tools!
sys.path.append('c:/Users/fsveide/Documents/gitresp/python_fault_tolerance-1/python_fault_tolerance/src')
pprint.pprint(sys.path)

import fault_tolerance

class TestSuite:

    def test_basic_fault(self):
        try:
            @fault_tolerance.forward_err_recovery_by_retry()
            def dummy():
                pass
            assert False
        except:
            pass

    def test_faulty_retries_beneath_zero(self):
        correct = False
        try:
            @fault_tolerance.forward_err_recovery_by_retry(max_no_of_retries=0)
            def dummy2():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError:
            correct = True
        finally:
            assert correct

    def test_faulty_exc_lst_spec1(self):
        correct = False

        try:
            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[1])
            def dummy2():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError:
            correct = True
        finally:
            assert correct

    def test_faulty_exc_lst_spec2(self):
        correct = False
        try:
            class DummyException(Exception):
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException,1])
            def dummy2():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError:
            correct = True
        finally:
            assert correct

    def test_correct_exc_lst_spec1(self):
        correct = True
        try:
            class DummyException(Exception):
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException])
            def dummy3():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError:
            correct = False
        finally:
            assert correct

    def test_incorrect_backoff_spec1(self):
        correct = False
        try:
            class DummyException(Exception):
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=1)
            def dummy4():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:
            correct = True
            print(e)
        finally:
            assert correct

    def test_incorrect_backoff_spec2(self):
        correct = False
        try:
            class DummyException(Exception):
                pass

            def incorrect_backoff1() -> float:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff1)
            def dummy5():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:
            correct = True
            print(e)
        finally:
            assert correct

    def test_incorrect_backoff_spec3(self):
        correct = False
        try:
            class DummyException(Exception):
                pass

            def incorrect_backoff2(attempt) -> float:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff2)
            def dummy6():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:
            correct = True
            print(e)
        finally:
            assert correct

    def test_incorrect_backoff_spec4(self):
        correct = False
        try:
            class DummyException(Exception):
                pass

            def incorrect_backoff3(attempt: float) -> float:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff3)
            def dummy7():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:
            correct = True
            print(e)
        finally:
            assert correct

    def test_incorrect_backoff_spec5(self):
        correct = False
        try:
            class DummyException(Exception):
                pass

            def incorrect_backoff4(attempt: int) -> bool:
                pass

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff4)
            def dummy8():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:
            correct = True
            print(e)
        finally:
            assert correct

    def test_correct_backoff_spec1(self):
        correct = True
        try:   
            class DummyException(Exception):
                pass

            def incorrect_backoff5(attempt: int) -> float:
                return attempt * 0.1

            @fault_tolerance.forward_err_recovery_by_retry(exc_lst=[DummyException], backoff_duration_fn=incorrect_backoff5)
            def dummy8():
                pass
            assert correct
        except fault_tolerance.IncorrectFaultToleranceSpecificationError as e:
            correct = False
            print(e)
        finally:
            assert correct

class TestBackoffSuite:

    _backoff_count = 0
    _backoff_max_no_of_retries = 10
    _backoff_time_delta = 0.1

    def test_backoff(self):
        """Test that backoff functionality works in the sense that the delays caused are reasonable and that 
           the decorated function is called the specified number of times. """

        # backoff duration time function for this test case
        def backoff(attempt: int) -> float:
            return TestBackoffSuite._backoff_time_delta

        # the simulated exception use to denote the failure of the instrumented function 
        class DummyException(Exception):
            pass

        try:
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
        except fault_tolerance.IncorrectFaultToleranceSpecificationError:
            assert False
