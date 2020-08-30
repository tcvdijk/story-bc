#!/usr/bin/python
# -*- coding: utf-8 -*-

#import I/O tools for 'python <-> system'
try:
    import time
    import math
    import sys
    import os
    import math
    import gc
    from os.path import basename
    from subprocess import call
except Exception as e:
    print('There are python packages missing')
    print('Printing error stack:')
    print(e)
    print('exiting...')
    quit()

try:
    import util
    from my_timer import Timer as tim
except Exception as e:
    print('Integrity check failed')
    print('\'util.py\' missing')
    print(e)
    print('exiting...')
    quit()

#init options
filepath = None
number_of_layers = 1
use_timestamps = False
do_print = True
preamble = False

#get all the input
try:
    filepath = sys.argv[1]
    if filepath == '-h':
        print('Usage: main.py <filepath> [options]')
        print('Options:\n\'-t\' for printing timestamps in output file\n\
     names. Use this if you plan to keep the results.')
        print('\'-np\' for not printing out results.\n\
      Probably has no real use case.')
        print('\'-tikz\' for writing the tikz preamble directly to the output.\n\
        Use this to create standalone output, ready for latex to compile.')
        sys.exit(0)
    for arg in range(len(sys.argv)):
        if sys.argv[arg] == '-t':
            use_timestamps = True
        if sys.argv[arg] == '-np':
            do_print = False
        if sys.argv[arg] == '-tikz':
            preamble = True
except Exception as e:
    util.error('Not like this :(. Use \'main.py -h\' for help.')

#get the basename to later name the output file
filename = basename(filepath)

try:
    from instance_generator import SAT_instance as imp
    from solver import SAT_solver as sol
except Exception as e:
    util.error('Integrity check failed. Some files are missing', e)

#timers
timer_complete = tim()
timer_only_solve = tim()

devnull = open(os.devnull, 'w')
is_solution_found = False
is_in_subroutine = False

timer_complete.start_stop()

fperf = open('perf.txt','w')
resultfile = open(filepath+'.result','w')

mem_max = 0
total_minisat_time = 0
search_factor = 2
max_unsat = 0
min_sat = float("inf")
number_of_layers = 1
while not min_sat - max_unsat == 1:
    print(str(number_of_layers)+' layers...')
    instance = imp(filepath, number_of_layers)
    args = instance.return_instance()
    solver = sol(args[0], args[1], args[2], use_timestamps, filename)
    wstart = time.time()
    solver.build()
    wend = time.time()
    tstart = time.time()
    call(["minisat","tmp/miniSATInput.sat","tmp/output.sat"], stdout=devnull, stderr=devnull)
    tend = time.time()
    total_minisat_time += tend-tstart
    fperf.write(str(number_of_layers)+'\t'+str(1000*(tend-tstart))+'\t'+str(1000*(wend-wstart))+'\n')
    output_lines = open('tmp/output.sat').readlines()
    mem_now = int(output_lines[0])
    if mem_now > mem_max: mem_max = mem_now
    sat = len(output_lines)>=3
    
    #number_of_layers += 1
    if sat:
        min_sat = number_of_layers
        #sat
        if min_sat==float("inf"):
            number_of_layers = int((min_sat+max_unsat)/2)
        else:
            min_sat = number_of_layers
            number_of_layers = int((min_sat+max_unsat)/2)
    else:
        #unsat
        max_unsat = number_of_layers
        if min_sat==float("inf"):
            old = number_of_layers
            number_of_layers = int(number_of_layers * search_factor)
            if old == number_of_layers: number_of_layers += 1
        else:
            number_of_layers = int((min_sat+max_unsat)/2)

resultfile.write( str(len(solver.meetings))+'\t'+str(total_minisat_time)+'\t'+str(mem_max)+'\n')
print "meetings", len(solver.meetings)
print "max_unsat",max_unsat
print "min_sat",min_sat
print "opt", min_sat
print "total_minisat_time", total_minisat_time
print "max_minisat_mem", mem_max