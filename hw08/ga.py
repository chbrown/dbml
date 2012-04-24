# -*- coding: utf-8 -*-
import os
import sys
from random import random as unif
import numpy as np
from itertools import groupby
from lib import mean, repeat, randrange, randindex, randpenalty, randproportionalvalue

class Output(object):
    fp = None

    def __init__(self, filename=None):
        # filename = '/dev/null'
        for arg in sys.argv:
            if '.csv' in arg:
                filename = arg
        if not filename:
            for prefix in 'abcdefghijklmnopqrstuvwxyz':
                filename = 'results/output-%s.csv' % prefix
                if not os.path.exists(filename):
                    break
        self.filename = filename

    def write(self, line):
        if self.fp == None:
            self.fp = open(self.filename, 'w')
        self.fp.write(line)
        self.fp.write('\n')
        self.fp.flush()

    def csv(self, *cells):
        self.write(','.join(map(str, cells)))


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
        attempt = self.sort(parasite)
        return len([a for a, b in evaluation_swaps if attempt[a] > attempt[b]])

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
    def __init__(self, solver, parasite, mistakes=None):
        self.solver = solver
        self.parasite = parasite
        # `fitness` returns the number of mistakes made by a candidate
        self.mistakes = mistakes or solver.mistakes(parasite)

    def clone(self):
        return Trial(self.solver, self.parasite, self.mistakes)

solvers_size = 200
solvers_carryover = 100

parasites_size = 20

iterations = 50000

# (x, y) swaps are good iff x < y
monotonic = [(x, y) for x in range(16) for y in range(x + 1, 16)]
adjacencies = zip(range(15), range(1, 16))
evaluation_swaps = monotonic
# print evaluation_swaps, '=>', len(evaluation_swaps)
# perfect_swaps = zip(range(0, 15), range(1, 16))*16
# perfect = Candidate(monotonic)

solver_key = lambda trial: trial.solver
parasite_key = lambda trial: trial.parasite
mistakes_key = lambda trial: trial.mistakes
penalty_key = lambda trial: trial.mistakes + (len(trial.solver) / 50.0)
first_key = lambda x: x[0]

output = Output()
output.csv('iteration', 'best_fitness', 'best_length', 'worst_fitness', 'worst_length')

def run(stdscr, debug):
    solvers = repeat(Candidate, solvers_size)
    parasites = repeat(Parasite, parasites_size)

    for iteration in range(iterations):
        trials = [Trial(solver, parasite) for parasite in parasites for solver in solvers]

        by_solver_mistakes = []
        by_solver = []
        for solver, solver_trials in groupby(sorted(trials, key=solver_key), solver_key):
            solver_trials = list(solver_trials)
            total_mistakes = sum(map(mistakes_key, solver_trials))
            total_penalty = sum(map(penalty_key, solver_trials))
            by_solver_mistakes.append((total_mistakes, solver))
            by_solver.append((total_penalty, solver))
            if total_mistakes == 0:
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
            total_mistakes = sum(map(mistakes_key, parasite_trials))
            by_parasite.append((total_mistakes, parasite))
        # we prefer higher penalties
        #randproportionalvalue(easiest_parasites)

        best_solvers = sorted(by_solver, key=first_key)
        best_score, best_candidate = best_solvers[0]
        worst_score, worst_candidate = best_solvers[-1]

        if debug and iteration % 10 == 0:
            best_solvers_by_mistakes = sorted(by_solver_mistakes, key=first_key)
            best_mistakes, best_candidate_by_mistakes = best_solvers_by_mistakes[0]
            # worst_score, worst_candidate = best_solvers[-1]
            print '#%5d, mean: %7.2f' % (iteration, mean([score for score, solver in best_solvers]))
            # print '       worst: %3d   (%3d)' % (worst_score, len(worst_candidate.swaps))
            print '        best: %3d - %3.1f (%3d)' % (best_mistakes, best_score, len(best_candidate_by_mistakes))
            # print '              %r' % best_candidate.swaps

            easiest_parasites = sorted(by_parasite, key=first_key)
            hardest_parasite_mistakes, hardest_parasite = easiest_parasites[-1]
            # print ' hardest_parasite: %r' % hardest_parasite.test_values
            # print '            score: %d' % hardest_parasite_mistakes
            # print "   best's attempt: %r" % best_candidate.sort(hardest_parasite)

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

        output.csv(iteration, best_score, len(best_candidate), worst_score, len(worst_candidate))
        # for candidate in next_generation:
        #     if unif() < 0.1:
        #         candidate.swaps.insert(randrange(len(candidate.swaps)), Candidate.swap())
        #     if unif() < 0.1:
        #         candidate.swaps.pop(randrange(len(candidate.swaps)))


if __name__ == '__main__':
    debug = 'debug' in sys.argv
    run(None, debug)
