#!/usr/bin/env python3
import os, function
from sys import argv, exit

default = {
"nogui":False,
"trash":True,
"entropy":True,
"systemd":True,
"disk":True,
"entropyThreshold":100,
"diskThreshold":80,
"systemdBlacklist":[],
"diskBlacklist":[]
}

exampleConfig = {
"nogui":False,
"trash":True,
"entropy":True,
"systemd":True,
"disk":True,
"entropyThreshold":100,
"systemdBlacklist":["lvm"],
"diskBlacklist":["tmpfs","/var"]
}

help = """{}

-e      Prints a example config
-h      Displays this help message
-c      Specifies a config to load. If it doesnt exists a default one will be created""".format(argv[0])

class Configuration:

    def __init__(self,file):
        file = os.path.realpath(file)
        if os.path.exists(os.path.abspath(file)) != True:
            if os.path.exists(os.path.dirname(file)) != True:
                os.makedirs(os.path.dirname(file))
            fd = open(file, "w")
            self.__write__(fd,default)
            fd.close()

    def __write__(self,fd,data):
        fd.write(str(data) + "\n")

    def read(self, file):
        fd = open(os.path.abspath(file), "r")
        config = fd.read()
        fd.close()

        return eval(config)

def typeCast(var):
    if type(var) == str: # No need to convert if its already a string
        return var
    if var == "True": # Check for bools
        return True
    if var == "False":
        return False
    if var.isnumeric == True: # See if its a number
        return int(var)

    return str(var) # Catch all incase we cant type cast

def getArgv(arg, Increment=False):
    counter = -1
    for i in argv:
        counter += 1
        if i == arg:
            if Increment == True:
                return argv[counter+1]
            return i

def testArgv(arg):
    for i in argv:
        if i == arg:
            return True
    return False

def main(config):
    function.checkSystemd(config)
    function.checkDisk(config)

if testArgv("-e") == True:
    print(exampleConfig)
    exit()

if testArgv("-h") == True:
    print(help)
    exit()

if testArgv("-c") == True:
    _config = Configuration(getArgv("-c",Increment=True))
    config = _config.read(getArgv("-c",Increment=True))
else:
    config = default

main(config)
