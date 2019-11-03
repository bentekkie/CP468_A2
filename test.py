#!/usr/bin/python3.8
from solve import solve_sudoku, P, CSP
from typing import List, Dict, Set, Tuple
from multiprocessing import Pool, Queue, Manager
from multiprocessing.pool import ThreadPool
import sys




def parse_puzzle(data: str) -> List[List[int]]:
    puzzle : List[List[int]] = [[int(v) for v in data[9*x:9*(x+1)]] for x  in  range(9)]
    return puzzle

def parse_line(line: str) -> Tuple[List[List[int]],List[List[int]]]:
    parts = line.split(',')
    puzzle = parse_puzzle(parts[0])
    solution = parse_puzzle(parts[1])
    return puzzle,solution

def worker(in_data :Tuple[int,Tuple[List[List[int]],List[List[int]]]]):
    i, in_data_stuff = in_data
    puzzle, solution = in_data_stuff
    csp, _, _ = solve_sudoku(puzzle)
    if all(csp.domains[P(y,x)].pop()==solution[x][y] for x in range(9) for y in range(9)):
        #print(f"{i} Correct")
        return True
    else:
        #print(f"{i} Incorrect")
        return False
    sys.stdout.flush()

with open('./sudoku.csv','r') as dataFile:
    m = Manager()
    n = 200
    with Pool(n) as p:
        r = True
        for i, res in enumerate(p.imap_unordered(worker,((i,parse_line(line)) for i,line in enumerate(dataFile)), chunksize=1), 1):
            r = r and res
            print(f"{i} {res}")
        print(r)
        limit = 1000
        p.close()
        p.join()