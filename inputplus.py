# Written by @DanTCA1

import msvcrt, time, types
TLoc = 0
text = ""
TFlash = 0
hist = []
histIdx = 0
cmd = []
prevTick = []
tickRate = 0.1
def clear(amount = -1):
    global cmd
    if amount < 0:
        cmd = []
    else:
        cmd = cmd[amount + 1:]
    return(cmd)

def textSet(newText, newCursorLoc=-1):
    global text, TLoc
    text = newText
    if newCursorLoc == -1:
        TLoc = len(text)
    else:
        TLoc = newCursorLoc

    
def tick():
    global cmd, TLoc, text, TFlash, hist, histIdx, prevTick, tickRate
    opNum = 0
    while msvcrt.kbhit():
        TFlash = time.time()
        c = msvcrt.getch()
        if c == b"\xe0": # Processing for special characters
            c = msvcrt.getch()
            try:
                c = ord(c.decode('utf-8'))
            except:
                continue
            if c not in [72, 77, 80, 75, 71, 79, 83, 115, 116]:
                continue
        else:
            try:
                c = c.decode('utf-8')
            except:
                continue
            if ord(c) in [127]:
                if ord(c) == 127:
                    c = "cback"
        opNum += 1
        if c in [72, 77, 80, 75, 71, 79, "\x1B", "\r", "\b", "\t", 83, "cback", 115, 116]: # All special characters processing
            if histIdx == 0: # makes a varable (currentText => cText) to operate on
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
                for i in range(TLoc - 1, -1, -1):
                    char = cText[i]
                    if delPhase == 0 and char != " ":
                        delPhase = 1
                    if delPhase == 1 and char == " ":
                        break
                    if i == 0:
                        i = -1
                TLoc -= TLoc - i - 1

            if c == 77: # right
                if TLoc < len(cText):
                    TLoc += 1

            if c == 116: # ctrl right
                delPhase = 0
                for i in range(TLoc, len(cText)):
                    char = cText[i]
                    if delPhase == 0 and char != " ":
                        delPhase = 1
                    if delPhase == 1 and char == " ":
                        break
                    if i == 0:
                        i = -1
                TLoc += i - TLoc + 1

            if c == 71: # home
                TLoc = 0

            if c == 79: # end
                TLoc = len(cText)

            if c in ["\r", "\b", 83, "cback"] and histIdx != 0: # 
                text = hist[histIdx]
                histIdx = 0

            if c == "\r": # enter
                cmd.append(("cmd", text))
                hist.append(text)
                if len(hist) > 100:
                    del hist[0]
                text = ""
                TLoc = 0

            if c == "\b": # backspace
                if TLoc != 0:
                    TLoc -= 1
                    text = text[:TLoc] + text[TLoc + 1:]
            if c == "cback": # ctrl + backspace
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
        if (time.time() - TFlash)//0.5 % 2 == 0:
            if TLoc == len(cText):
                cText += " "
            cText = "\33[0m" + cText[0: TLoc] + "\u001b[30m\x1b[47m" + cText[TLoc] + "\33[0m" + cText[TLoc + 1: len(cText)]
            # All text before cursor, formating, cursor, remove formating, text after cursor
    else:
        cText = ""
    prevTick.append(opNum)
    while len(prevTick) > round(1/tickRate) * 10:
        prevTick.remove(prevTick[0])
    avg = 0
    for i in prevTick:
        avg += i
    avg = avg / len(prevTick)
    
    # FullPrint(prevTick, avg)
    if avg == 0:
        avg = 0.5
    else:
        avg = avg * (1/tickRate)
        avg = 1 / avg
        avg = min(avg, 0.2)
    for i in range(len(prevTick)):
        prevTick[i] = round(prevTick[i] / (tickRate / avg), 2)
        # Updates all of prevTick to not cause stale data to effect the average
    tickRate = avg
    return(types.SimpleNamespace(text=cText, cmd=cmd, RecTick=tickRate))