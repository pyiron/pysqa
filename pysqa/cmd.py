import sys
import getopt
from pysqa.queueadapter import QueueAdapter


def command_line(argv):
    """
    Parse the command line arguments.

    Args:
        argv: Command line arguments

    """
    try:
        opts, args = getopt.getopt(
            argv, "f:sq:j:w:n:m:t:c:ri:dqh", ["config_directory=", "submit", "queue=", "job_name=",
                                              "working_directory=", "cores=", "memory_max=", "run_time_max=",
                                              "command=", "reservation", "id", "delete", "status", "help"]
        )
    except getopt.GetoptError:
        print("cmd.py help")
        sys.exit()
    else:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print("cmd.py help ... coming soon.")
                sys.exit()
        sys.exit()


if __name__ == "__main__":
    command_line(sys.argv[1:])
