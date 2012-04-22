# -*- coding: utf-8 -*-
import sys
# import math
from random import random as unif  # , choice as choice
# import re
# from collections import defaultdict, Counter
import numpy as np
# import curses
from itertools import groupby

def randrange(max):
    return int(unif() * max)

def randindex(sequence):
    return randrange(len(sequence))

def mean(numbers):
    return float(sum(numbers)) / len(numbers)

def repeat(func, sequence):
    '''Can take a list-like object or an integer'''
    count = sequence if isinstance(sequence, int) else len(sequence)
    return [func() for x in range(count)]

def randproportional_mine(distribution):
    # given a list of floats, pick one with probability proportional
    # to the float relative to the other floats. return an int index.
    cumulative = []
    last = 0
    for event in distribution:
        last += event
        cumulative.append(last)
    # cumulative[-1] should equal the sum (=last), now
    uniform = unif() * last
    for i, threshold in enumerate(cumulative):
        if uniform <= threshold:
            return i

def randproportional(weights):
    '''http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/ -- very clever'''
    threshold = unif() * sum(weights)
    for i, weight in enumerate(weights):
        threshold -= weight
        if threshold <= 0:
            return i

def randproportionalvalue(weights_options):
    # print weights_options
    # try:
    weights, options = zip(*weights_options)
    # except Exception, exc:
        # print weights_options
        # raise
    return options[randproportional(weights)]

def randpenalty(penalties_options):
    # helper function for randproportional:
    #   1) figures out weights from penalties
    #   2) returns item instead of index
    penalties, options = zip(*penalties_options)
    worst = max(penalties)
    weights = [worst - penalty for penalty in penalties]
    return randproportionalvalue(zip(weights, options))

def randsegment(sequence):
    length = randindex(sequence)
    start = randrange(len(sequence) - length)
    return (start, start + length)

def unique(sequence):
    seen = set()
    for item in sequence:
        if item not in seen:
            seen.add(item)
            yield item

res_filename = '/dev/null'
for arg in sys.argv:
    if '.csv' in arg:
        res_filename = arg
fp = open(res_filename, 'w')
def log(line):
    fp.write(line)
    fp.write('\n')
    fp.flush()

class Candidate(object):
    def __init__(self, swaps=None):
        self.swaps = swaps or [Candidate.swap() for i in range(randrange(40) + 10)]

    def sort(self, parasite):
        # sort ascending
        # this means we want all tuples of (x_{n}, x_{n + 1}) pairs so that x_{n} ≤ x_{n + 1}
        test = parasite.copy_values()
        for left, right in self.swaps:
            # if the item referred to by the left side of the swap is greater than the right side, switch them.
            # this ensures that if we cover everything,

            # thus we want swap(a, b) where a < b, but swaps with b < a will throw us off.
            if test[left] > test[right]:
                test[right], test[left] = (test[left], test[right])
        return test

    def mistakes(self, parasite):
        # more positive = fitter individual
        # solution = sorted(original)
        result = self.sort(parasite)
        # misorderings =
        # len(evaluation_swaps) -
        # return misorderings
        return len([a for a, b in evaluation_swaps if result[a] > result[b]])

    def crossover(self, other):
        '''Returns a tuple of the results of the crossover (copies)'''
        # allow crossover to change the whole thing.
        # start_self, end_self = randsegment(self.swaps)
        # start_other, end_other = randsegment(other.swaps)
        length_self = int(min(abs(np.random.normal(0, len(self.swaps) / 10.0)), len(self.swaps)))
        start_self = randrange(len(self.swaps) - length_self)
        end_self = start_self + length_self

        length_other = int(min(abs(np.random.normal(0, len(other.swaps) / 10.0)), len(other.swaps)))
        start_other = randrange(len(other.swaps) - length_other)
        end_other = start_other + length_other

        try:
            self_a, self_b, self_c = self.swaps[:start_self], self.swaps[start_self:end_self], self.swaps[end_self:]
            other_a, other_b, other_c = other.swaps[:start_other], other.swaps[start_other:end_other], other.swaps[end_other:]
        except:
            print start_self, end_self
            print start_other, end_other
            raise

        # new_self = Candidate(list(unique(self_a + other_b + self_c)))
        # new_other = Candidate(list(unique(other_a + self_b + other_c)))
        new_self = Candidate(self_a + other_b + self_c)
        new_other = Candidate(other_a + self_b + other_c)

        return (new_self, new_other)

    def mutate(self, severity=1):
        for i in range(severity):
            index = randindex(self.swaps)
            # tuple_index = int(math.round(unif()))
            # nvm: switch out an entire swapper
            self.swaps[index] = Candidate.swap()

    def clone(self):
        return Candidate([swap for swap in self.swaps])

    # def mutate_into(self, severity=1):
    #     candidate = self.clone()
    #     candidate.mutate(self, severity)
    #     return candidate

    def __str__(self):
        return ' '.join('(%d,%d)' % pair for pair in self.swaps)

    def __repr__(self):
        return '<Candidate %s>' % str(self)

    def __len__(self):
        return len(self.swaps)

    @classmethod
    def swap(cls, length=16):
        return (randrange(length), randrange(length))

class Parasite(object):
    test_values = None

    def __init__(self, initial_values=None, length=16):
        if initial_values != None:
            self.test_values = initial_values
        else:
            self.test_values = [randrange(90) + 10 for x in range(length)]

    # @property
    def copy_values(self):
        return [x for x in self.test_values]

    def mutate(self, severity=1):
        for i in range(severity):
            index = randindex(self.test_values)
            self.test_values[index] = randrange(90) + 10

    def clone(self):
        return Parasite(self.copy_values())

    def __repr__(self):
        return '<Parasite %r>' % self.test_values

class Trial(object):
    def __init__(self, solver, parasite, penalty=None):
        self.solver = solver
        self.parasite = parasite
        # `fitness` returns the number of mistakes made by a candidate
        if penalty != None:
            self.penalty = None
        else:
            self.penalty = solver.mistakes(parasite)  # + (len(solver) / 10)

    def clone(self):
        return Trial(self.solver, self.parasite, self.penalty)

solvers_size = 200
solvers_carryover = 150

parasites_size = 20
# crossover_count = generation_size - carryover_count
# best_count = 50

# iterations = 50
iterations = 50000
# p_mutation = 0.01

# (x, y) swaps are good iff x < y
monotonic = [(x, y) for x in range(16) for y in range(x + 1, 16)]
adjacencies = zip(range(15), range(1, 16))
evaluation_swaps = monotonic
# print evaluation_swaps, '=>', len(evaluation_swaps)
# perfect_swaps = zip(range(0, 15), range(1, 16))*16
# perfect = Candidate(monotonic)

solver_key = lambda trial: trial.solver
parasite_key = lambda trial: trial.parasite
penalty_key = lambda trial: trial.penalty
first_key = lambda x: x[0]

def run(stdscr, debug):
    solvers = repeat(Candidate, solvers_size)
    parasites = repeat(Parasite, parasites_size)

    for iteration in range(iterations):
        trials = [Trial(solver, parasite) for parasite in parasites for solver in solvers]

        by_solver = []
        for solver, solver_trials in groupby(sorted(trials, key=solver_key), solver_key):
            solver_trials = list(solver_trials)
            total_penalty = sum(map(penalty_key, solver_trials))
            by_solver.append((total_penalty, solver))
            if total_penalty == 0:
                print
                print 'Perfect solver: %r' % solver
                print '  len: %d' % len(solver)
                for trial in solver_trials:
                    print trial.parasite
                    print solver.sort(trial.parasite)
                raise Exception("DONE!")
        # we prefer lower penalties
        #randpenalty(best_solvers)

        by_parasite = []
        for parasite, parasite_trials in groupby(sorted(trials, key=parasite_key), parasite_key):
            total_penalty = sum(map(penalty_key, parasite_trials))
            by_parasite.append((total_penalty, parasite))
        # we prefer higher penalties
        #randproportionalvalue(easiest_parasites)

        best_solvers = sorted(by_solver, key=first_key)

        if debug and iteration % 10 == 0:
            best_score, best_candidate = best_solvers[0]
            worst_score, worst_candidate = best_solvers[-1]
            print '#%5d, mean: %7.2f' % (iteration, mean([score for score, solver in best_solvers]))
            print '       worst: %3d   (%3d)' % (worst_score, len(worst_candidate.swaps))
            print '        best: %3d   (%3d)' % (best_score, len(best_candidate.swaps))
            print '              %r' % sorted(best_candidate.swaps)

            easiest_parasites = sorted(by_parasite, key=first_key)
            hardest_parasite_penalty, hardest_parasite = easiest_parasites[-1]
            print ' hardest_parasite: %r' % hardest_parasite.test_values
            print '            score: %d' % hardest_parasite_penalty
            print "   best's attempt: %r" % best_candidate.sort(hardest_parasite)

            # print ' eval seq  %r' % eval_pool_choice
            # print ' best sort %r' % best_candidate.sort(eval_pool_choice)
            # print ' perfect.fitness: %s' % perfect.fitness(eval_pool_choice)
            # print ' perfect sort %r' % perfect.sort(eval_pool_choice)

        next_solvers = []
        # for m in range(best_count)
        reproductions = (solvers_size - solvers_carryover) / 2
        for n in range(reproductions):
            a = randpenalty(by_solver)
            b = randpenalty(by_solver)
            next_solvers += a.crossover(b)

        # these are copied, they are not the originals
        next_solvers += [randpenalty(by_solver).clone() for c in range(solvers_carryover)]

        for solver in next_solvers:
            if unif() < 0.1:
                solver.mutate()

        next_solvers[0] = best_solvers[0][1]

        solvers = next_solvers

        next_parasites = [randproportionalvalue(by_parasite).clone() for p in range(parasites_size)]
        for parasite in next_parasites:
            parasite.mutate()

        parasites = next_parasites
        # for candidate in next_generation:
        #     if unif() < 0.1:
        #         candidate.swaps.insert(randrange(len(candidate.swaps)), Candidate.swap())
        #     if unif() < 0.1:
        #         candidate.swaps.pop(randrange(len(candidate.swaps)))


if __name__ == '__main__':
    debug = 'debug' in sys.argv
    # curses.wrapper(run, debug)
    run(None, debug)
