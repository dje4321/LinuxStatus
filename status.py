#!/usr/bin/python3
import subprocess, os, sys
argv = sys.argv

def findArgv(argv,condidtion): # Find the position of something in argv and returns the position
    for x in range(0,len(argv)):
        if argv[x] == condidtion:
            return x

def checkArgv(argv,condidition): # Will check to see if a argument has been passed
    for x in range(0,len(argv)):
        if argv[x] == condidition:
            return True
    return False

def applyBlacklist(command, blacklist): # Apply a grep based blacklist to a command
    if len(blacklist) == 0: # Checks to see if the blacklist even needs to be applied
        return command
        
    command += " | grep -v"
    
    for x in range(0,len(blacklist)):
        command += " -e {}".format(blacklist[x])
    return command

def checkSystemd(argv): # Checks for any systemd errors and reports them
    formattedOutput = 'The following issues were found with systemd\n'
    systemctl,errors = [],0
    blacklist = []
    
    if checkArgv(argv,"--sysBlacklist") == True: # Check to see if a blacklist needs to be applied
        for x in range(0,len(argv[findArgv(argv,"--sysBlacklist") + 1].split(","))):
            blacklist.append(argv[findArgv(argv,"--sysBlacklist") + 1].split(",")[x])
    
    systemctlOutput = subprocess.getoutput(applyBlacklist("systemctl",blacklist)).split('\n') # Runs systemctl with the optional blacklist and stores the output as a newline separted list

    for x in range(0,len(systemctlOutput)): # Interate over the lists in systemctl
        if systemctlOutput[x].count("failed") >= 1: #Check if anything has failed
            systemctl.append(systemctlOutput[x])
            
    for x in range(0,len(systemctl)):
        formattedOutput += systemctl[x].split(' ')[1] + ' ' + 'has failed' + '\n'
        errors += 1
    
    if errors >= 1: # Checks if any errors were even found before attempting to display them
        print(formattedOutput)
        if checkArgv(argv,"--nogui") == False: # Check if a GUI based prompt is supposed to be run
            os.system("zenity --error --ellipsize --text='{}' 2>/dev/null".format(formattedOutput)) # Display GUI prompt

def diskUsage(argv): # Checks if any mounted devices have exceeded a threshold
    formattedOutput = 'Low diskspace detected\n'
    diskSpace,errors = [],0
    blacklist = []
    threshold = 85 # Default threshold level
 
    if checkArgv(argv,"--diskBlacklist") == True: # Check if blacklist argument has been specified
        for x in range(0,len(argv[findArgv(argv,"--diskBlacklist") + 1].split(","))):
            blacklist.append(argv[findArgv(argv,"--diskBlacklist") + 1].split(",")[x])
    
    if checkArgv(argv,"--threshold") == True: # Check if we need to adjust the threshold
        threshold = int(argv[findArgv(argv,"--threshold") + 1])
    
    dfOutput = subprocess.getoutput(applyBlacklist("df -h",blacklist)).split('\n') # Get the output of df and store as a newline separated list

    for x in range(1,len(dfOutput)): # Iterate over each line
        for i in range(0,len(dfOutput[x].split(' '))): # Interate over the line
            if dfOutput[x].split(' ')[i].count("%") >= 1: # Check if we are on a usage position
                if int(dfOutput[x].split(' ')[i].strip("%")) >= threshold: # see if usage exceeds threshold
                    diskSpace.append(dfOutput[x])

    for x in range(0,len(diskSpace)): # Prettify output
        for i in range(0,len(diskSpace[x].split(' '))):
            if diskSpace[x].split(' ')[i].count("%") >= 1:
                formattedOutput += diskSpace[x].split(' ')[i+1] + " is at " + diskSpace[x].split(' ')[i] + " disk usage" + '\n'
                errors += 1
                
    if errors >= 1: # Check if there are any errors to even report
        print(formattedOutput)
        if checkArgv(argv,"--nogui") == False: # see if any errors even need to be displayed
            os.system("zenity --error --ellipsize --text='{}' 2>/dev/null".format(formattedOutput)) # display errors as a gui

########################################################################################
# Main Program

if checkArgv(argv,"-h") == True or checkArgv(argv,"--help") == True: # Check if we need to display the help screen
    print(
"""{}
    -h --help               Prints this help message
    --nogui                 Disables the GUI output and only prints to STDOUT
    --threshold             Overrides the threshold value for disk space usage
    --diskBlacklist         Blacklists certain strings from disk usage checks. Values are comma separated
    --sysBlacklist          Blacklists certain strings from systemd checks. Values are comma separated""".format(argv[0]))
    sys.exit()

checkSystemd(argv) # Check systemd for errors
diskUsage(argv) # Check for high disk usage
