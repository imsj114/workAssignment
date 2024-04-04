import sys
from collections import defaultdict
import numpy as np
from scipy.optimize import linear_sum_assignment

def parseInput(inputFile):
    timeTable = {}
    with open(inputFile, "r") as openFile:
        for line in openFile:
            name, available = line.split()
            timeTable[name] = list(map(int, available))
    return timeTable

class TableMatcher():
    def __init__(self, timeTable, MIN_SLOT_PER_PERSON, MAX_SLOT_PER_PERSON):
        self.names, self.available = zip(*timeTable.items())
        self.MIN_SLOT_PER_PERSON = MIN_SLOT_PER_PERSON
        self.MAX_SLOT_PER_PERSON = MAX_SLOT_PER_PERSON
        self.numPeople = len(self.names)
        self.numSlot = len(self.available[0])
        self.assignments = [None]*self.numSlot
    
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

    # First round: assign just one person per slot
    def build_cost_matrix(self):
        # worker (person, idx), slot
        cost_matrix = np.zeros((self.numPeople*self.MAX_SLOT_PER_PERSON, self.numSlot))

        for person in range(self.numPeople):
            for idx in range(self.MAX_SLOT_PER_PERSON):
                for slot in range(self.numSlot):
                    cost_matrix[person*self.MAX_SLOT_PER_PERSON + idx][slot] = self.weight(person, slot, idx)*self.available[person][slot]
        return cost_matrix

    # Second round: assign second person if possible
    # def build_cost_matrix_2(self, occupied, slots_left):
    #     cost_matrix = np.zeros((self.numPeople*self.MAX_SLOT_PER_PERSON, self.numSlot))

    #     for person in range(self.numPeople):
    #         for idx in range(self.MAX_SLOT_PER_PERSON):
    #             for slot in range(self.numSlot):
    #                 cost_matrix[person*self.MAX_SLOT_PER_PERSON + idx][slot] = self.weight(slot, idx)*self.assignments[person][slot]
    #     return cost_matrix

    def match(self):
        cost_matrix = self.build_cost_matrix()
        row_ind, col_ind = linear_sum_assignment(cost_matrix, maximize=True)
        
        # First round
        self.assignments = [-1]*self.numSlot
        for i in range(len(row_ind)):
            person = row_ind[i] // self.MAX_SLOT_PER_PERSON
            idx = row_ind[i] % self.MAX_SLOT_PER_PERSON
            slot = col_ind[i]
            if self.available[person][slot] == 1:
                self.assignments[slot] = (person, idx)
        
        # Second round
        
        return self.assignments

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