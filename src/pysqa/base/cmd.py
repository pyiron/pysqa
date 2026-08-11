import getopt
import json
import os
import sys
from typing import Callable, Optional

from pysqa.base.core import execute_command
from pysqa.queueadapter import QueueAdapter


def command_line(
    arguments_lst: Optional[list] = None, execute_command: Callable = execute_command
) -> None:
    """
    Parse the command line arguments.

    Args:
        arguments_lst (Optional[list]): Command line arguments
        execute_command (Callable): Function to communicate with shell process

    Returns:
        None
    """
    directory = "~/.queues"
    queue = None
    job_name = None
    working_directory = None
    cores = 1
    memory_max = None
    run_time_max = None
    command = None
    job_id = None
    if arguments_lst is None:
        arguments_lst = sys.argv[1:]
    try:
        opts, args = getopt.getopt(
            arguments_lst,
            "f:pq:j:w:n:m:t:b:c:ri:dslh",
            [
                "config_directory=",
                "submit",
                "queue=",
                "job_name=",
                "working_directory=",
                "cores=",
                "memory=",
                "run_time=",
                "dependency=",
                "command=",
                "reservation",
                "id=",
                "delete",
                "status",
                "list",
                "help",
            ],
        )
    except getopt.GetoptError:
        print(_help_message())
    else:
        mode_submit = False
        mode_delete = False
        mode_reservation = False
        mode_status = False
        mode_list = False
        dependency_list = []
        for opt, arg in opts:
            if opt in ("-f", "--config_directory"):
                directory = arg
            elif opt in ("-p", "--submit"):
                mode_submit = True
            elif opt in ("-q", "--queue"):
                queue = arg
            elif opt in ("-j", "--job_name"):
                job_name = arg
            elif opt in ("-w", "--working_directory"):
                working_directory = arg
            elif opt in ("-n", "--cores"):
                cores = int(arg)
            elif opt in ("-m", "--memory"):
                memory_max = arg
            elif opt in ("-t", "--run_time"):
                run_time_max = int(arg)
            elif opt in ("-c", "--command"):
                command = arg
            elif opt in ("-r", "--reservation"):
                mode_reservation = True
            elif opt in ("-i", "--id"):
                if arg != "":
                    job_id = int(arg)
            elif opt in ("-d", "--delete"):
                mode_delete = True
            elif opt in ("-s", "--status"):
                mode_status = True
            elif opt in ("-l", "--list"):
                mode_list = True
            elif opt in ("-b", "--dependency"):
                dependency_list.append(int(arg))
        if mode_submit or mode_delete or mode_reservation or mode_status:
            qa = QueueAdapter(directory=directory, execute_command=execute_command)
            if mode_submit:
                print(
                    qa.submit_job(
                        queue=queue,
                        job_name=job_name,
                        working_directory=working_directory,
                        cores=cores,
                        memory_max=memory_max,
                        run_time_max=run_time_max,
                        dependency_list=dependency_list,
                        command=command,
                    )
                )
            elif mode_delete:
                if job_id is not None:
                    print(qa.delete_job(process_id=job_id))
                else:
                    raise ValueError("Job ID not provided")
            elif mode_reservation:
                if job_id is not None:
                    print(qa.enable_reservation(process_id=job_id))
                else:
                    raise ValueError("Job ID not provided")
            elif mode_status:
                print(json.dumps(qa.get_queue_status().to_dict(orient="list")))
        elif mode_list and working_directory is not None:
            working_directory = os.path.abspath(os.path.expanduser(working_directory))
            remote_dirs, remote_files = [], []
            for p, _folder, files in os.walk(working_directory):
                remote_dirs.append(p)
                if p is not None:
                    remote_files += [os.path.join(p, f) for f in files if f is not None]
            print(
                json.dumps({"dirs": sorted(remote_dirs), "files": sorted(remote_files)})
            )
        else:
            print(_help_message())


def _help_message() -> str:
    return """\
usage: python -m pysqa [options]

Command line interface to submit, monitor and delete jobs on the queuing
system configured in the pysqa configuration directory.

Submit job:
  -p, --submit                  submit a new job to the queuing system
  -c, --command=COMMAND         command to execute as part of the job
  -q, --queue=QUEUE             queue to submit to (default: primary_queue)
  -j, --job_name=NAME           name of the submitted job
  -w, --working_directory=DIR   working directory the job is executed in
  -n, --cores=N                 number of cores to use (default: minimum for queue)
  -m, --memory=MEMORY           memory to reserve for the job
  -t, --run_time=SECONDS        maximum run time (default: maximum for queue)
  -b, --dependency=ID           job id this job depends on (repeatable)

  Example: python -m pysqa --submit --command hostname

Enable reservation:
  -r, --reservation             enable a reservation for an already submitted job
  -i, --id=ID                   job id to add to the reservation

  Example: python -m pysqa --reservation --id 123

List jobs on the queuing system:
  -s, --status                  list status of all jobs on the queuing system

  Example: python -m pysqa --status

Delete job:
  -d, --delete                  delete a job from the queuing system
  -i, --id=ID                   job id to delete

  Example: python -m pysqa --delete --id 123

List files:
  -l, --list                    list files in the working directory
  -w, --working_directory=DIR   directory whose files are listed

  Example: python -m pysqa --list --working_directory /path/on/remote/hpc

General options:
  -f, --config_directory=DIR    pysqa configuration directory (default: ~/.queues)
  -h, --help                    print this help message

Full documentation: https://pysqa.readthedocs.io/en/latest/command.html
"""
