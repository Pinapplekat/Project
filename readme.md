# Getting started
## Project for AP Computer Science

Run `fresh-start.bat` if you are running it for the first time, otherwise run `start.bat`. WINDOWS ONLY. IF YOU ARE NOT ON WINDOWS RUN `python3 main.py` AFTER INSTALLING THE DEPENDENCIES LISTED BELOW

`fresh-start.bat` installs the dependencies on Windows computers then runs the `main.py` script automatically

Dependencies to install: `pyaudio pyttsx3 SpeechRecognition setuptools`

`pip install pyaudio pyttsx3 SpeechRecognition setuptools`

Just run `python main.py` to start the script

Once you start the script with the command `$ python main.py`, it will look something like this:

![python main.py](media/image1.png)

If you try and speak through your microphone, it will tell you to say the word start into your microphone.

![not running weirdo](media/image-2.png)

Once you do say "start" you will then see this screen

![alt text](media/image-3.png)

Now, you can say anything and it will make a request to the AI.

![alt text](media/image-4.png)

If you type "override" on your keyboard then the program will switch to text input mode.

Where there is a text caret, you can type anything to make a request to the server with the data you type, or you can type `close` to close the socket and shutdown the program.

Every time you make a request, it will add another one of those `Making request` bodies to the console.

After you enter `close` it should look something like this:

![close](media/image-1.png)