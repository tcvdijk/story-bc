#!/usr/bin/python
# -*- coding: utf-8 -*-

#already been checked
import sys
import util

if __name__ =='__main__':
    util.error('This file should not be called directly.\
                Use \'main.py -h\' for help.')

try:
    import re
    import math
except Exception as e:
    util.error('There are python packages missing', e)

class Instance(object):
    """This is the parent class for all instances."""

    def __init__(self, filepath, options):
        super(Instance, self).__init__()
        self.options = options

        #get all lines from instance file.
        instance_file = open(filepath)
        self.lines = instance_file.read().splitlines()
        instance_file.close()

        #get number of meetings and number of character.
        self.k = 0
        self.n = 0
        try:
            self.k = int(self.lines[0].split(',')[0].strip())
            self.n = int(self.lines[0].split(',')[1].strip())
        except Exception as e:
            print('Unsupported Instance: See \'format.txt\' for help.')
            print(e)
            print('exiting...')
            quit()

        #get events
        meetings = list()
        events = list()
        _id = 0
        try:
            for line in self.lines:
                #if this is not a comment.
                if not re.match('^c', line):
                    #if this is a meeting
                    if re.match('^m', line):
                        data = line.split(',,')

                        members = list()
                        for char in data[3].split(','):
                            members.append(int(char.strip()))
                        members = tuple(members)

                        start = int(data[1].strip())
                        end = int(data[2].strip())

                        events.append((_id, 0, end, members))
                        events.append((_id, 1, start, members))
                        meetings.append((_id, start, end, members))
                    #if this is a born event.
                    if re.match('^b', line):
                        data = line.split(',,')

                        time = int(data[1].strip())
                        char = int(data[2].strip())

                        events.append((_id,3,time,char))
                    #if this is a death event.
                    if re.match('^d', line):
                        data = line.split(',,')

                        time = int(data[1].strip())
                        char = int(data[2].strip())

                        events.append((_id,4,time,char))
                    #increment id
                    _id += 1
        except Exception as e:
            util.error('Unsupported Instance: See \'format.txt\' for help.', e)

        if len(meetings) != self.n:
            util.error('Unsupported Instance: See \'format.txt\' for help.', e)

        self.events = tuple(sorted(events, key=lambda x: (x[2], -x[1])))
        self.meetings = tuple(sorted(meetings, key=lambda tup: tup[1]))

#a SAT instance (in our context) is a ILP2 instance
#it can't be solved with an ILP solver anymore though
#this program only supports SAT
class ILP2_instance(Instance):
    """This is an instance of ILP2 as described in the paper."""

    def __init__(self, filepath, options):
        super(ILP2_instance, self).__init__(filepath, options)
        self.build()

    def build(self):
        #create layers
        active_meetings = list()
        merged_events = list()
        meeting_groups = list()
        alive = list()

        meetings = self.meetings
        events = self.events
        last_event = events[0]

        for event in events:
            if event[2] == last_event[2]:
                merged_events.append(event)
            else:
                if merged_events:
                    for merged_event in merged_events:
                        if merged_event[1] == 1:
                            for meeting in meetings:
                                if meeting[0] == merged_event[0]:
                                    active_meetings.append(meeting)
                        if merged_event[1] == 3:
                            alive.append(merged_event[3])

                    for merged_event in merged_events:
                        if merged_event[1] == 0:
                            for meeting in meetings:
                                if meeting[0] == merged_event[0]:
                                    active_meetings.remove(meeting)
                        if merged_event[1] == 4:
                            alive.remove(merged_event[3])

                    if active_meetings:
                        meeting_groups.append((tuple(active_meetings),tuple(alive)))

                    merged_events = list()
                    merged_events.append(event)
            last_event = event
        self.meeting_groups = meeting_groups

    def return_instance(self):
        return(self.k,tuple(self.meeting_groups), self.options)

class SAT_instance(ILP2_instance):
    """This is an instance of SAT as described in the paper."""

    def __init__(self, filepath, number_of_layer):
        super(SAT_instance, self).__init__(filepath, number_of_layer)
