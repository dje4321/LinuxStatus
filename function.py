import os, subprocess
from sys import exit

if __name__ == "__main__":
    print("Your not supposed to run this as a program")

def checkSystemd(config):

    print("[SYSTEMD]")
    systemctl = []
    blacklist = config["systemdBlacklist"]
    output = subprocess.getoutput("systemctl list-units").splitlines() #Get a list of all systemd units

    for x in output: # Run over the systemd units and check if it has failed
        if x.count("failed") >= 1:
            # print(repr(x))
            systemctl.append(x.split(" ")[1] + " has failed")

    if config["systemdBlacklist"] != []: # Apply the blacklist
        counter = -1
        counter += 1
        for i in blacklist:
            for a in systemctl:
                if a.count(i) != 0:
                    systemctl.pop(counter)

    for a in systemctl:
        print(a)

def checkDisk(config):

    print("[DISK USAGE]")
    diskUsage = []
    blacklist = config["diskBlacklist"]
    output = subprocess.getoutput("df -h").splitlines()

    for i in output:
        _output = i.split(" ")
        for x in _output:
            if x.count("%") != 0 and x.lower().count("use") == 0: #see if were on a percent used
                if int(x.strip("%")) >= config["diskThreshold"]:
                    diskUsage.append(_output[-1] + " is at " + str(x) + " disk usage")

    for a in diskUsage:
        print(a)
