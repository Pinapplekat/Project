# Written by @DanTCA1

import os

def FullPrint(*args, end="\n"):
    text = ""
    for i in args:
        text += str(i) + ""
    SpaceNum = os.get_terminal_size().columns - 1
    print(" " * SpaceNum + "\r" + text, end=end)