# This script is just to make reloads of handler.py possible
import time, subprocess, sys
arguments = sys.argv
defaults = ["request.py", "false"]
arguments = arguments + defaults[len(arguments):]
devmode = arguments[1].lower()

while True:
    test = subprocess.run(["python.exe", "handler.py", devmode])
    if test.returncode  != 1:
        break
    print("\033[1;33mRestarting script... please wait\033[0m")