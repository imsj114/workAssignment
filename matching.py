from tkinter.filedialog import askopenfilename
import sys
from collections import defaultdict
from enum import Enum
from tabulate import tabulate

DAYS = 5
MIN_WORK_PER_PERSON = 10
MAX_WORK_PER_PERSON = 13
class State(Enum):
    EMPTY = 0
    CLASS = 1
    WORK = 2

defaultDayTime = \
    [((8, 30), (10, 00)),\
     ((10, 00), (10, 30)),\
     ((10, 30), (11, 00)),\
     ((11, 00), (11, 30)),\
     ((11, 30), (12, 00)),\
     ((13, 00), (13, 30)),\
     ((13, 30), (14, 00)),\
     ((14, 00), (14, 30)),\
     ((14, 30), (15, 00)),\
     ((15, 00), (15, 30)),\
     ((15, 30), (16, 00)),\
     ((16, 00), (16, 30)),\
     ((16, 30), (17, 00)),\
     ((17, 00), (17, 30)),\
     ((17, 30), (18, 00)),\
     ((18, 00), (19, 30))]
defaultPriority = \
    [5000, 300, 200, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 300, 5000]
DAY_SLOTS = len(defaultDayTime)

def timeToInt(x):
    return x[0]*2 + x[1]//30

def workDuration(tid):
    return timeToInt(defaultDayTime[tid][1]) - timeToInt(defaultDayTime[tid][0])

def adjacent(tid1, tid2):
    if tid1 > tid2:
        tid1, tid2 = tid2, tid1
    return defaultDayTime[tid1][1] == defaultDayTime[tid2][0]

def timeDist(tid1, tid2):
    if tid1 > tid2:
        tid1, tid2 = tid2, tid1
    return timeToInt(defaultDayTime[tid2][0]) - timeToInt(defaultDayTime[tid1][1])

class AssignmentTable():
    def __init__(self):
        self.table = [[list() for _ in range(DAY_SLOTS)] for _ in range(DAYS)]

    def assignPerson(self, day, tid, person):
        self.table[day][tid].append(person)
    
    def getAssignment(self, day, tid):
        return self.table[day][tid]
    
    def numAssigned(self, day, tid):
        return len(self.table[day][tid])

    def asTable(self):
        newTable = []
        for tid in range(DAY_SLOTS):
            newTable.append([" ".join(self.table[day][tid]) for day in range(DAYS)])
        return newTable

class ScheduleTable():
    def __init__(self, classSchedule):
        self.scheduleTable = [[State.EMPTY]*DAY_SLOTS for _ in range(DAYS)]
        self.weightTable = [[0.0]*DAY_SLOTS for _ in range(DAYS)]
        self.numWorks = 0

        classIter = iter(classSchedule)
        # Assume that tid is in order
        for day in range(DAYS):
            for tid in range(DAY_SLOTS):
                self.scheduleTable[day][tid] = State(next(classIter))
    
    def getWeight(self, day, tid):
        return self.weightTable[day][tid]
    
    def getSchedule(self, day, tid):
        return self.scheduleTable[day][tid]
    
    def updateWeight(self, numAvailTable, assignmentTable):
        multiplier = [[1.0]*DAY_SLOTS for _ in range(DAYS)]
        # 0. null out infeasible arrays according to the rule
        # (0-1) If the slot is already occupied, it is not possible to assign it again
        for day in range(DAYS):
            for tid in range(DAY_SLOTS):
                self.weightTable[day][tid] = 0.0
                if self.scheduleTable[day][tid] != State.EMPTY:
                    multiplier[day][tid] = float('-inf')
                    
        # (0-2) numWorks + newWork should not exceed MAX_WORK_PER_PERSON
        for tid in range(DAY_SLOTS):
            if self.numWorks + workDuration(tid) > MAX_WORK_PER_PERSON:
                for day in range(DAYS):
                    multiplier[day][tid] = float('-inf')
        # (0-3) Special rule: one worker cannot be assigned to more than one earliest/latest slot
        for tid in (0, -1):
            if any(self.scheduleTable[day][tid] == State.WORK for day in range(DAYS)):
                for day in range(DAYS):
                    multiplier[day][tid] = float('-inf')

        # 1. Every slot must have 1~2 worker.
        # (1-1) If the slot is empty, inversely proportional to number of available candidates
        #       This makes the assignment prioritize slots with limited possible workers.
        # (1-2) If the slot already has worker assigned, less prioritized
        for day in range(DAYS):
            for tid in range(DAY_SLOTS):
                alpha = defaultPriority[tid]/(numAvailTable[day][tid]+0.01)
                self.weightTable[day][tid] += alpha
                if assignmentTable.numAssigned(day, tid) == 1 and tid != 0 and tid != DAY_SLOTS-1:
                    multiplier[day][tid] *= 0.2
        
        # 2. Each work should be at least 1 hour long.
        # (2-1) high priority to work-adjacent slot, especially if current work slot is single
        for day in range(DAYS):
            startTid = None
            for tid in range(DAY_SLOTS):
                if self.scheduleTable[day][tid] == State.WORK and startTid == None:
                    startTid = tid
                if (tid+1 == DAY_SLOTS or self.scheduleTable[day][tid+1] != State.WORK) and startTid != None:
                    endTid = tid
                    # update startTid-1, endTid+1
                    beta = 100.0 if startTid == endTid else 20.0
                    if startTid-1 >= 0 and adjacent(startTid-1, startTid):
                        self.weightTable[day][startTid-1] += beta
                    if endTid+1 < DAY_SLOTS and adjacent(endTid, endTid+1):
                        self.weightTable[day][endTid+1] += beta
                    startTid = None
        
        # 3. priority to slots close to class schedule
        for day in range(DAYS):
            startTid, endTid = None, None
            for tid in range(DAY_SLOTS):
                if self.scheduleTable[day][tid] != State.EMPTY:
                    startTid = tid
                    break
            for tid in range(DAY_SLOTS-1, -1, -1):
                if self.scheduleTable[day][tid] != State.EMPTY:
                    endTid = tid
                    break
            if startTid == None:
                continue
            for tid in range(DAY_SLOTS):
                gamma = 10
                if tid < startTid:
                    gamma *= (1 - 0.01*(timeDist(tid, startTid)**2))
                elif tid > endTid:
                    gamma *= (1 - 0.1*(timeDist(tid, endTid)**2))
                self.weightTable[day][tid] += gamma

        # 4. Global adjustment according to each person, such as numWorks
        
        delta = 1.0 - (0.01*self.numWorks)
        for day in range(DAYS):
            for tid in range(DAY_SLOTS):
                multiplier[day][tid] *= delta
                if MIN_WORK_PER_PERSON < self.numWorks:
                    multiplier[day][tid] *= 0.7

        # 5. Apply global multiplier
        for day in range(DAYS):
            for tid in range(DAY_SLOTS):
                self.weightTable[day][tid] *= multiplier[day][tid]
            

    def assignWork(self, day, tid):
        if self.scheduleTable[day][tid] != State.EMPTY:
            print("ERROR", day, tid)
            return
        self.scheduleTable[day][tid] = State.WORK
        # Update numWorks
        self.numWorks += workDuration(tid)

class TableMatcher():
    def __init__(self, classSchedules):
        self.numPeople = len(classSchedules)
        
        self.scheduleTables = {}
        for person, classTable in classSchedules.items():
            self.scheduleTables[person] = ScheduleTable(classTable)
        self.assignmentTable = AssignmentTable()

    def match(self):        
        # One cell by one, assign a cell
        for _ in range(DAYS * len(defaultDayTime) * 2):
            # 1. Update weights
            numAvailTable = [[0]*DAY_SLOTS for _ in range(DAYS)]
            for scheduleTable in self.scheduleTables.values():
                if scheduleTable.numWorks < MAX_WORK_PER_PERSON:
                    for day in range(DAYS):
                        for tid in range(DAY_SLOTS):
                            if scheduleTable.getSchedule(day, tid) == State.EMPTY:
                                numAvailTable[day][tid] += 1
            for scheduleTable in self.scheduleTables.values():
                scheduleTable.updateWeight(numAvailTable, self.assignmentTable)

            # 2. Choose a slot with max weight
            maxPerson, maxDay, maxTid, maxWeight = None, None, None, float('-inf')
            for day in range(DAYS):
                for tid in range(DAY_SLOTS):
                    if self.assignmentTable.numAssigned(day, tid) < 2:
                        for person, scheduleTable in self.scheduleTables.items():
                            weight = scheduleTable.getWeight(day, tid)
                            if weight > maxWeight:
                                maxPerson, maxDay, maxTid, maxWeight = person, day, tid, weight

            # if (maxPerson == "H" or maxPerson == "J") and maxTid == 15:
            #     print("> ")
            #     print("A", self.scheduleTables["A"].getWeight(3, 15))
            #     print("H", self.scheduleTables["H"].getWeight(3, 15))
            #     print("J", self.scheduleTables["J"].getWeight(3, 15))
            #     print(numAvailTable[1][15], numAvailTable[2][15], numAvailTable[4][15])
            #     print("<")
            # print(f"{maxPerson}\t{maxDay}\t{maxTid}\t{maxWeight}")

            # 3. Assign
            if maxPerson == None:
                break
            self.assignmentTable.assignPerson(maxDay, maxTid, maxPerson)
            self.scheduleTables[maxPerson].assignWork(maxDay, maxTid)
            
    def assignment(self):
        return self.assignmentTable.asTable()
    
    def workHours(self):
        return {person:table.numWorks for person, table in self.scheduleTables.items()}

def parseInput(inputFile):
    timeTable = {}
    with open(inputFile, "r") as openFile:
        for line in openFile:
            name, available = line.split()
            timeTable[name] = list(map(int, available))
    return timeTable

def printResult(matcher):
    print("Assignment")
    assignment = matcher.assignment()
    print(tabulate(assignment, headers=["Mon", "Tue", "Wed", "Thr", "Fri"]))
    
    print("Total Works")
    print(matcher.workHours())
    

def main():
    if len(sys.argv) < 2:
        inputFile = askopenfilename()
    else:
        inputFile = sys.argv[1]
    classSchedule = parseInput(inputFile)
    matcher = TableMatcher(classSchedule)
    matcher.match()
    printResult(matcher)
    if len(sys.argv) < 2:
        input("Press enter to exit..")

if __name__ == "__main__":
    main()