# Backend created by @DanTCA1 & Frontend somewhat created by Elijah Ryerson (@Pinapplekat)

# Importing packages
import socket, types, traceback, sys, time
# Special packages created by @DanTCA1 for the backend, but used in the frontend cuz im lazy. it allows me to connect to a websocket in an easier way and lets me implement visual goodness while the script is running
import activesocket, inputplus
from fullprint import FullPrint as Print

# ANSI colors and special case for nice console
colors = {
    "address": "\033[96m",
    "definition": "\033[1;33m",
    "success": "\033[0;32m",
    "italic": "\033[3m",
    "traceback": "\033[0;3;31m",
    "default": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "negative": "\033[7m",
    "blink": "\33[5m",
    "error": "\033[1;31m"
}

print(f"\n{colors["italic"]}Written by @DanTCA1 (Backend) & Elijah Ryerson (Frontend){colors["default"]}\n")

# Arguments
arguments = sys.argv
defaults = ["request.py", "ai.dantca.net", 80, ""]
arguments = arguments + defaults[len(arguments):]

# Errors
ip = ""
res = ""
con_approve = False
closed = True
online = True

# Actual code lol
try:
    # Set paremeters from the argument section
    hostname = arguments[1]
    port = int(arguments[2])
    data = arguments[3]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Launching the connection
    def launchCon():
        global closed, con_approve

        # Creates a socket, gets the ip address from the hostname defined in the arguments, connects to the ip address and port, sends the headers, checks for response, makes a test request if there is a parameter, then prints it out
        print(f"{colors["default"]}{colors["blink"]}Establishing Connection{colors["default"]}")
        
        print(f"{colors["default"]}  ┝ {colors["definition"]}Getting host by name: {colors["address"]}" + hostname)
        ip = socket.gethostbyname(hostname)
        print(f"{colors["default"]}  ┝ {colors["definition"]}Connecting to {colors["address"]}" + ip)
        sock.connect((ip, port))
        print(f"{colors["default"]}  ┝ {colors["definition"]}Initializing socket connection")
        sock.send(b"GET / HTTP/1.1\r\nHost: ai.dantca.net\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\nSec-WebSocket-Protocol: chat, superchat\r\nSec-WebSocket-Version: 13\r\n\r\n")
        con_approve = True
        sock.recv(9999)
        print(f"{colors["default"]}  ┝ {colors["success"]}Connection approved")
        print(f"{colors["success"]}  └ Connection successful to{colors["default"]} {colors["address"]}{hostname} @ {ip}:{port}")
        # If the user did not give data, then it will not run the connection test
        if data != "":
            makeReq(data)
        closed = False

    def makeReq(data):
        print(f"{colors["default"]}{colors["blink"]}Making request{colors["default"]}")
        activesocket.webSocketFormat(sock, data, MASKED=True)
        res = activesocket.parseReq(sock)
        print(f"{colors["default"]}  └ {colors["definition"]}Response{colors["default"]} ------------")
        print("  "+colors["address"]+res)
        print(f"{colors["default"]}  -----------------------")
        # print(f"{colors["success"]}  └ Request successfully made!")

    # Closing the connection
    def closeCon():
        global closed

        print(f"{colors["default"]}{colors["blink"]}Closing Connection{colors["default"]}")
        activesocket.webSocketFormat(sock, opcode="Close", errorCode=1001, content="closing from the pi")
        print(f"{colors["success"]}  └ Connection successfully closed from{colors["default"]} {colors["address"]}{hostname}")
        closed = True
        print(colors["default"])

    # Just in case
    print(colors["default"])

    # Start
    launchCon()

    while online == True:
        output = inputplus.tick()
        Print(output.text, end="\r")
        if len(output.cmd) != 0:
            inputplus.clear()
            breakLoop = False
            for i in output.cmd:
                if i[0] == "cmd":
                    if i[1] == "close":
                        closeCon()
                        breakLoop = True
                        break
                    makeReq(i[1])
            if breakLoop:
                break
        time.sleep(0.05)


except Exception as e:
    # Checks using the variables i made earlier
    if ip == "":
        print(f"{colors["error"]}  └ Connection unsuccessful, could not get ip address. Bad hostname?")
    elif res == "":
        print(f"{colors["error"]}  └ Connection unsuccessful, could not get response.")
    elif con_approve == False:
        print(f"{colors["error"]}  └ Connection unsuccessful, connection was declined.")
    elif closed == False:
        print(f"{colors["error"]}  └ Connection could not close.")
    else:
        print(f"{colors["error"]}  └ Could not complete task.")

    # Makes the color red and italicised for the traceback exception
    print(colors["traceback"])
    
    # Prints the excpetion
    traceback.print_exception(e)

# Resetting the colors in terminal just incase i forget lol
print(colors["default"])

