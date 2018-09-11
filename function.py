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

    systemctlError = systemctl
    if config["systemdBlacklist"] != []: # Apply the blacklist
        counter = -1
        counter += 1
        for _blacklist in blacklist:
            for _systemctl in systemctl:
                if _systemctl.count(_blacklist) > 0:
                    systemctlError.pop(counter)

    for b in systemctlError:
        print(b)

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

    diskUsageError = diskUsage
    if config["diskBlacklist"] != []: # Apply the blacklist
        counter = -1
        counter += 1
        for _blacklist in blacklist:
            for _diskUsage in diskUsage:
                if _diskUsage.count(_blacklist) > 0:
                    diskUsageError.pop(counter)

    for b in diskUsageError:
        print(b)
