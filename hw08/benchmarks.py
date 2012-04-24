import sys
import math
import random
import numpy as np
import ga
from ga import unif
from time import time

iterations = [int(arg) for arg in sys.argv if arg.isdigit()][0]

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

def random_random():
    for i in xrange(iterations):
        r = random.random()
def np_random_random():
    for i in xrange(iterations):
        r = np.random.random()
def random_uniform():
    for i in xrange(iterations):
        r = random.uniform(0, 100)
def np_random_uniform():
    for i in xrange(iterations):
        r = np.random.uniform(0, 100)
def random_randrange():
    for i in xrange(iterations):
        r = random.randrange(100)
def ga_randrange():
    for i in xrange(iterations):
        r = ga.randrange(100)
def lcg():
    r = 1
    r = np.array([r], np.uint32)[0]
    for i in xrange(iterations):
        # I don't even know.
        r = r * 1664525 + 1013904223
def sysrand_random():
    sysrand = random.SystemRandom()
    for i in xrange(iterations):
        r = sysrand.random()
def np_random_random_vector():
    rs = np.random.random(iterations)
    for i in xrange(iterations):
        r = rs.pop()
def random_gauss():
    # takes about 8 times longer than random.random
    for i in xrange(iterations):
        r = random.gauss(0, 1)
def local_gauss():
    for i in xrange(iterations):
        r = gauss(0, 1)
def local_gauss2():
    for i in xrange(iterations):
        r = gauss2(0, 1)
def np_random_normal():
    # about 3 times as fast as home-made gauss, 4 times faster than python lib gauss
    for i in xrange(iterations):
        r = np.random.normal(0, 1)
def list_append():
    l = []
    for i in xrange(iterations):
        l.append(i)
def list_plusequals():
    # about 0.5 times slower than list append
    l = []
    for i in xrange(iterations):
        l += [i]


func = [v for k, v in locals().items() if k in sys.argv][0]

started = time()

res = func()

ended = time()

elapsed = ended - started

print 'Took %10.9f seconds for %d iterations' % (elapsed, iterations)
print '  %10.9f seconds / per iteration' % (elapsed / iterations)
