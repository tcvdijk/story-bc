#!/usr/bin/python
# -*- coding: utf-8 -*-

#already been checked
import util
import time

if __name__ =='__main__':
    util.error('This file should not be called directly.\n\
Use \'main.py -h\' for help.')

try:
    import functools
    import time
except Exception as e:
    util.error('There are python packages missing', e)

class SAT_solver(object):
    """This is the solver for SAT"""

    def __init__(self, number_of_characters, meeting_groups, layers, use_timestamps, filename):
        super(SAT_solver, self).__init__()
        self.number_of_characters = number_of_characters
        self.meetings = meeting_groups
        self.meeting_groups = meeting_groups
        self.layers = layers
        self.use_timestamps = use_timestamps
        self.filename = filename
        self.time_millis = str(int(round(time.time() * 1000)))

    def build(self):
        numberOfVariables = self.createVariableLists()
        miniSATfile = open("tmp/miniSATInput.sat","w")
        self.numberOfClauses = self.writeClauses(miniSATfile,numberOfVariables)
        self.printInfo.write(str(self.layers)+"\n"+str(self.number_of_characters))
        self.printInfo.close()
        miniSATfile.close()

    #creates variables and returns their number
    def createVariableLists(self):
        a = list()
        b = list()
        c = list()

        x = list()
        cr = list()

        q = list()
        #y = list()

        d = list()
        layersLen = self.layers
        k = self.number_of_characters
        meetings = self.meetings

        workingList = list()
        workingList2 = list()
        globalCount = 1

        #fill a
        for i in range(layersLen):
            for j in range(k):
                workingList.append(str(globalCount))
                globalCount += 1
            a.append(tuple(workingList))
            workingList = list()
        a = tuple(a)

        #fill b
        for i in range(layersLen):
            for j in range(k):
                workingList.append(str(globalCount))
                globalCount += 1
            b.append(tuple(workingList))
            workingList = list()
        b = tuple(b)

        #fill c
        for i in range(layersLen):
            for j in range(k):
                workingList.append(str(globalCount))
                globalCount += 1
            c.append(tuple(workingList))
            workingList = list()
        c = tuple(c)

        #fill x
        #store information for printing
        printInfo = open("tmp/printInfo.dat","w")
        printInfo.write(str(globalCount)+"\n")
        for i in range(layersLen):
            for j in range(k):
                for ki in range(k):
                    workingList.append(str(globalCount))
                    globalCount += 1
                workingList2.append(tuple(workingList))
                workingList  = list()
            x.append(tuple(workingList2))
            workingList2 = list()
        x = tuple(x)
        #store more information for printing
        printInfo.write(str(globalCount-1)+"\n")

        #fill cr
        for i in range(layersLen-1):
            for j in range(k):
                for ki in range(k):
                    workingList.append(str(globalCount))
                    globalCount += 1
                workingList2.append(tuple(workingList))
                workingList  = list()
            cr.append(tuple(workingList2))
            workingList2 = list()
        cr = tuple(cr)

        #fill q
        for i in range(layersLen):
            for j in range(len(meetings)):
                workingList.append(str(globalCount))
                globalCount += 1
            q.append(tuple(workingList))
            workingList = list()
        q = tuple(q)

        #fill d
        printInfo.write(str(globalCount)+"\n")
        for r in range(layersLen):
            for i in range(k):
                workingList.append(str(globalCount))
                globalCount += 1
            d.append(tuple(workingList))
            workingList = list()
        d = tuple(d)
        printInfo.write(str(globalCount-1)+"\n")

        self.a = a
        self.b = b
        self.c = c

        self.x = x
        self.cr = cr

        self.q = q

        self.d = d
        self.printInfo = printInfo

        return globalCount - 1

    #writes clauses to file and returns number of clauses
    def writeClauses(self, myfile, numberOfVariables):
        a = self.a
        b = self.b
        c = self.c
        x = self.x
        k = self.number_of_characters
        q = self.q
        d = self.d
        cr = self.cr
        layersLen = self.layers
        meetings = self.meeting_groups
        numberOfClauses = 0

        L = list()
        
        # 4.15 - 4.16
        for r in range(layersLen):
            for i in range(k):
                if True: #oneDeadOnLayer(r,[i]) == 0:
                    #a+b+c=1
                    #L.append("\n c ###########################################")
                    #L.append("\n c i="+(i)+" r="+(r))
                    L.append("\n %s %s %s %s 0" % ((a[r][i]),(b[r][i]),(c[r][i]),(d[r][i]) ) )
                    L.append("\n -%s -%s %s %s 0" % ((a[r][i]),(b[r][i]),(c[r][i]),(d[r][i])) )
                    L.append("\n -%s %s -%s %s 0" % ((a[r][i]),(b[r][i]),(c[r][i]),(d[r][i])) )
                    L.append("\n %s -%s -%s %s 0" % ((a[r][i]),(b[r][i]),(c[r][i]),(d[r][i])) )
                    L.append("\n -%s -%s -%s %s 0" % ((a[r][i]),(b[r][i]),(c[r][i]),(d[r][i])) ) #tvd
                    #L.append("\n c ###########################################")

                    numberOfClauses += 5 #tvd

        for r in range(layersLen):
            for i in range(k):
                for j in range(k):
                    if i != j: #and oneDeadOnLayer(r,[i,j]) == 0:
                        #x+x=1
                        #L.append("\n c ###########################################")
                        #L.append("\n c i="+(i)+" j="+(j)+" r="+(r))
                        # 4.8
                        L.append("\n %s %s %s %s 0" % ((x[r][i][j]),(x[r][j][i]),(d[r][i]),(d[r][j])) )
                        # 4.9
                        L.append("\n -%s -%s %s %s 0" % ((x[r][i][j]),(x[r][j][i]),(d[r][i]),(d[r][j])) )

                        #B over C
                        # 4.17
                        L.append("\n %s -%s -%s %s %s 0" % ((x[r][i][j]),(b[r][i]),(c[r][j]),(d[r][i]),(d[r][j])) )
                        #L.append("\n c ###########################################")
                        numberOfClauses += 3

        for r in range(layersLen-1):
            for i in range(k):
                for j in range(k):
                    if i != j:# and oneDeadOnLayer(r,[i,j]) == 0:
                        #L.append("\n c ###########################################")
                        #L.append("\n c i="+(i)+" j="+(j)+" r="+(r))
                        #cross
                        # 4.11 - 4.12
                        L.append("\n %s %s -%s %s %s 0" % ((cr[r][i][j]),(x[r][i][j]),(x[r+1][i][j]),(d[r][i]),(d[r][j])) )
                        L.append("\n %s %s -%s %s %s 0" % ((cr[r][i][j]),(x[r+1][i][j]),(x[r][i][j]),(d[r][i]),(d[r][j])) )

                        # 4.13 - 4.14
                        L.append("\n -%s %s %s %s %s 0" % ((cr[r][i][j]),(x[r][i][j]),(x[r+1][i][j]),(d[r][i]),(d[r][j])) )
                        L.append("\n -%s %s %s %s %s 0" % ((cr[r][i][j]),(x[r][j][i]),(x[r+1][j][i]),(d[r][i]),(d[r][j])) )

                        #B and C cross
                        # 4.21 - 4.24
                        L.append("\n %s -%s -%s %s %s 0" % ((cr[r][i][j]),(b[r][i]),(c[r][j]),(d[r][i]),(d[r][j])) )
                        L.append("\n -%s -%s %s %s 0" % ((cr[r][i][j]),(a[r][i]),(d[r][i]),(d[r][j])) )
                        L.append("\n -%s -%s -%s %s %s 0" % ((cr[r][i][j]),(b[r][i]),(b[r][j]),(d[r][i]),(d[r][j])) )
                        L.append("\n -%s -%s -%s %s %s 0" % ((cr[r][i][j]),(c[r][i]),(c[r][j]),(d[r][i]),(d[r][j])) )
                        #L.append("\n c ###########################################")

                        #force blockcrossings
                        #L.append("\n "+(y[r])+" -"+(cr[r][i][j])+" 0")

                        numberOfClauses += 8

        for r in range(layersLen):
            for i in range(k):
                for j in range(k):
                    for ki in range(k):
                        if i != j and j != ki and i != ki:# and oneDeadOnLayer(r,[i,j,ki]) == 0:
                            #3-cycle
                            # 4.10
                            L.append("\n %s %s %s %s %s %s 0" % ((x[r][i][j]),(x[r][j][ki]),(x[r][ki][i]),(d[r][i]),(d[r][j]),(d[r][ki])))
                            L.append("\n -%s -%s -%s %s %s %s 0" % ((x[r][i][j]),(x[r][j][ki]),(x[r][ki][i]),(d[r][i]),(d[r][j]),(d[r][ki])))

                            #B tvd continuous
                            # 4.18
                            L.append("\n %s -%s -%s -%s -%s %s %s %s 0" % ((b[r][j]),(x[r][i][j]),(x[r][j][ki]),(b[r][i]),(b[r][ki]),(d[r][i]),(d[r][j]),(d[r][ki])))

                            #C continuous
                            # 4.19
                            L.append("\n %s -%s -%s -%s -%s %s %s %s 0" % ((c[r][j]),(x[r][i][j]),(x[r][j][ki]),(c[r][i]),(c[r][ki]),(d[r][i]),(d[r][j]),(d[r][ki])))

                            #B and C neighboring
                            # 4.20
                            L.append("\n -%s -%s -%s -%s -%s %s %s %s 0" % ((a[r][j]),(x[r][i][j]),(x[r][j][ki]),(b[r][i]),(c[r][ki]),(d[r][i]),(d[r][j]),(d[r][ki])))

                            numberOfClauses += 5 #tvd

                            #meetings
                            #4.28 - 4.29
                            count = 0
                            for mg in meetings:
                                for meeting in mg[0]:
                                    if i in meeting[3] and ki in meeting[3] and j not in meeting[3]:
                                        #L.append("\n c ###########################################")
                                        #L.append("\n c this is the "+(count)+"-th meeting group")
                                        #L.append("\n c i="+(i)+" j="+(j)+" k="+(ki)+" r="+(r))
                                        #L.append("\n c "+(meeting))
                                        L.append("\n -%s %s -%s 0" % ((q[r][count]),(x[r][i][j]),(x[r][ki][j])))
                                        L.append("\n -%s -%s %s 0" % ((q[r][count]),(x[r][i][j]),(x[r][ki][j])))
                                        #L.append("\n c ###########################################")

                                        numberOfClauses += 2
                                count += 1

        for r in range(layersLen):
            count = 0
            for mg in meetings:
                #count2 = 0
                # 4.25
                #for mg1 in meetings:
                #    if count != count2 and set(mg[1]) != set(mg1[1]):
                #        L.append("\n -%s -%s 0" % ((q[r][count]),(q[r][count2])))
                #        numberOfClauses += 1
                #    count2 += 1
                for i in range(k):
                    if i in mg[1]:
                        # 4.4
                        L.append("\n -%s -%s 0" % ((q[r][count]),(d[r][i])))
                        numberOfClauses += 1
                    else:
                        #L.append("\n ")
                        #count3 = 0
                        #for mg1 in meetings:
                        #    if i in mg1[1]:
                        #        L.append((q[r][count3])+" ")
                        #    count3 += 1
                        #L.append((d[r][i])+" 0")
                        
                        # 4.5 >>>neu<<<
                        L.append("\n -%s %s 0" % ((q[r][count]),(d[r][i])))
                        numberOfClauses += 1
                count += 1

        for mg in range(len(meetings)):
            # 4.1 a
            L.append("\n ")
            for r in range(layersLen):
                L.append((q[r][mg])+" ")
            L.append("0")
            numberOfClauses += 1

        #for r in range(layersLen-1):
        for r in range(1,layersLen):
            for i in range(k):
                # 4.6
                L.append("\n")
                for mg in range(len(meetings)):
                    L.append(" "+(q[r][mg]))
                L.append(" %s -%s 0" % ((d[r][i]),(d[r-1][i])))
                # 4.7
                L.append("\n")
                for mg in range(len(meetings)):
                    L.append(" "+(q[r][mg]))
                L.append(" -%s %s 0" % ((d[r][i]),(d[r-1][i])))

                numberOfClauses += 2

        # 4.1b
        for mg in range(len(meetings)):
            for r0 in range(layersLen):
                for r1 in range(layersLen):
                    if r0 != r1:
                        L.append("\n -%s -%s 0" % ((q[r0][mg]),(q[r1][mg])))
                        numberOfClauses += 1

        # 4.2
        for mg in range(len(meetings)):
            if mg > 0:
                for r0 in range(layersLen):
                    L.append("\n -"+(q[r0][mg])+" ")
                    for r1 in range(r0+1):
                        L.append((q[r1][mg-1])+" ")
                    L.append("0")
                    numberOfClauses += 1


        for r in range(layersLen-1):
            for i in range(k):
                for j in range(k):
                    if i != j:
                        for ki in range(k):
                            if i != ki and j != ki:
                                # 4.26
                                L.append("\n %s -%s -%s %s %s %s %s 0" % ((d[r][i]),(d[r+1][i]),(cr[r][j][ki]),(d[r][j]),(d[r][ki]),(d[r+1][j]),(d[r+1][ki])))
                                # 4.27
                                L.append("\n -%s %s -%s %s %s %s %s 0" % ((d[r][i]),(d[r+1][i]),(cr[r][j][ki]),(d[r][j]),(d[r][ki]),(d[r+1][j]),(d[r+1][ki])))
                                numberOfClauses += 2

        # 4.3
        L.append("\n %s 0" % ((q[0][0])))


        myfile.write( " p cnf "+str(numberOfVariables)+" "+str(numberOfClauses))
        myfile.write( ''.join(L) )
        
        return numberOfClauses