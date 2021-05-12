#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys
import os
import time

pidfile = os.path.expanduser("~/.runner.pid")
statusfilename = os.path.expanduser("~/.runner.status")

f = None

try:
    f = open(pidfile, "r")
except FileNotFoundError:
    sys.stderr.write("file " + pidfile + " cannot be found\n")
    quit()

pid = f.readline() # Reads pid from file

try:
    pid = int(pid)
except ValueError:
    sys.stderr.write("file " + pidfile + " contains an invalid pid\n")
    quit()

f.close()

try:
    os.kill(pid, 10)  # Sends SIGUSR1 signal to runner.py
except OSError:
    sys.stderr.write("error in sending SIGUSR1 signal to runner.py - bad pid\n")
    quit()

f = None

try:
    f = open(statusfilename, "r")
except FileNotFoundError:
    sys.stderr.write("file " + statusfilename + " cannot be found\n")
    quit()


timer_start = time.perf_counter()
timer_end = 0

while timer_end - timer_start < 5:  # 5 second timer
    if len(open(statusfilename).readlines()) > 0:  # Checks if file is empty
        break
    timer_end = time.perf_counter()

if len(open(statusfilename).readlines()) == 0:  # Checks if file is still empty
    sys.stderr.write("status timeout\n")
    quit()

lines = f.readlines()

for line in lines:  # Prints out the contents of the status file
    print(line.strip())

f.close()

f = open(statusfilename, "w")  # Opens file in write mode to set file contents to empty
f.close()

quit()


