import sys
import math
import random
import re
from collections import defaultdict
from copy import copy
import time as timemodule
import curses

res_filename = '/dev/null'
for arg in sys.argv:
    if '.csv' in arg:
        res_filename = arg
fp = open(res_filename, 'w')
def errlog(line):
    fp.write(line)
    fp.write('\n')
    fp.flush()

class Matrix(object):
    length = 0
    width = 0
    store = None  # dictionary of (int, int) -> char

    def __init__(self, length, width, value=None):
        self.store = dict()
        self.length = length
        self.width = width
        for x in range(length):
            for y in range(width):
                self.store[(x, y)] = value

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, val):
        self.store[key] = val

    def hscan(self):
        for row_index in range(self.width):
            yield ''.join(self.store[(col_index, row_index)] for col_index in range(self.length))

    def __add__(self, other):
        res = copy(self)
        res.store = dict((key, self[key] + other[key]) for key in self.store.keys())
        return res

def distance(a, b):
    return math.sqrt((float(a[0]) - b[0])**2 + (float(a[1]) - b[1])**2)

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

class StateSpace(object):
    complete = False
    agent_1 = (0, 0)
    agent_2 = (0, 0)

    def __init__(self, width, length, obstacle_count):
        self.width = width
        self.length = length
        self.obstacle_count = obstacle_count
        self.status = SidewalkWindow(width, length + 1, 0, 2)

    def reset(self):
        self.obstacles = set((random.randrange(self.length), random.randrange(self.width)) for i in range(self.obstacle_count))
        self.agent = (0, random.randrange(self.width))
        self.complete = False

    def lines(self):
        chars = Matrix(self.length + 1, self.width, ' ')

        for obstacle in self.obstacles:
            chars[obstacle] = 'O'

        chars[self.agent_2] = '.'
        chars[self.agent_1] = 'a'
        chars[self.agent] = 'X' if self.agent in self.obstacles else 'A'

        for row in range(self.width):
            chars[(self.length, row)] = '$'

        return list(chars.hscan())

    def move(self, action):
        score = 0
        x, y = add(self.agent, action)
        if x < 0:
            x = 0
            score -= 1
        elif x >= self.length:
            x = self.length - 1
            score -= 1
            self.complete = True

        if y < 0:
            y = 0
            score -= 1
        elif y >= self.width:
            y = self.width - 1
            score -= 1

        self.agent_2 = self.agent_1
        self.agent_1 = self.agent
        self.agent = (x, y)
        return score

    def current_reward(self, module_name):
        if module_name == 'Finish':
            if self.complete:
                return self.length - 1
            return 0
        elif module_name == 'Obstacle':
            if self.agent in self.obstacles:
                return -1
            return 0

    def current_state(self, module_name):
        if module_name == 'Finish':
            return 1
        elif module_name == 'Obstacle':
            flags = []
            for key, direction in directions.items():
                if any(add(self.agent, action) in self.obstacles for action in direction):
                    flags.append(key)

            return '+'.join(flags)

class StatusWindow(object):
    win = None
    pattern = '%22s' + '%10s '*4

    def __init__(self, height, length, y, x):
        self.height = height + 2
        self.length = length + 2
        self.y = y
        self.x = x

    def initialize(self):
        self.win = curses.newwin(self.height, self.length, self.y, self.x)

    def draw(self, q):
        if not self.win:
            self.initialize()
        # states = set([s for s, a in q.store.keys()])
        states = sorted(list(q.states)[:13])
        self.win.addstr(1, 1, self.pattern % (' # states = %d     ' % len(states), 'up', 'down', 'left', 'right'))
        for i, s in enumerate(states):
            args = [str(s)] + ['%6.4f' % q.scores[(s, a)] for a in actions]
            line = self.pattern % tuple(args)
            self.win.addstr(i + 2, 1, line)

        self.win.refresh()

    def clear(self):
        if not self.win:
            self.initialize()
        self.win.erase()  # erase is way smoother than clear()
        self.win.border()


class SidewalkWindow(object):
    win = None

    def __init__(self, width, length, y, x):
        self.width = width + 2
        self.length = length + 2
        self.y = y
        self.x = x

    def initialize(self):
        # height, width, begin_y, begin_x
        self.win = curses.newwin(self.width, self.length, self.y, self.x)
        self.clear()

    def draw(self, sidewalk, label):
        if not self.win:
            self.initialize()
        self.win.addstr(0, 4, label)

        for i, line in enumerate(sidewalk.lines()):
            if 'X' in line:
                line = '-'*len(line)
            self.win.addstr(i + 1, 1, line)
        self.win.refresh()

    def clear(self):
        if not self.win:
            self.initialize()
        self.win.erase()  # erase is way smoother than clear()
        self.win.border()

def match_into(pattern, search, default):
    m = re.search(pattern, search)
    if m:
        result = []
        for group in m.groups():
            if group.isdigit():
                result.append(int(group))
            elif '.' in group:
                result.append(float(group))
            else:
                result.append(group)
        if len(result) == 1:
            return result[0]
        return result
    return default

argstring = ' '.join(sys.argv)
sidewalk_length, sidewalk_width = match_into(r's(\d+)x(\d+)', argstring, (40, 7))
sidewalk_obstacles = match_into(r'o(\d+)', argstring, 10)
# how quickly do we learn in general?
alpha = match_into(r'a([\d.]+)', argstring, 0.01)
# how much do we believe what our next action can get us?
discount = match_into(r'g([\d.]+)', argstring, 0.8)
# how often do we venture away from what we know works?
epsilon = match_into(r'e([\d.]+)', argstring, 0.9)


actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up down left right
# two_away = list(set([add(a, b) for a in actions for b in actions]))
east = [(2, -2), (1, -1), (2, -1), (1, 0), (2, 0), (3, 0), (1, 1), (2, 1), (2, 2)]
directions = dict(east=east, west=[(-x, y) for x, y in east],
    south=[(y, x) for x, y in east], north=[(y, -x) for x, y in east])

class Module(object):
    status = None

    def __init__(self, module_name, weight):
        self.name = module_name
        self.scores = defaultdict(lambda: 1)
        self.weight = weight

    def scores_actions(self, state):
        return [(self.scores[(state, a)], a) for a in actions]

    def get_top_score_action(self, state):
        scores_actions = self.scores_actions(state)
        random.shuffle(scores_actions)
        sorted_scores_actions = sorted(scores_actions, key=lambda sa: sa[0], reverse=True)
        if (sorted_scores_actions[0][0] - sorted_scores_actions[1][0]) < 0.001:
            return random.choice(scores_actions)
        return sorted_scores_actions[0]

    def get_random_score_action(self, state):
        return random.choice(self.scores_actions(state))

    @property
    def states(self):
        return set([state for state, action in self.scores.keys()])


def episode(qs, sidewalk, max_iterations, draw=False, run=0):
    sidewalk.reset()
    sidewalk.status.clear()
    if draw:
        for q in qs:
            q.status.clear()

    total_reward = 0
    total_obstacles = 0
    for time in xrange(max_iterations):
        scores_actions = []
        state = None
        for q in qs:
            state = sidewalk.current_state(q.name)
            if random.random() < epsilon:
                score, action = q.get_top_score_action(state)
            else:
                score, action = q.get_random_score_action(state)
            scores_actions.append((score*q.weight, score, action))
        random.shuffle(scores_actions)

        weighted_score, score, action = sorted(scores_actions, key=lambda sa: sa[0], reverse=True)[0]

        # now we have the chosen action, and q's record of the score for taking that action in this state

        sidewalk.move(action)
        state_reward = sum(sidewalk.current_reward(q.name) for q in qs)
        total_reward += state_reward
        if sidewalk.agent in sidewalk.obstacles:
            # timemodule.sleep(1)
            total_obstacles += 1

        if draw:
            sidewalk.status.draw(sidewalk, ' & '.join(q.name for q in qs))
            for q in qs:
                q.status.draw(q)

        if len(qs) == 1:
            next_state = sidewalk.current_state(qs[0].name)
            best_score = max(q.scores[(next_state, a)] for a in actions)
            qs[0].scores[(state, action)] = score + alpha * (state_reward + (discount * best_score) - score)

        if sidewalk.complete and 'Finish' in [q.name for q in qs]:
            break

    name = ' + '.join(q.name for q in qs)
    return name, total_reward, total_obstacles, time

def run(stdscr, draw):
    # 2 modules, a) finish, b) avoid obstacles
    sidewalk = StateSpace(sidewalk_width, sidewalk_length, sidewalk_obstacles)
    q_fin = Module('Finish', 1)
    q_fin.status = StatusWindow(2, 90, sidewalk_width + 3, 2)  # y, x
    q_obs = Module('Obstacle', 2)
    q_obs.status = StatusWindow(15, 90, sidewalk_width + 7, 2)  # y, x

    basic = curses.newwin(3, 16 + len(res_filename), 0, sidewalk_length + 12)
    basic.border()

    # errlog('\t'.join([q_fin.name, q_obs.name, 'combined']))
    errlog('epoch,module,reward,obstacles,time')
    for run in range(1000):
        basic.addstr(1, 2, '%s: %7d ' % (res_filename, run))
        basic.refresh()
        # if run == 0:
        #     global epsilon
        #     epsilon = 1
        # q_results = [

        results = [
            episode([q_fin], sidewalk, 1000000, draw),
            episode([q_obs], sidewalk, 1000, draw, run=run),
            episode([q_fin, q_obs], sidewalk, 10000, draw)]
        for module, score, obstacles, time in results:
            errlog('%d,%s,%.8f,%d,%d' % (run, module, score, obstacles, time))



if __name__ == '__main__':
    curses.wrapper(run, 'draw' in sys.argv)

# s20x5-o20-e0.9-a0.01-g0.8-out.csv
