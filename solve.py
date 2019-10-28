#!/usr/bin/python3
#%%
from typing import List, Set, Tuple, Dict, TypeVar, Generic
from queue import Queue
from copy import deepcopy
import argparse

T = TypeVar('T')
S = TypeVar('S')
class CSP(Generic[T, S]):
    def __init__(self, domains : Dict[T,Set[S]], adjList : Dict[T,Set[T]]):
        self.domains : Dict[T,Set[S]] = domains
        self.adjList : Dict[T,Set[T]] = adjList

    def revise (self, x : T, y : T) -> bool:
        new_domain = {vx for vx in self.domains[x] if any(True for vy in self.domains[y] if vy != vx)}
        change = self.domains[x] != new_domain
        self.domains[x] = new_domain
        return change
    
    def solved(self) -> bool:
        return all(len(key)==1 for key in self.domains.values())

    def ac3(self) -> bool:
        q : "Queue[Tuple[T,T]]" = Queue()
        for x in self.adjList:
            for y in self.adjList[x]:
                    q.put((x,y))
        while not q.empty():
            print(q.qsize())
            i, j = q.get()
            if self.revise(i,j):
                if len(self.domains[i]) == 0:
                    return False
                for k in self.adjList[i] - {j}:
                    q.put((k,i))
        return True

    def unAssignedVars(self):
        return {key:val for key,val in self.domains.items() if len(val)>1}

    def backtrack(self):
        if not self.ac3():
            return False
        if self.solved():
            return True
        d = [x for x in filter(lambda k: len(k[1]) >1,self.domains.items())]
        print(d)
        k = min(d,key=lambda k: len(k[1]))
        print(k)
        var = k[0]
        for value in self.domains[var]:
            newCsp = deepcopy(self)
            newCsp.domains[var] = {value}
            if newCsp.backtrack():
                self.domains = newCsp.domains
                return True


def related(v1 : Tuple[int,int], v2 : Tuple[int,int]) -> bool:
    return v1[0] == v2[0] or v1[1] == v2[1] or (v1[0] // 3 == v2[0] // 3 and v1[1] // 3 == v2[1] // 3)


parser = argparse.ArgumentParser(description='Solve a sudoku puzzle')

parser.add_argument("sudokufile",type=argparse.FileType('r'))

args = parser.parse_args()
with args.sudokufile as f:
    data = [[int(x) for x in line.strip().split(' ')] for line in f.readlines()]
domains = {(i,j):{data[j][i]} if data[j][i] != 0 else set(range(1,10)) for i in range(9) for j in range(9)}
adjList = {x:{y for y in domains if x is not y and related(x,y)} for x in domains}
csp = CSP(domains,adjList)
print(csp.ac3())
print(csp.solved())
for x in range(9):
    print(" ".join(str(next(iter(csp.domains[(y,x)]))) for y in range(9)))
print(csp.backtrack())
print(csp.solved())
for x in range(9):
    print(" ".join(str(next(iter(csp.domains[(y,x)]))) for y in range(9)))
