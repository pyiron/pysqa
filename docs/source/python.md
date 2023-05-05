# Python Interface
The `pysqa` package primarily defines one class, that is the `QueueAdapter`. It loads the configuration from a configuration directory, initializes the corrsponding adapter for the specific queuing system and provides a high level interface for users to interact with the queuing system. The `QueueAdapter` can be imported using:
```
from pysqa import QueueAdapter
```
After the initial import the class is initialized using the configuration directory specificed by the `directory` parameter which defaults to `"~/.queues"`: 
```
qa = QueueAdapter(directory="~/.queues")
```
Another optional parameter of the `QueueAdapter` class is the `execute_command`, still this is primarily used for testing purposes to call the underlying shell commands. 

## List available queues 
List available queues as list of queue names: 
```
qa.queue_list
```
List available queues in an pandas dataframe: 
```
qa.queue_view
```

## Submit job to queue
Submit a job to the queue - if no queue is specified it is submitted to the default queue defined in the queue configuration:
```
qa.submit_job(
    queue=None,
    job_name=None,
    working_directory=None,
    cores=None,
    memory_max=None,
    run_time_max=None,
    dependency_list=None,
    command=‘python test.py’,
    **kwargs
)
```

## Show jobs in queue 
Get status of all jobs currently handled by the queuing system:
```
qa.get_queue_status()
```
Get status of a specifc job from the queuing system:
```
qa.get_status_of_job(process_id=1234)
```

## Delete job from queue 
Delete a job from the queuing sytem:
```
qa.delete_job(process_id=1234)
```