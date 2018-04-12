#!/usr/bin/python3
import subprocess, os, sys
argv = sys.argv

def checkArgv(argv,condidition):
    for x in range(0,len(argv)):
        if argv[x] == condidition:
            return True
    return False

def applyBlacklist(command, blacklist):
    if len(blacklist) == 0:
        return command
        
    command += " | grep -v"
    
    for x in range(0,len(blacklist)):
        command += " -e {}".format(blacklist[x])
    return command

def checkSystemd(argv):
    formattedOutput = 'The following issues were found with systemd\n\n'
    systemctl,errors = [],0
    blacklist = []
    
    systemctlOutput = subprocess.getoutput(applyBlacklist("systemctl",blacklist)).split('\n')

    for x in range(0,len(systemctlOutput)): # Interate over the lists in systemctl
        if systemctlOutput[x].count("failed") >= 1: #Check if anything has failed
            systemctl.append(systemctlOutput[x])
            
    for x in range(0,len(systemctl)):
        formattedOutput += systemctl[x].split(' ')[1] + ' ' + 'has failed' + '\n'
        errors += 1
    
    if errors >= 1:
        print(formattedOutput)
        if checkArgv(argv,"--nogui") == False:
            os.system("zenity --error --ellipsize --text='{}' 2>/dev/null".format(formattedOutput))

def diskUsage(argv):
    formattedOutput = 'Low diskspace detected\n\n'
    diskSpace,errors = [],0
    threshold = 85 #Percent threshold for disk space usage
    blacklist = ["snap"]
    
    dfOutput = subprocess.getoutput(applyBlacklist("df -h",blacklist)).split('\n')

    for x in range(1,len(dfOutput)):
        for i in range(0,len(dfOutput[x].split(' '))):
            if dfOutput[x].split(' ')[i].count("%") >= 1:
                if int(dfOutput[x].split(' ')[i].strip("%")) >= threshold:
                    diskSpace.append(dfOutput[x])

    for x in range(0,len(diskSpace)):
        for i in range(0,len(diskSpace[x].split(' '))):
            if diskSpace[x].split(' ')[i].count("%") >= 1:
                formattedOutput += diskSpace[x].split(' ')[i+1] + " is at " + diskSpace[x].split(' ')[i] + " disk usage" + '\n'
                errors += 1
                
    if errors >= 1:
        print(formattedOutput)
        if checkArgv(argv,"--nogui") == False:
            os.system("zenity --error --ellipsize --text='{}' 2>/dev/null".format(formattedOutput))

if checkArgv(argv,"-h"):
    print(
"""{}
    -h --help      Prints the help message
    --nogui        Disables the GUI output and only prints to STDOUT""".format(argv[0]))
    sys.exit()

checkSystemd(argv)
diskUsage(argv)
