# Python fault tolerance package
The purpose of this package is to provide a declarative approach to specifying error-detection and recovery
behavior to functions or methods in Python.

## Motivation
The reason is that using exceptions for error-detection for recovery is not straight-forward. For example, it is critical to synchronize the program state including
the execution point with respect to related resources while recovering. Further, it is desirable to detail what exceptions are recoverable and what exceptions are not.
Finally, existing approaches in DAGS are often coarse in many aspects, for example, they are typically catch-all exceptions, offer a fixed time interval between retries 
and work on larger code blocks than mere functions or methods.

