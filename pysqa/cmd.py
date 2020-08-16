import sys
import os
import json
import getopt
from pysqa.queueadapter import QueueAdapter


def command_line(argv):
    """
    Parse the command line arguments.

    Args:
        argv: Command line arguments

    """
    directory = "~/.queues"
    queue = None,
    job_name = None,
    working_directory = None,
    cores = None,
    memory_max = None,
    run_time_max = None,
    command = None,
    job_id = None
    try:
        opts, args = getopt.getopt(
            argv, "f:pq:j:w:n:m:t:c:ri:dslh", ["config_directory=", "submit", "queue=", "job_name=",
                                               "working_directory=", "cores=", "memory=", "run_time=",
                                               "command=", "reservation", "id", "delete", "status", "list", "help"]
        )
    except getopt.GetoptError:
        print("cmd.py help")
        sys.exit()
    else:
        mode_submit = False
        mode_delete = False
        mode_reservation = False
        mode_status = False
        mode_list = False
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
            elif opt in ("-d", "--status"):
                mode_status = True
            elif opt in ("-l", "--list"):
                mode_list = True
            elif opt in ("-h", "--help"):
                print("cmd.py help ... coming soon.")
                sys.exit()
        if mode_submit or mode_delete or mode_reservation or mode_status:
            qa = QueueAdapter(directory=directory)
            if mode_submit:
                print(qa.submit_job(
                        queue=queue,
                        job_name=job_name,
                        working_directory=working_directory,
                        cores=cores,
                        memory_max=memory_max,
                        run_time_max=run_time_max,
                        command=command
                    ))
            elif mode_delete:
                print(qa.delete_job(process_id=job_id))
            elif mode_reservation:
                print(qa.enable_reservation(process_id=job_id))
            elif mode_status:
                print(json.dumps(qa.get_queue_status().to_dict(orient='list')))
        elif mode_list:
            working_directory = os.path.abspath(os.path.expanduser(working_directory))
            remote_dirs, remote_files = [], []
            for p, folder, files in os.walk(working_directory):
                remote_dirs.append(p)
                remote_files += [os.path.join(p, f) for f in files]
            print(json.dumps({'dirs': remote_dirs, 'files': remote_files}))
        sys.exit()


if __name__ == "__main__":
    command_line(sys.argv[1:])
