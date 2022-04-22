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