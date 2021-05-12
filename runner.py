#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys
import os
import time as Time
import datetime
import signal


class Programs:
    def __init__(self, time, day, every, program, sys_argv):
        self.time = time
        self.day = day
        self.every = every
        self.program_path = program
        self.sys_argv = sys_argv
        self.date = None
        self.runtime = None
        self.error = None
        self.type = None
        self.time_ran = None


valid_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
valid_keywords = ["every", "on", "at", "run"]
run_list = []


def config_error(line):  # Prints out appropriate error message for configuration
    sys.stderr.write("error in configuration: " + line +"\n")
    quit()


# Writes PID to file
pid = os.getpid()

f = open(os.path.expanduser("~/.runner.pid"), "w")
f.write(str(pid))
f.close()

# Checks if runner status file exists and creates it if it doesn't exist
if os.path.isfile(os.path.expanduser("~/.runner.status")) == False:
    try:
        os.mknod(os.path.expanduser("~/.runner.status"))
    except OSError:
        sys.stderr.write("file runner.status cannot be created\n")
        quit()

filename = os.path.expanduser("~/.runner.conf")
f = ""
try:
    f = open(filename, "r")
except FileNotFoundError:
    sys.stderr.write("configuration file not found\n")
    quit()

# Checks length of config file
lines = len(open(filename).readlines())
if lines == 0:
    sys.stderr.write("configuration file empty\n")
    quit()

i = 1

while i<=lines:
    line = f.readline()  # Stores current line for error message purposes
    current_line = line.split()  # Stores current line split up by spaces

    if current_line[0] not in valid_keywords:  # Checks for valid keyword
            config_error(line)

    if current_line[0] == "at":
        current_day = datetime.datetime.today().strftime("%A")
        times = current_line[1].split(",")

        for time in times:
            try:
                time = datetime.datetime.strptime(time, "%H%M")  # Checks if time is valid number
            except ValueError:
                config_error(line)

        if current_line[2] != "run":  # Format checking
            config_error(line)

        program = current_line[3]  # Program path

        sys_argv = []
        j = 3
        while j<len(current_line):  # Adds program parameters to list
            sys_argv.append(current_line[j])
            j += 1

        if program[0] != "/":  # Checks if it's a valid program path
            config_error(line)

        for time in times:  # Creates new Programs instance
            if len(sys_argv) == 0:
                run_list.append(Programs(time, current_day, False, program, None))
            else:
                run_list.append(Programs(time, current_day, False, program, sys_argv))
            run_list[-1].type = "at"


    elif current_line[0] == "on":

        days = current_line[1].split(",")
        for day in days:
            if day not in valid_days or days.count(day) != 1:  # Checks if days in config files are valid
                config_error(line)

        if current_line[2] != "at":  # Config file formatting check
            config_error(line)

        times = current_line[3].split(",")

        for time in times:
            try:
                time = datetime.datetime.strptime(time, "%H%M")  # Checks if time is valid number
            except ValueError:
                config_error(line)

        if current_line[4] != "run":  # Config file formatting check
            config_error(line)
        program = None
        try:
            program = current_line[5]
        except IndexError:
            config_error(line)

        sys_argv = []
        j = 5
        while j<len(current_line):  # Adds program parameters to list
            sys_argv.append(current_line[j])
            j += 1

        if program[0] != "/":  # Checks if program path has valid syntax
            config_error(line)

        for time in times:  # Creates new Programs instance
                for day in days:
                    if len(sys_argv) == 0:
                        run_list.append(Programs(time, day, False, program, None))
                    else:
                        run_list.append(Programs(time, day, False, program, sys_argv))


    elif current_line[0] == "every":

        days = current_line[1].split(",")
        for day in days:
            if day not in valid_days or days.count(day) != 1:  # Checks if days in config are valid
                config_error(line)

        if current_line[2] != "at":  # Config format check
            config_error(line)

        times = current_line[3].split(",")
        for time in times:
            try:
                time = datetime.datetime.strptime(time, "%H%M")  # Checks if time is a valid number
            except ValueError:
                config_error(line)

        if current_line[4] != "run":  # Config format check
            config_error(line)

        program = None

        try:
            program = current_line[5]
        except IndexError:
            config_error(line)

        sys_argv = []
        j = 5
        while j<len(current_line):  # Adds program parameters to list
            sys_argv.append(current_line[j])
            j += 1

        if program[0] != "/":  # Checks formatting of program path
            config_error(line)

        for time in times:  # Creates Instance of Programs class
                for day in days:
                    if len(sys_argv) == 0:
                        run_list.append(Programs(time, day, True, program, None))
                    else:
                        run_list.append(Programs(time, day, True, program, sys_argv))

    j = 0
    k = 0

    while j < len(run_list):  # Duplicate run time error checking
        while k < len(run_list):
            if run_list[k].day == run_list[j].day and run_list[k].time == run_list[j].time and j!=k:
                config_error(line)
            k += 1
        k = 0
        j += 1

    i += 1


def time_conversion(program, valid_days):  # Converts given time into datetime object
    current_day_of_week = int(datetime.datetime.today().strftime("%w"))  # Reference point to calculate day difference
    program_day = int(valid_days.index(program.day))

    if current_day_of_week > program_day:
        if current_day_of_week == 0:
            difference = abs(current_day_of_week - program_day)
        elif abs(current_day_of_week - program_day) != 0:
            difference = 7 - abs(current_day_of_week - program_day)
    else:
        difference = program_day - current_day_of_week

    program_date = datetime.datetime.today() + datetime.timedelta(days = difference)  # Gives time and day in config file an actual year and month
    program_day = int(program_date.strftime("%d"))
    program_hour = int(program.time[0] + program.time[1])
    program_minute = int(program.time[2] + program.time[3])

    # If program is scheduled for today but the time has already passed, determines when to run it next
    if (program_day == int(datetime.datetime.today().strftime("%d")) and  program_hour < int(datetime.datetime.today().strftime("%H"))) or (program_day == int(datetime.datetime.today().strftime("%d")) and program_hour == int(datetime.datetime.today().strftime("%H")) and program_minute <= int(datetime.datetime.today().strftime("%M"))):
        if program.type == "at":
            program_date += datetime.timedelta(days = 1)
        else:
            program_date += datetime.timedelta(days = 7)

        program_day = int(program_date.strftime("%d"))

    program_year = int(program_date.strftime("%Y"))
    program_month = int(program_date.strftime("%m"))

    program.date = datetime.datetime(program_year, program_month, program_day, program_hour,program_minute) #sets datetime value for Program instance
    program.runtime = program.date.timestamp()  # Time in seconds since epoch


for program in run_list:  # Converts all times from config into datetimes
    time_conversion(program, valid_days)

run_list.sort(key=lambda x:x.date)  # Sorts run_list in order of date and time


def write_status_messages(run_history, run_list):  # Writes to status file

    f = open(os.path.expanduser("~/.runner.status"), "w")

    for record in run_history:  # Writes programs that have been run first
        if record.error != True:
            f.write("ran " + Time.ctime(record.time_ran) + " " + record.program_path)
            i = 1
            while i<len(record.sys_argv):  # Writes program parameters - have variable length
                f.write(" " + record.sys_argv[i])
                i += 1
            f.write("\n")

    for record in run_history:  # Writes programs that had errors
        if record.error == True:
            f.write("error " + Time.ctime(record.time_ran) + " " + record.program_path)
            i = 1
            while i<len(record.sys_argv):  # Writes program parameters - have variable length
                f.write(" " + record.sys_argv[i])
                i += 1
            f.write("\n")

    for program in run_list:  # Writes programs that will be run
        f.write("will run at " + Time.ctime(program.runtime) + " " + program.program_path)
        i = 1
        while i<len(program.sys_argv):  # Writes program parameters - have variable length
            f.write(" " + program.sys_argv[i])
            i += 1
        f.write("\n")

    f.close()


run_history = []


def handler(signum, stack):  # Signal handler
    write_status_messages(run_history, run_list)


while len(run_list)>0:  # Main loop of program

    signal.signal(signal.SIGUSR1, handler)  # Signal receiver

    current_time_seconds = int(Time.time())  # Time in seconds since epoch
    time_diff = int(run_list[0].runtime) - current_time_seconds

    Time.sleep(time_diff)  # Program waits till it's time to execute the specifed program

    pid = None

    try:
        pid = os.fork()
    except OSError:  # Catches any potential error with fork
        run_list[0].error = True

    if pid == 0:  # Child process
        try:
            os.execv(run_list[0].program_path, run_list[0].sys_argv)
        except OSError:  # Catches any potential error with the execution of the program
            sys.exit(1)  # Exits with non-zero exit status to indicate error in child process

    elif pid > 0:  # Parent process
        exit_status = os.wait()  # Waits for the child

    elif pid < 0:  # Error in fork
        run_list[0].error = True

    if int(exit_status[1]) != 0:  # Checks if child process exited normally
        run_list[0].error = True
    
    run_list[0].time_ran = Time.time()
    run_history.append(run_list[0])  # Adds executed program to run history list


    if run_list[0].every == True:  # Checks whether it needs to be run again
        time_conversion(run_list[0], valid_days)  # Does appropriate time conversion then adds it to end of list
        run_list.append(run_list[0])

    run_list.pop(0)  # Removes program from the front of the list


print("nothing left to run")  # Runs when there are no programs left in run_list
quit()






"""Contents of testConfig.py is below

import sys
import os

file = sys.argv[1]

f = open(file, "r")

ls = f.readlines()

f.close()

f = open(os.path.expanduser("runner.conf"), "w")

for line in ls:
    f.write(line)

f.close()

This would take the configuration file from my .in file and write it to .runner.conf to make it usable for
the subsequent configuration error test. """




"""Contents of testOutput.py is  below

import sys
from datetime import datetime
import os

file = sys.argv[1]
f = open(file, "r")

ls = []
lines = len(open(file).readlines())
i = 0
while i<lines:
    ls.append(f.readline().split())
    i = i + 1

i = 0
current_time = datetime.now()
if current_time.minute + 1 < 10:
    config_time = str(current_time.hour) + "0" + str(current_time.minute + 1)
elif current_time.minute + 1>=60:
    config_time = str(current_time.hour) + str(60 - (current_time.minute + 1))
else:
    config_time = str(current_time.hour) + str(current_time.minute + 1)

i=0
while i<len(ls):
    if (ls[i][0] == "at"):
        ls[i][1] = config_time
        break
    i += 1

i = 0
j = 0
config = []
while i<len(ls):
    line = ""
    while j<len(ls[i]):
        line += ls[i][j]
        line += " "
        j += 1
    i += 1
    j = 0
    config.append(line)

f.close()

f = open(os.path.expanduser("runner.conf"), "w")
i = 0
while i<len(config):
    f.write(config[i].strip())
    f.write("\n")
    i = i + 1

f.close()

This python script was used to test the output fo runstatus.py. It would update the time on the config file
to be 1 minute ahead of the current time, then write it back to the config file, allowing me to test
the actual running of programs to see if runner.py is working appropriately. """

