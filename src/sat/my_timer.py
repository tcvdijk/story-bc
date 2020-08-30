#!/usr/bin/python
# -*- coding: utf-8 -*-
#timer class for time measurements

if __name__ =='__main__':
    print('This file should not be called directly.\
           Use \'python main.py -h\' for help.')
    print('exiting...')
    quit()

#already been checked
import time

class Timer(object):
    """docstring for Timer."""

    def __init__(self):
        super(Timer, self).__init__()
        self._current_time = 0
        self._t_start = 0
        self._is_running = False

    def start_stop(self):
        if not self._is_running:
            self._t_start = time.time()
            self._is_running = True
        else:
            self._current_time += time.time() - self._t_start
            rval = self._current_time
            self._current_time = 0
            self._is_running = False
            return rval

    def resume_pause(self):
        if not self._is_running:
            self._t_start = time.time()
            self._is_running = True
        else:
            self._current_time += time.time() - self._t_start
            self._is_running = False

    def force_stop(self):
        rval = self._current_time
        self._current_time = 0
        self._is_running = False
        return rval
