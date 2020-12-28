#!/usr/bin/python3

import sys
import re
import argparse
from typing import Dict, Any

def safe_eval(py: str, locals: Dict[str, Any]) -> Any:
    return eval(py, {}, locals)

def main():

    parser = argparse.ArgumentParser(prog="colorize", description="listen a stream and add colorization to it via some patterns defined by the user")
    parser.add_argument('-m', '--map',
        action='append', nargs=2, metavar=('pattern','replacement'),
        help="""
            Add a new pattern that will be applied to the output.
            This specifies that whenever the program encouter the pattern, it will automatically replace it with the second expression.

            Example:
            --map='r"Warning"' 'r"WARNING:"'
            --map='r"Warning"' 'YELLOW + r"WARNING:" + RESET'
        """)
    options = parser.parse_args(sys.argv[1:])

    patterns = options.map

    red=r"\033[31m"
    yellow=r"\033[33m"    
    green=r"\033[32m"
    cyan=r"\033[36m"
    blue=r"\033[34m"

    bold_red=r"\033[1;31m"
    bold_yellow=r"\033[1;33m"
    bold_green=r"\033[1;32m"
    bold_cyan=r"\033[1;36m"
    bold_blue=r"\033[1;34m"

    reset=r"\033[0m"

    locals = {
        "RED": red,
        "YELLOW": yellow,
        "GREEN": green,
        "CYAN": cyan,
        "BLUE": blue,

        "BOLD_RED": bold_red,
        "BOLD_YELLOW": bold_yellow,
        "BOLD_GREEN": bold_green,
        "BOLD_CYAN": bold_cyan,
        "BOLD_BLUE": bold_blue,
        "RESET": reset,
    }

    for line in sys.stdin.readlines():
        tmp_line = line
        for pattern, replacement in patterns:
            real_pattern = safe_eval(pattern, locals=locals)
            real_replacement = safe_eval(replacement, locals=locals)
            tmp_line = re.sub(real_pattern, real_replacement, tmp_line)
        #print line
        print(tmp_line, end="")

if __name__ == '__main__':
    main()