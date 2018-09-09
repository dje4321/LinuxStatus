import os, subprocess
from sys import exit

if __name__ == "__main__":
    print("Your not supposed to run this as a program")

def checkSystemd(config):

    print("[SYSTEMD]")
    systemctl = []
    output = subprocess.getoutput("systemctl list-units").splitlines()

    for x in output:
        if x.count("failed") >= 1:
            # print(repr(x))
            systemctl.append(x.split(" ")[1] + " has failed")

    for i in systemctl:
        print(i)
