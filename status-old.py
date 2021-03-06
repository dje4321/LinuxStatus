#!/usr/bin/python3
import subprocess, os, sys
argv = sys.argv

def displayError(argv,formattedOutput,errors=0,skipError=False):
    try:
        if errors >= 1 or skipError == True: # Checks if any errors were even found before attempting to display them
            print(formattedOutput)
            if checkArgv(argv,["--nogui"]) == False: # Check if a GUI based prompt is supposed to be run
                os.system("zenity --error --ellipsize --text='{}' 2>/dev/null".format(formattedOutput)) # Display GUI prompt
    except Exception as e:
        print("displayError()\n{}".format(e))
        sys.exit()

def findArgv(argv,condidtion): # Find the position of something in argv and returns the position
    try:
        for x in range(0,len(argv)):
            for i in range(0,len(condidtion)):
                if argv[x] == condidtion[i]:
                    return x
    except Exception as e:
        print("findArgv()\n{}".format(e))
        sys.exit()

def checkArgv(argv,condidition): # Will check to see if a argument has been passed
    try:
        for x in range(0,len(argv)):
            for i in range(0,len(condidition)):
                if argv[x] == condidition[i]:
                    return True
        return False
    except Exception as e:
        print("checkArgv()\n{}".format(e))
        sys.exit()

def applyBlacklist(command, blacklist): # Apply a grep based blacklist to a command
    try:
        if len(blacklist) == 0: # Checks to see if the blacklist even needs to be applied
            return command

        command += " | grep -v"

        for x in range(0,len(blacklist)):
            command += " -e {}".format(blacklist[x])
        return command
    except Exception as e:
        print("applyBlacklist()\n{}".format(e))
        sys.exit()

def checkSystemd(argv): # Checks for any systemd errors and reports them
    try:
        formattedOutput = 'The following issues were found with systemd\n'
        systemctl,errors = [],0
        blacklist = []

        if checkArgv(argv,["--sysBlacklist","-sb"]) == True: # Check to see if a blacklist needs to be applied
            for x in range(0,len(argv[findArgv(argv,["--sysBlacklist","-sb"]) + 1].split(","))):
                blacklist.append(argv[findArgv(argv,["--sysBlacklist","-sb"]) + 1].split(",")[x])

        systemctlOutput = subprocess.getoutput(applyBlacklist("systemctl",blacklist)).split('\n') # Runs systemctl with the optional blacklist and stores the output as a newline separted list

        for x in range(0,len(systemctlOutput)): # Interate over the lists in systemctl
            if systemctlOutput[x].count("failed") >= 1: #Check if anything has failed
                systemctl.append(systemctlOutput[x])

        for x in range(0,len(systemctl)):
            formattedOutput += systemctl[x].split(' ')[1] + ' ' + 'has failed' + '\n'
            errors += 1

        displayError(argv,formattedOutput,errors)
    except Exception as e:
        print("checkSystemd()\n{}".format(e))
        sys.exit()

def diskUsage(argv): # Checks if any mounted devices have exceeded a threshold
    try:
        formattedOutput = 'Low diskspace detected\n'
        diskSpace,errors = [],0
        blacklist = []
        threshold = 85 # Default threshold level

        if checkArgv(argv,["--diskBlacklist","-db"]) == True: # Check if blacklist argument has been specified
            for x in range(0,len(argv[findArgv(argv,["--diskBlacklist","-db"]) + 1].split(","))):
                blacklist.append(argv[findArgv(argv,["--diskBlacklist","-db"]) + 1].split(",")[x])

        if checkArgv(argv,["--diskThreshold","-dt"]) == True: # Check if we need to adjust the threshold
            threshold = int(argv[findArgv(argv,["--diskThreshold","-dt"]) + 1])

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

        displayError(argv,formattedOutput,errors)
    except Exception as e:
        print("diskUsage()\n{}".format(e))
        sys.exit()

def checkTrash(argv):
    try:
        formattedOutput = 'Trash is not empty\n'
        if subprocess.getoutput("$(which dir) $HOME/.local/share/Trash/files").split(' ') != ['']:
            displayError(argv,formattedOutput,skipError=True)
    except Exception as e:
        print("checkTrash()\n{}".format(e))
        sys.exit()

def checkEntropy(argv):
    try:
        threshold = 100
        entropy = int(subprocess.getoutput("cat /proc/sys/kernel/random/entropy_avail"))
        if checkArgv(argv,["--entropyThreshold","-et"]) == True:
            threshold = int(argv[findArgv(argv,["--entropyThreshold","-et"]) + 1])

        formattedOutput = "Entropy is below {}\n You should not do anything cryptographicly intensive".format(threshold)

        if entropy <= threshold:
            displayError(argv,formattedOutput,skipError=True)
    except Exception as e:
        print("displayEntropy()\n{}".format(e))
        sys.exit()
'''
def checkDmesg(argv):
	emerg = subprocess.getoutput("dmesg -l err").split('\n')
	alert = subprocess.getoutput("dmesg -l alert").split('\n')
	crit = subprocess.getoutput("dmesg -l crit").split('\n')
	emerg_new = emerg

	for x in range(0,len(emerg)):
		for i in range(0,len(emerg[x])):
			if emerg[x][i] == "]":
				emerg[x] += ' '
				emerg = emerg[x][i + 2:-1]
				break
'''
########################################################################################
# Main Program

if checkArgv(argv,["-h","--help"]) == True: # Check if we need to display the help screen
    print(
"""{}
    -h --help                  Prints this help message
    --nogui                    Disables the GUI output and only prints to STDOUT
    --diskThreshold -dt        Overrides the threshold value for disk space usage
    --diskBlacklist -db        Blacklists certain strings from disk usage checks. Values are comma separated
    --sysBlacklist  -sb        Blacklists certain strings from systemd checks. Values are comma separated
    --enableTrash   -et        Enables checking Trash to see if its empty
    --enableEntropy -ee        Checks to see if entropy is too low
    --entropyThreshold -et     Threshold for total entropy""".format(argv[0]))
    sys.exit()

checkSystemd(argv) # Check systemd for errors
diskUsage(argv) # Check for high disk usage

if checkArgv(argv,["--enableTrash","-et"]) == True:
    checkTrash(argv)

if checkArgv(argv,["--enableEntropy","-ee"]) == True:
    checkEntropy(argv)

#checkDmesg(argv)
