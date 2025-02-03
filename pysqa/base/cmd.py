import getopt
import json
import os
import sys
from typing import Optional

from pysqa.base.core import execute_command
from pysqa.queueadapter import QueueAdapter


def command_line(
    arguments_lst: Optional[list] = None, execute_command: callable = execute_command
) -> None:
    """
    Parse the command line arguments.

    Args:
        arguments_lst (Optional[list]): Command line arguments
        execute_command (callable): Function to communicate with shell process

    Returns:
        None
    """
    directory = "~/.queues"
    queue = None
    job_name = None
    working_directory = None
    cores = None
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
        print("python -m pysqa --help")
    else:
        mode_submit = False
        mode_delete = False
        mode_reservation = False
        mode_status = False
        mode_list = False
        dependency_list = None
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
                run_time_max = arg
            elif opt in ("-c", "--command"):
                command = arg
            elif opt in ("-r", "--reservation"):
                mode_reservation = arg
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
                if dependency_list is None:
                    dependency_list = [arg]
                else:
                    dependency_list.append(arg)
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
                print(qa.delete_job(process_id=job_id))
            elif mode_reservation:
                print(qa.enable_reservation(process_id=job_id))
            elif mode_status:
                print(json.dumps(qa.get_queue_status().to_dict(orient="list")))
        elif mode_list:
            working_directory = os.path.abspath(os.path.expanduser(working_directory))
            remote_dirs, remote_files = [], []
            for p, _folder, files in os.walk(working_directory):
                remote_dirs.append(p)
                remote_files += [os.path.join(p, f) for f in files]
            print(
                json.dumps({"dirs": sorted(remote_dirs), "files": sorted(remote_files)})
            )
        else:
            print("python -m pysqa --help ... coming soon.")
