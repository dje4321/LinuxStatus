#!/usr/bin/python3
import subprocess, os, sys
argv = sys.argv

def findArgv(argv,condidtion):
    for x in range(0,len(argv)):
        if argv[x] == condidtion:
            return x

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
    formattedOutput = 'The following issues were found with systemd\n'
    systemctl,errors = [],0
    blacklist = []
    
    if checkArgv(argv,"--sysBlacklist") == True:
        for x in range(0,len(argv[findArgv(argv,"--sysBlacklist") + 1].split(","))):
            blacklist.append(argv[findArgv(argv,"--sysBlacklist") + 1].split(",")[x])
    
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
    formattedOutput = 'Low diskspace detected\n'
    diskSpace,errors = [],0
    blacklist = []
 
    if checkArgv(argv,"--diskBlacklist") == True:
        for x in range(0,len(argv[findArgv(argv,"--diskBlacklist") + 1].split(","))):
            blacklist.append(argv[findArgv(argv,"--diskBlacklist") + 1].split(",")[x])
    
    if checkArgv(argv,"--threshold") == True:
        threshold = int(argv[findArgv(argv,"--threshold") + 1])
    else:
        threshold = 85 #Percent threshold for disk space usage
    
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

########################################################################################
# Main Program

if checkArgv(argv,"-h") == True or checkArgv(argv,"--help") == True:
    print(
"""{}
    -h --help               Prints the help message
    --nogui                 Disables the GUI output and only prints to STDOUT
    --threshold             Overrides the threshold value for disk space usage
    --diskBlacklist         Blacklists certain strings from disk usage checks. Values are comma separated
    --sysBlacklist          Blacklists certain strings from systemd checks. Values are comma separated""".format(argv[0]))
    sys.exit()

checkSystemd(argv)
diskUsage(argv)
