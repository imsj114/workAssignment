import sys
from collections import defaultdict

MIN_SLOT_PER_PERSON = 10
MAX_SLOT_PER_PERSON = 13

def timeToTID(h, m):
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

class DayTable():
    def __init__(self):
        self.cells = {tid:0 for tid in map(timeToTID, defaultDayTime)}

class WeekTable():
    def __init__(self):
        self.numDays = 5
        self.dayTables = [DayTable()] * 5

class WeightTable(WeekTable):
    def updateWeight(self):
        pass
    
    def maxCell(self):
        pass
        # return (day, tid, weight)
class AssignmentTable(WeekTable):
    def assignNewCell(self, costTables):
        for person, costTable in costTables.items():
            costTable.maxCell()

class TableMatcher():
    def __init__(self, timeTable):
        self.timeTable = timeTable
        self.numPeople = len(self.timeTable)
        self.assignments = WeekTable()
    
    def weight(self, person, slot, idx):
        # alpha: higher if idx is large, dramatic decrease after MIN_SLOT_PER_PERSON
        if idx <= self.MIN_SLOT_PER_PERSON:
            alpha = 100 - idx//4*4
        else:
            alpha = 20 - idx//4*4
        # beta: distance from the occupied
        d = 0
        while d < 16:
            lo, hi = slot - d, slot + d
            if (lo//16 == slot//16 and self.available[person][lo] == 0) or (hi//16 == slot//16 and self.available[person][hi] == 0):
                break
            d += 1
        beta = 2.0 - (0.1*(d//4))
        return alpha*beta

    # Remove 8:30~10:00, 18:00~19:30

    def match(self):

        # First: parse input table, convert to WeekTable objects
        # WeekTable keeps personal score for each slot
        for person in self.names
        weekTable = WeekTable()

        
        # Second: one cell by one, assign a cell

        
        return self.assignments

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
    timeTable = parseInput(inputFile)
    matcher = TableMatcher(timeTable, 10, 13)
    result = matcher.match()
    # personCnt = [0]*12
    # for person, _ in result:
    #     personCnt[person] += 1


    for i in range(5):
        print(result[i*16:(i+1)*16])

if __name__ == "__main__":
    main()