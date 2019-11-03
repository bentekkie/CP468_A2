#!/usr/bin/python3.8
# %%
from typing import List, Set, Dict, Tuple, TypeVar, Generic, Callable, Any
from queue import Queue
from copy import deepcopy
from collections import namedtuple
import argparse

P = namedtuple('Point', ['x', 'y'])

T = TypeVar('T')
S = TypeVar('S')

#Workaround for typing
class FunctionProperty(Generic[T]):
    def __get__(self, oself: Any, owner: Any) -> T:
        ...

    def __set__(self, oself: Any, value: T) -> None:
        ...


class CSP(Generic[T, S]):
    domains: Dict[T, Set[S]]
    adj_list: Dict[T, Set[T]]
    constraint: FunctionProperty[Callable[[S, S], bool]]

    def __init__(
            self,
            domains: Dict[T, Set[S]],
            related: Callable[[T, T], bool],
            constraint: Callable[[S, S], bool]):
        self.domains = domains
        self.adj_list = {
            x: {y for y in domains if x is not y and related(x, y)}
            for x in domains}
        self.constraint = constraint

    def revise(self, x_var: T, y_var: T) -> bool:
        new_domain = {vx for vx in self.domains[x_var] if any(
            True for vy in self.domains[y_var] if self.constraint(vx, vy))}
        change = self.domains[x_var] != new_domain
        self.domains[x_var] = new_domain
        return change

    def solved(self) -> bool:
        return all(len(values) == 1 for values in self.domains.values())

    def ac3(self) -> Tuple[bool, List[int]]:
        q: Queue[Tuple[T,T]] = Queue()
        counts: List[int] = []
        for x in self.adj_list:
            for y in self.adj_list[x]:
                q.put((x, y))
        while not q.empty():
            counts.append(q.qsize())
            i, j = q.get()
            if self.revise(i, j):
                if len(self.domains[i]) == 0:
                    return False, counts
                for k in self.adj_list[i] - {j}:
                    q.put((k, i))
        return True, counts

    def backtrack(self) -> bool:
        # Ensure that the csp is arc consistent before backtracking begins
        if not self.ac3()[0]:
            return False
        if self.solved():  # Short circuit if the puzzle is already solved
            return True
        # most remaining values heuristic
        mrv_var = min(
            ((k, len(v)) for k, v in self.domains.items() if len(v) > 1),
            key=lambda k: k[1])[0]
        # least constraining value heuristic
        for value in sorted(
                self.domains[mrv_var],
                key=lambda x: sum(
                    1 for n in self.adj_list[mrv_var] if x in self.domains[n])):
            new_csp = deepcopy(self)
            new_csp.domains[mrv_var] = {value}  # Assign the value to the variable
            # Check if this is consistent using the backtracking alogorithm
            if new_csp.backtrack():
                self.domains = new_csp.domains  # If it is we are done
                return True
        return False


def solve_sudoku(data: List[List[int]]) -> Tuple[CSP,List[int],bool]:
    # Generate domains for each square given the input data
    domains: Dict[P, Set[int]] = {
        P(i, j): {data[j][i]} if data[j][i] != 0 else set(range(1, 10))
        for i in range(9) for j in range(9)}

    # Initialize csp
    csp = CSP(
        domains,
        lambda v1, v2:  (
            v1.x == v2.x or
            v1.y == v2.y or
            (v1.x // 3 == v2.x // 3 and v1.y // 3 == v2.y // 3)),
        lambda vx, vy: vx != vy)

    # Run the ac3 algorithm
    valid, counts = csp.ac3()

    valid = valid and csp.backtrack()

    return csp, counts, valid

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Solve a sudoku puzzle')
    parser.add_argument("sudokufile", type=argparse.FileType('r'))
    parser.add_argument("outputfile", type=argparse.FileType('w'))
    parser.add_argument("-c", "--counts", action='store_true',
                        help="Print queue size counts for ac3 to stdout")
    args = parser.parse_args()

    # Read in input file
    with args.sudokufile as f:
        input_data = [
            [int(x) for x in line.strip().split(' ')] for line in f.readlines()]

    csp, counts, valid = solve_sudoku(input_data)
    
    with args.outputfile as f:
        if args.counts and counts and len(counts):
            print(','.join(str(c) for c in counts))
        if valid:
            # If backtracking succeeds then
            # print the solution to the output file
            print(
                '\n'.join(
                    ' '.join(
                        str(csp.domains[P(x, y)].pop()) for x in range(9))
                    for y in range(9)),
                file=f)
        else:
            print("Impossible", file=f)
