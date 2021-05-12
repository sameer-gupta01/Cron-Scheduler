#! /usr/bin/bash

#The contents of testConfig.py and testOutput.py are at the bottom of runner.py as docstrings
#This shell script used a set of .in and .out files to compare expected output to actual output using diff.
#This allowed for effective automation of the testcases and allowed me to test a wide variety of scenarios

echo "Running tests for possible configuration file errors"
echo ""
count=0 # number of test cases run so far


for test in configTests/*.in; do
    name=$(basename $test .in) #name of test
    expected=configTests/$name.out #expected output
    config=configTests/$name.in #config file

    echo "Running configuration test $name"
    
    python3 testConfig.py $config #updates the configuration file for runner.py with test configuration
    
    python3 runner.py | diff -B - $expected || echo "Test $name: failed!" #compares output vs expected output - will print failed if the output is different

    count=$((count+1))
done

echo "Ran $count configuration tests!"
echo ""
echo "Running tests for runstatus.py output"
echo ""
count=0 # number of test cases run so far

for test in outputTests/*.in; do
    name=$(basename $test .in) #name of test
    expected=outputTests/$name.out #expected output
    config=outputTests/$name.in #config file

    echo "Running output test $name"
    
    python3 testOutput.py $config #updated the time and contents of .runner.conf - time would be 1 min ahead of current time
    
    python3 runner.py & #runs runner.py in background
    sleep 1 # delays shell script for a second to allow for runner.py to be properly initialised
    python3 runstatus.py > status.txt #saves the initial output of runstatus to a intermediate file
    counter=0
    >$expected # deletes contents of .out file so it can be updated

    cat status.txt | while read line
    do
        datetime=$(echo $line | awk '{print $4, $5, $6, $7, $8, $9, $10}') #extracts expected datetime from the output of runstatus

        if [ $counter == 0 ] # determines whether this is the first status line of runstatus - should have been "ran" not "will run at"
        then
            echo "ran $datetime" >> $expected #writes appropriate expected output to .out file
        else
            echo "will run at $datetime" >> $expected
        fi
        counter=$((counter+1))
    done
    
    sleep 60 #waits till program has been run
    python3 runstatus.py | diff - $expected || echo "Test $name: failed!" # examines difference between expected and actual output

    count=$((count+1))
done

echo ""
echo "Ran $count tests!"