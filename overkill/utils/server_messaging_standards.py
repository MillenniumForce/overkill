"""
This module contains variables that outline
certains standards of how servers should
interact with each other
"""

# User messaging standards:
_DISTRIBUTE = "distribute"  # ask master to distribute task

# Master messaging standards:
_NEW_CONNECTION = "new_connect"  # recieve connection from a worker
_REJECT = "reject"  # reject a worker that is trying to connect to master
_ACCEPT = "accept"  # accept a worker that is trying to connect to master
_DELEGATE_WORK = "delegate_work"  # delegate work to a worker
_FINISHED_TASK = "finished_task"  # task from user has been completely finished
_NO_WORKERS_ERROR = "no_workers_error" # error when there are no workers when the user asks for work

# Worker messsaging standards:
_CLOSE_CONNECTION = "close"  # close connection with master
_ACCEPT_WORK = "accept_work"  # accept work from a worker
_WORK_ERROR = "work_error" # error when computing the function on the array
