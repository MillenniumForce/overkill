# Universal encoding
ENCODING = "utf-8"

# User messaging standards:
DISTRIBUTE = "distribute" # ask master to distribute task

# Master messaging standards:
NEW_CONNECTION = "new_connect" # recieve connection from a worker
REJECT = "reject" # reject a worker that is trying to connect to master
ACCEPT = "accept" # accept a worker that is trying to connect to master
DELEGATE_WORK = "delegate_work" # delegate work to a worker
ACCEPT_WORK = "accept_work" # accept work from a worker
FINISHED_TASK = "finished_task" # task from user has been completely finished

# Worker messsaging standards
CLOSE_CONNECTION = "close" # close connection with master
