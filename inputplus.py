import time
import types
import sys

if(sys.platform == "win32"):
    import msvcrt
    # VSCode gives too many warnings without these  
    termios = None
    os = None
    fcntl = None
    atexit = None
    select = None
else:
    import termios
    import os
    import atexit
    import fcntl
    from select import select

# The text, what else?
text = ""
# Text that appears when text is empty
placeholderText = ""
# Keeps track of the time for cursor flash (Text Flash => TFlash)
TFlash = 0
# Location of cursor (Text Location => TLoc)
TLoc = 0
# Where in the history you are located
histIdx = 0
# Gets returned so that you can sleep that amount of time
tickRate = 0.1
# Whether this is running on windows or not 
windows = (sys.platform == "win32")
# History
hist = []
# Saved commands in case program isn't ready to process cmd, but can run tick
cmd = []
# How many characters were processed (char that were typed, and are not on blocklist)
prevTick = []
# All the characters read from stdin, needed because linux, but implemented for both
queue = []

if not windows:
    fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(fd)

    # Create new unbuffered terminal settings to use:
    new_term = termios.tcgetattr(fd)
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

    # Reset original terminal settings on exit:
    atexit.register(termios.tcsetattr, fd, termios.TCSAFLUSH, old_term)

def readChars():
    global queue
    if windows:
        while msvcrt.kbhit():
            queue.append(msvcrt.getch())
    else:
        fd = sys.stdin.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        dr, _, _ = select([sys.stdin], [], [], 0)
        if dr:
            chars = sys.stdin.read()
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
            queue.extend(list(chars))
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)


def clear(amount = -1):
    """
    Clears commands from the list that is returned every time tick is called.

    Params: amount = -1

    Clears all commands by default, but can clear a set amount instead
    """
    global cmd
    if amount < 0:
        cmd = []
    else:
        cmd = cmd[amount + 1:]
    return(cmd)

def setText(newText, newCursorLoc=-1):
    """
    Overrides the text that the user has set text of the program's choice, 
    optionally accepts a parameter to set the new cursor location as well.

    Params: newText, newCursorLoc = -1

    Defaults the new cursor location to the end of the new text
    """
    global text, TLoc
    text = newText
    if newCursorLoc == -1:
        TLoc = len(text)
    else:
        TLoc = newCursorLoc

def setPlaceholder(placeholder):
    """
    Sets the placeholder text of InputPlus.

    Params: placeholder

    Placeholder text is the text that will show up when there is no text entered, such as "Enter password..."
    """
    global placeholderText
    placeholderText = placeholder

def tick():
    """
    Runs the main loop of InputPlus. 
    It is recommend to use the tickRate return in a sleep nearby (or don't sleep at all)

    Params: None

    Returns: Class(text, cmd, tickRate)

    Text contains the current text of the terminal to be printed
    Cmd is a list containing any recent commands, in a tuple:
    1. Either cmd or autofill, triggered by enter key and tab respectively
    2. Either the text of the command, or the current text when autofill was triggered
    """
    global cmd, TLoc, text, TFlash, hist, histIdx, prevTick, tickRate
    opNum = 0
    readChars()
    for _ in range(len(queue)):
        TFlash = time.time()
        if len(queue) == 0:
            break
        c = queue[0]
        del(queue[0])

        if c == b"\xe0": # Processing for special characters
            c = ord(queue[0])
            del(queue[0])
            if c not in [72, 77, 80, 75, 71, 79, 83, 115, 116, 147]:
                continue

        elif c == "\x1b" and not windows:
            try:
                if len(queue) in [0, 1]:
                    c = "esc"
                elif queue[0] != "[":
                    c = "esc"
                else:
                    c = queue[1]
                    del(queue[0:2])
                ctrl = False
                if c == "1":
                    ctrl = True
                    c = "ctrl" + queue[2]
                    del(queue[0:3])

                elif c == "3":
                    if queue[0] == "~":
                        c = "del"
                        del(queue[0])
                    else:
                        c = "ctrlDel"
                        del(queue[0:3])

                elif len(str(c)) == 1 and c.isdigit():
                    del(queue[0])
                    continue
                
                linuxReplace = {
                    "A" : 72,
                    "B" : 80,
                    "C" : 77,
                    "D" : 75,
                    "F" : 79,
                    "H" : 71,
                    "del" : 83,
                    "ctrlC" : 116,
                    "ctrlD" : 115,
                    "ctrlDel" : 147,
                    "esc" : "\x1B",
                }
                c = linuxReplace[c]
            except KeyError:
                continue

        else:
            try:
                if windows:
                    c = c.decode('utf-8')
                else:
                    if (ord(c) < 32 or ord(c) > 126) and not c in ["\x7f", "\x08", "\t", "\n"]:
                        continue
            except:
                continue
            
            if windows:
                if ord(c) in [127]:
                    if ord(c) == 127:
                        c = "ctrlBack" # (control backspace => ctrlBack)
            else:
                linuxReplace = {
                    "\x7f" : "\b",
                    "\x08" : "ctrlBack"
                }
                c = linuxReplace.get(c, c)

        opNum += 1
        # Special character processing
        if c in [72, 77, 80, 75, 71, 79, "\x1B", "\r", "\n", "\b", "\t", 83, "ctrlBack", 115, 116, 147]:
            if histIdx == 0: # Makes a variable (currentText => cText) to operate on
                cText = text
            else:
                cText = hist[histIdx]
                if c in ["\t"]:
                    continue

            if c == "\t": # tab
                cmd.append(("autofill", text))
                break

            if c == 72: # up
                if abs(histIdx) != len(hist):
                    histIdx -= 1
                    TLoc = len(hist[histIdx])

            if c == 80: # down
                if histIdx != 0:
                    histIdx += 1
                if histIdx != 0:
                    TLoc = len(hist[histIdx])
                else:
                    histIdx = 0
                    TLoc = len(text)

            if c == 75: # left
                if TLoc != 0:
                    TLoc -= 1

            if c == 115: # ctrl left
                delPhase = 0
                for i in range(TLoc - 1, -2, -1):
                    if i == -1:
                        break
                    char = cText[i]
                    if delPhase == 0 and char != " ":
                        delPhase = 1
                    if delPhase == 1 and char == " ":
                        break
                TLoc -= TLoc - i - 1

            if c == 77: # right
                if TLoc < len(cText):
                    TLoc += 1

            if c == 116: # ctrl right
                delPhase = 0
                for i in range(TLoc, len(cText) + 1):
                    if i == len(cText):
                        break
                    char = cText[i]
                    if delPhase == 0 and char != " ":
                        delPhase = 1
                    if delPhase == 1 and char == " ":
                        break
                TLoc += i - TLoc

            if c == 71: # home
                TLoc = 0

            if c == 79: # end
                TLoc = len(cText)

            if c in ["\r", "\n", "\b", 83, "ctrlBack", 147] and histIdx != 0: # 
                text = hist[histIdx]
                histIdx = 0

            if c in ["\r", "\n"]: # enter
                cmd.append(("cmd", text))
                if text != "":
                    hist.append(text)
                if len(hist) > 100:
                    del hist[0]
                text = ""
                TLoc = 0

            if c == "\b": # backspace
                if TLoc != 0:
                    TLoc -= 1
                    text = text[:TLoc] + text[TLoc + 1:]
            if c == "ctrlBack": # ctrl + backspace
                delPhase = 0
                i = 0
                for i in range(TLoc - 1, -1, -1):
                    char = text[i]
                    if delPhase == 0 and char != " ":
                        delPhase = 1
                    if delPhase == 1 and char == " ":
                        break
                if i == 0:
                    i = -1
                text = text[:i + 1] + text[TLoc:]
                TLoc -= TLoc - i - 1
            if c == 83: # del
                if TLoc != len(text):
                    text = text[:TLoc] + text[TLoc + 1:]
            if c == 147: # ctrl + del
                delPhase = 0
                i = -1
                for i in range(TLoc, len(cText) + 1):
                    if i == len(cText):
                        break
                    char = text[i]
                    if delPhase == 0 and char != " ":
                        delPhase = 1
                    if delPhase == 1 and char == " ":
                        break
                if i == -1:
                    i = len(cText)
                text = text[:TLoc] + text[i:]
            if c == "\x1B": # esc
                text = ""
                TLoc = 0
                histIdx = 0
        else:
            if histIdx != 0:
                text = hist[histIdx]
                histIdx = 0
            text = text[:TLoc] + c + text[TLoc:]
            TLoc += 1
    if histIdx == 0:
        cText = text
    else:
        cText = hist[histIdx]
    if len(cText) > 0:
        # Code that makes the cursor appear
        if (time.time() - TFlash)//0.5 % 2 == 0:
            if TLoc == len(cText):
                cText += " "
            cText = cText[0: TLoc] + "\033[7m" + cText[TLoc] + "\033[27m" + cText[TLoc + 1: len(cText)]
            # All text before cursor, formatting, cursor, remove formatting, text after cursor
    else:
        cText = "\033[2m" + placeholderText + "\033[22m"
    
    prevTick.append(opNum)
    while len(prevTick) > round(1/tickRate * 5):
        prevTick.remove(prevTick[0])
    
    maxOpNum = max(prevTick)
    
    if maxOpNum == 0:
        newTickRate = 0.5
    else:
        # 1 is perfect tickRate, less than 1 is too fast, and more than 1 is too slow
        # This turns how many operations are happening into a tickRate
        newTickRate = tickRate / maxOpNum
        newTickRate = min(newTickRate, 0.2)
        newTickRate = max(newTickRate, 0.001)

    for i in range(len(prevTick)):
        prevTick[i] = round(prevTick[i] / (tickRate / newTickRate), 2)
        # Updates all of prevTick to not cause stale data to affect the max
    tickRate = newTickRate
    return(types.SimpleNamespace(text=cText, cmd=cmd, tickRate=tickRate))