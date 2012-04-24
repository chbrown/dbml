from random import random as unif

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
    weights, options = zip(*weights_options)
    return options[randproportional(weights)]

def randpenalty(penalties_options):
    # helper function for randproportional:
    #   1) figures out weights from penalties
    #   2) returns item instead of index
    penalties, options = zip(*penalties_options)
    worst = max(penalties)
    weights = [(worst * 2) - penalty for penalty in penalties]
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
