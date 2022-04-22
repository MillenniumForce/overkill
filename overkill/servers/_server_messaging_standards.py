"""
This module contains variables that outline
certains standards of how servers should
interact with each other
"""

# User messaging standards:
DISTRIBUTE = "distribute"  # ask master to distribute task

# Master messaging standards:
NEW_CONNECTION = "new_connect"  # recieve connection from a worker
REJECT = "reject"  # reject a worker that is trying to connect to master
ACCEPT = "accept"  # accept a worker that is trying to connect to master
DELEGATE_WORK = "delegate_work"  # delegate work to a worker
FINISHED_TASK = "finished_task"  # task from user has been completely finished
# error when there are no workers when the user asks for work
NO_WORKERS_ERROR = "no_workers_error"

# Worker messsaging standards:
CLOSE_CONNECTION = "close"  # close connection with master
ACCEPT_WORK = "accept_work"  # accept work from a worker
WORK_ERROR = "work_error"  # error when computing the function on the array
