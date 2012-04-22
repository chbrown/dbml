import sys
import math
import random
import numpy as np
from time import time

iterations = [int(arg) for arg in sys.argv if arg.isdigit()][0]

from ga import randrange, unif

started = time()

def gauss(mu, sigma):
    while True:
        x1 = 2.0 * unif() - 1.0
        x2 = 2.0 * unif() - 1.0
        w = x1 * x1 + x2 * x2
        if w < 1.0:
            w = math.sqrt((-2.0 * math.log(w)) / w)
            return x1 * w
            # y2 = x2 * w;

def gauss2(mu, sigma):
    x1 = unif()
    x2 = unif()
    return math.sqrt(-2.0 * math.log(x1)) * math.cos(2 * math.pi * x2)
    # y2 = sqrt( - 2 ln(x1) ) sin( 2 pi x2 )

if 'random.random' in sys.argv:
    print 'random.random'
    for i in xrange(iterations):
        r = random.random()
if 'np.random.random' in sys.argv:
    print 'np.random.random'
    for i in xrange(iterations):
        r = np.random.random()
if 'random.uniform' in sys.argv:
    print 'random.uniform'
    for i in xrange(iterations):
        r = random.uniform(0, 100)
if 'np.random.uniform' in sys.argv:
    print 'np.random.uniform'
    for i in xrange(iterations):
        r = np.random.uniform(0, 100)
if 'random.randrange' in sys.argv:
    print 'random.randrange'
    for i in xrange(iterations):
        r = random.randrange(100)
if 'randrange' in sys.argv:
    print 'randrange'
    for i in xrange(iterations):
        r = randrange(100)
if 'lcg' in sys.argv:
    print 'lcg'
    r = 1
    r = np.array([r], np.uint32)[0]
    for i in xrange(iterations):
        # I don't even know.
        r = r * 1664525 + 1013904223
if 'sysrand.random' in sys.argv:
    print 'sysrand.random'
    sysrand = random.SystemRandom()
    for i in xrange(iterations):
        r = sysrand.random()
if 'np.random.random.vector' in sys.argv:
    print 'np.random.random.vector'
    rs = np.random.random(iterations)
    for i in xrange(iterations):
        r = rs.pop()
if 'random.gauss' in sys.argv:
    # takes about 8 times longer than random.random
    print 'random.gauss'
    for i in xrange(iterations):
        r = random.gauss(0, 1)
if 'gauss' in sys.argv:
    print 'gauss'
    for i in xrange(iterations):
        r = gauss(0, 1)
if 'gauss2' in sys.argv:
    print 'gauss2'
    for i in xrange(iterations):
        r = gauss2(0, 1)
if 'np.random.normal' in sys.argv:
    # about 3 times as fast as home-made gauss, 4 times faster than python lib gauss
    print 'np.random.normal'
    for i in xrange(iterations):
        r = np.random.normal(0, 1)

ended = time()

elapsed = ended - started

print 'Took %10.9f seconds for %d iterations' % (elapsed, iterations)
print '  %10.9f seconds / per iteration' % (elapsed / iterations)
