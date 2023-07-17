import sys
from pysqa.executor.backend import command_line


if __name__ == "__main__":
    command_line(arguments_lst=sys.argv[1:])
