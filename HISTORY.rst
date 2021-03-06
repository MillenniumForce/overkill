=======
History
=======

0.1.0 (2022-04-10)
------------------

* Initial working version

0.2.0 (2022-04-17)
------------------

* Added functionality to notify master that worker has stopped (see #4)
* Huge increase in documentation
* More testing

0.2.1 (2022-04-17)
------------------

* Fixed regression in Master where dictionary items were used instead of values
* Fixed regression in Worker where _master may be None

0.3.0 (2022-04-18)
------------------

* Added initial user api (i.e. ClusterCompute class and map functionality)


0.3.1 (2022-04-18)
------------------

* Refactored utils into protected members (see issue #17)

0.3.2 (2022-04-18)
------------------

* Added error handling for when the user incorrectly specifies the function or array (see issue #5)

0.3.3 (2022-04-18)
------------------

* Refactored socket send and recieve protocols to handle large data

Notes: could be optimised further but experimentation is required

0.3.4 (2022-04-18)
------------------

* Added error when a user tries to distribute a task when there are no workers, user should now recieve a NoWorkersError

0.4.0 (2022-04-23)
------------------

* Abstracted master and worker classes into _master and _worker files respectively
* Refactored util modules into protected modules

0.4.1 (2022-04-25)
------------------

* Errors where the user might mispecify the function or array are caught by the Master server and raised with the user

0.4.2 (2022-04-25)
------------------

* Removed array from WorkOrder repr so logs aren't flooded. There is still a temporary issue that the entire array is printed when an ask is initially sent to master but will be amended in a future release. See issue #37

0.4.3 (2022-05-01)
------------------

* If the worker cannot notify the master that it is shutting down, log the error instead of spitting out an ugly traceback to the user

0.4.4 (2022-05-01)
------------------

* Updated docs for Master, ClusterCompute and Worker classes