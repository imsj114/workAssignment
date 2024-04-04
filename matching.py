import sys
from collections import defaultdict
from enum import Enum

DAYS = 5
MIN_SLOT_PER_PERSON = 10
MAX_SLOT_PER_PERSON = 13

class State(Enum):
    EMPTY = 0
    CLASS = 1
    WORK = 2

def timeToTID(x):
    h, m = x
    return h*2 + m//30
def TIDToTime(tid):
    return (tid//2, (tid%2)*30)

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
DAY_SLOTS = len(defaultDayTime)

class AssignmentTable():
    def __init__(self):
        self.table = [[None]*DAY_SLOTS for _ in range(DAYS)]

    def assignPerson(self, day, tid, person):
        self.table[day][tid] = person
    
    def getAssignment(self, day, tid):
        return self.table[day][tid]

    def asTable(self):
        return self.table
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
    
    def updateWeight(self, numAvailTable):
        for day in range(DAYS):
            for tid in range(DAY_SLOTS):
                if self.scheduleTable[day][tid] == State.EMPTY:
                    self.weightTable[day][tid] = 100.0/(numAvailTable[day][tid]+1)
                else:
                    self.weightTable[day][tid] = 0.0

    def assignWork(self, day, tid):
        if self.scheduleTable[day][tid] != State.EMPTY:
            raise RuntimeError()
        self.scheduleTable[day][tid] = State.WORK

class TableMatcher():
    def __init__(self, classSchedules):
        self.numPeople = len(classSchedules)
        
        self.scheduleTables = {}
        for person, classTable in classSchedules.items():
            self.scheduleTables[person] = ScheduleTable(classTable)
        self.assignmentTable = AssignmentTable()

    def match(self):        
        # One cell by one, assign a cell
        for _ in range(DAYS * len(defaultDayTime)):
            # 1. Update weights
            numAvailTable = [[0]*DAY_SLOTS for _ in range(DAYS)]
            for scheduleTable in self.scheduleTables.values():
                for day in range(DAYS):
                    for tid in range(DAY_SLOTS):
                        if scheduleTable.getSchedule(day, tid) == State.EMPTY:
                            numAvailTable[day][tid] += 1
            for scheduleTable in self.scheduleTables.values():
                scheduleTable.updateWeight(numAvailTable)

            # 2. Choose a slot with max weight
            maxPerson, maxDay, maxTid, maxWeight = None, None, None, float('-inf')
            for day in range(DAYS):
                for tid in range(DAY_SLOTS):
                    if self.assignmentTable.getAssignment(day, tid) == None:
                        for person, scheduleTable in self.scheduleTables.items():
                            weight = scheduleTable.getWeight(day, tid)
                            if weight > maxWeight:
                                maxPerson, maxDay, maxTid, maxWeight = person, day, tid, weight
            # 3. Assign
            if maxPerson == None:
                break
            self.assignmentTable.assignPerson(maxDay, maxTid, maxPerson)
            self.scheduleTables[maxPerson].assignWork(maxDay, maxTid)
            
        return self.assignmentTable.asTable()

def parseInput(inputFile):
    timeTable = {}
    with open(inputFile, "r") as openFile:
        for line in openFile:
            name, available = line.split()
            timeTable[name] = list(map(int, available))
    return timeTable

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 matching.py [input file]")
        exit(0)
    inputFile = sys.argv[1]
    classSchedule = parseInput(inputFile)
    matcher = TableMatcher(classSchedule)
    result = matcher.match()
    print(result)

if __name__ == "__main__":
    main()