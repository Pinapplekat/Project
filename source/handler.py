# Backend created by @DanTCA1 & Frontend somewhat created by Elijah Ryerson (@Pinapplekat)

# Importing packages
import socket, types, traceback, sys, os, time, subprocess, pyttsx3, multiprocessing, json, speech_recognition as sr
from threading import Thread
# Special packages created by @DanTCA1 for the backend, but used in the frontend cuz im lazy. it allows me to connect to a websocket in an easier way and lets me implement visual goodness while the script is running
import activesocket, inputplus
from fullprint import FullPrint as Print

# Launching the connection
def launchCon():
    global closed, con_approve, started, ip

    # Creates a socket, gets the ip address from the hostname defined in the arguments, connects to the ip address and port, sends the headers, checks for response, makes a test request if there is a parameter, then prints it out
    print(f"{colors['default']}{colors['blink']}Establishing Connection{colors['default']}")
    
    print(f"{colors['default']}  ┝ {colors['definition']}Getting host by name: {colors['address']}" + hostname)
    ip = socket.gethostbyname(hostname)
    print(f"{colors['default']}  ┝ {colors['definition']}Connecting to {colors['address']}" + ip)
    sock.connect((ip, port))
    print(f"{colors['default']}  ┝ {colors['definition']}Initializing socket connection")
    sock.send(b"GET / HTTP/1.1\r\nHost: ai.dantca.net\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\nSec-WebSocket-Protocol: chat, superchat\r\nSec-WebSocket-Version: 13\r\n\r\n")
    con_approve = True
    sock.recv(9999)
    print(f"{colors['default']}  ┝ {colors['success']}Connection approved{colors['default']}")
    print(f"  └ {colors['success']}Connection successful to {colors['address']}{hostname} @ {ip}:{port}{colors['default']}")
    # If the user did not give data, then it will not run the connection test
    closed = False
    started = True

def makeReq(data):
    global chat_history
    print(f"{colors['default']}{colors['blink']}Making request{colors['default']} - \"{colors['definition']}{data}{colors['default']}\"")
    activesocket.webSocketFormat(sock, data, MASKED=True)
    while True:
        res = activesocket.parseReq(sock)
        res = json.loads(res)
        if res["success"] == False:
            break
        print("  ┝ "+colors['definition']+res["status"]+colors['default'])
        if res.get("response", False):
            break
    
    if res["success"] == False:
        res = res["error"]
        error = True
    else:
        res = res["response"]
        error = False
    print(f"{colors['default']}  └ {colors['success']}Response{colors['default']} ------------")
    if error:
        print("  "+colors['error']+res)
    else:
        print("  "+colors['address']+res)
    print(f"{colors['default']}  -----------------------")
    chat_history.append(f"{res}\" --> ")
    list = res.split("```")
    res = ""
    for i in range(len(list)):
        if i == len(list) - 1:
            res += list[i]
            break
        if i % 2 == 0:
            res += list[i] + " code block start "
        else:
            res += list[i] + " code block end "
    SpeakText(res)

# Closing the connection
def closeCon():
    global closed, started

    print(f"{colors['default']}{colors['blink']}Closing connection{colors['default']}")
    activesocket.webSocketFormat(sock, opcode="Close", errorCode=1001, content="closing from the pi")
    print(f"{colors['success']}  └ Connection successfully closed from{colors['default']} {colors['address']}{hostname}")
    closed = True
    started = False
    print(colors['default'])
    time.sleep(1)
    stop_speaker()

# A bunch of stuff for async tts
def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def speak(phrase, vc):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty('voice', voices[vc].id)
    engine.say(phrase)
    engine.runAndWait()
    engine.stop()

def stop_speaker():
    global term
    term = True
    try:
        t.join()
    except:
        pass

@threaded
def manage_process(p):
    global term
    while p.is_alive():
        if term:
            p.terminate()
            term = False
        else:
            continue

def SpeakText(phrase, vc = 1):
    global t
    global term
    term = False
    p = multiprocessing.Process(target=speak, args=(phrase,vc))
    p.start()
    t = manage_process(p)

if __name__ == "__main__":

    # Actual code lol
    r = sr.Recognizer()

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

    print(f"\n{colors['italic']}Written by Даниил Иванов (Backend) & Elijah Ryerson (Frontend){colors['default']}\n")


    # Arguments
    arguments = sys.argv
    defaults = ["request.py", "false"]
    arguments = arguments + defaults[len(arguments):]

    # Errors
    ip = ""
    res = ""
    con_approve = False
    closed = True
    online = True
    started = False
    override = False
    restart = False

    chat_history = []
    try:
        # Set parameters from the argument section
        devmode = arguments[1].lower()
        hostname = "ai.dantca.net"
        port = 80
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Just in case
        print(colors['default'])

        if devmode == "true":
            override = True
            print("DEVMODE IS ON. TYPE 'voice' TO RETURN TO VOICE CONTROL")
            SpeakText("Dev mode is on. Type voice to return to voice control")
        else:
            override = False
        launchCon()

        while online == True:    
        
            output = inputplus.tick()
            Print(output.text, end="\r")
            if len(output.cmd) != 0:
                inputplus.clear()
                breakLoop = False
                for i in output.cmd:
                    if i[0] == "cmd":
                        cmd = i[1].lower()
                        if cmd == "close":
                            stop_speaker()
                            SpeakText("Goodbye!")
                            online = False
                            breakLoop = True
                            closeCon()
                            break
                        if cmd in ["rs", "restart"]:
                            stop_speaker()
                            SpeakText("Restarting, stand by")
                            time.sleep(3)
                            closeCon()
                            exit(1)
                        elif cmd == "override":
                            print(f"{colors['default']}{colors['blink']}Activating text override{colors['default']}")
                            override = True
                            if started == False:
                                launchCon()
                        elif cmd == "voice":
                            print(f"{colors['default']}{colors['blink']}Returned to voice control{colors['default']}")
                            override = False
                        elif cmd == "stop":
                            stop_speaker()
                        elif override:
                            makeReq(i[1])
                if breakLoop:
                    break
            
            if override:
                time.sleep(output.tickRate)
                continue

            try:
                
                # use the microphone as source for input.
                with sr.Microphone() as source2:
                    
                    # wait for a second to let the recognizer
                    # adjust the energy threshold based on
                    # the surrounding noise level 
                    r.adjust_for_ambient_noise(source2, duration=0.2)
                    
                    #listens for the user's input 
                    audio2 = r.listen(source2,  timeout=0.5, phrase_time_limit=3)
                    
                    # Using google to recognize audio
                    MyText = r.recognize_google(audio2)

                    print(MyText)

                    if started == False and MyText.lower() != "start":
                        tosay = "The program is not running. Please say the word \"start\" clearly into your microphone."
                        print(tosay)
                        SpeakText(tosay)
                    elif MyText.lower() == "start" and started == False:
                        launchCon()
                        SpeakText("Hello, speak to me.")
                    elif started == True:
                        if MyText.lower() == "close":
                            closeCon()
                            stop_speaker()
                            SpeakText("Goodbye!")
                            breakLoop = True
                            break
                        elif MyText.lower() == "restart":
                            stop_speaker()
                            SpeakText("Restarting, stand by")
                            time.sleep(3)
                            closeCon()
                            exit(1)
                        elif MyText.lower() == "stop":
                            stop_speaker()
                        else:
                            chat_history.append(f"-Client: \"{MyText}\" --> Assistant: \"")
                            makeReq("".join(chat_history))
                    
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

            except sr.WaitTimeoutError: # Nothing was said during the 3 second timeout
                pass
                
            except sr.UnknownValueError:
                print("Unknown error occurred, this error likely doesn't matter.")

            except OSError:
                print("No microphone available, switching to text mode...")
                print("Start typing to make a request")
                SpeakText("No microphone detected. Use your keyboard to type requests.")
                override = True

    except Exception as e:
        # Figuring out what the error is using the variables i made earlier
        if ip == "": print(f"{colors['error']}  └ Connection unsuccessful, could not get ip address. Bad hostname?")
        elif res == "": print(f"{colors['error']}  └ Connection unsuccessful, could not get response.")
        elif con_approve == False: print(f"{colors['error']}  └ Connection unsuccessful, connection was declined.")
        elif closed == False: print(f"{colors['error']}  └ Connection could not close.")
        else: print(f"{colors['error']}  └ Could not complete task.")

        # Makes the color red and italicized for the traceback exception
        print(colors['traceback'])
        
        # Prints the exception
        traceback.print_exception(e)
        print(colors['default'])
        exit(1)