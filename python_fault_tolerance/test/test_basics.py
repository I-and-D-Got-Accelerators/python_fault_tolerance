import pytest
import datetime
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

    def test_backoff(self):
        def backoff(attempt: int) -> float:
            return attempt*1

        class DummyException(Exception):
            pass

        @fault_tolerance.forward_err_recovery_by_retry(max_no_of_retries=10, exc_lst=[DummyException], backoff_duration_fn=backoff)
        def simulated_faulty_function():
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
        print(f'Expected duration = 1 second, actual duration = {duration_sec} seconds')
        if duration_sec < 10*1:
            assert False
        else:
            assert True
