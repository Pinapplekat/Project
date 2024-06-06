import time, subprocess, sys
time.sleep(3)
print(sys.argv)
print("\033[1;33mRestarting script... please wait\033[0m")
time.sleep(5)
isopen = True
while isopen:
    isopen = True
    test = subprocess.run(["python.exe", "main.py", "true"])
    if test != 1:
        break