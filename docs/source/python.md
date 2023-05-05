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
The only required parameter is: 
* `command` the command that is executed as part of the job 

Additional options for the submission of the job are:
* `queue` the queue the job is submitted to. If this option is not defined the `primary_queue` defined in the configuration is used. 
* `job_name` the name of the job submitted to the queuing system. 
* `working_directory` the working directory the job submitted to the queuing system is executed in.
* `cores` the number of cores used for the calculation. If the cores are not defined the minimum number of cores defined for the selected queue are used. 
* `memory_max` the memory used for the calculation. 
* `run_time_max` the run time for the calculation. If the run time is not defined the maximum run time defined for the selected queue is used. 
* `dependency_list` other jobs the calculation depends on. 
* `**kwargs` allows writing additional parameters to the job submission script if they are available in the corresponding template.

## Show jobs in queue 
Get status of all jobs currently handled by the queuing system:
```
qa.get_queue_status()
```
With the additional parameter `user` a specific user can be defined to only list the jobs of this specific user. 

In analogy the jobs of the current user can be listed with: 
```
qa.get_status_of_my_jobs()
```

Finally, the status of a specific job with the queue id  `1234` can be received from the queuing system using:
```
qa.get_status_of_job(process_id=1234)
```

## Delete job from queue 
Delete a job with the queue id `1234` from the queuing system:
```
qa.delete_job(process_id=1234)
```