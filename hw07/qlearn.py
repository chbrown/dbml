import math
import random
from collections import defaultdict
from copy import copy
import curses

fp = open('qlearn.tsv', 'w')
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
    agent = None
    width = 1
    length = 2
    obstacles = None

    def __init__(self, width=5, length=25, obstacles=10):
        self.agent = (0, random.randrange(width))
        self.width = width
        self.length = length

        self.obstacles = set((random.randrange(length), random.randrange(width)) for i in range(obstacles))

    def lines(self):
        # chars is an list of lists of chars, each strings is a line, a horizontal strip of the sidewalk
        chars = Matrix(self.length, self.width, ' ')

        for obstacle in self.obstacles:
            chars[obstacle] = 'O'

        if chars.store.get(self.agent) == 'O':
            chars[self.agent] = 'X'
        else:
            chars[self.agent] = 'A'

        return list(chars.hscan())

    def move(self, action):
        score = 0
        x, y = add(self.agent, action)
        if x < 0:
            x = 0
            score -= 1
        elif x >= self.length:
            # hang out in the end-zone
            x = self.length
            score -= 1

        if y < 0:
            y = 0
            score -= 1
        elif y >= self.width:
            y = self.width - 1
            score -= 1

        self.agent = (x, y)
        return score

    @property
    def complete(self):
        return self.agent[0] >= self.length

    def current_reward(self, module_name):
        if module_name == 'finish':
            if self.complete:
                return 100
            return 0
        elif module_name == 'obstacle':
            if self.agent in self.obstacles:
                return -20
            return 1

    def current_state(self, module_name):
        if module_name == 'finish':
            return 1

            # distance_to_finish_line = self.length - self.agent.x
            # if distance_to_finish_line < 1:
                # return 0
            # return int(math.log(distance_to_finish_line) * 2.0)
        elif module_name == 'obstacle':
            # if self.agent.dist(obstacle) > 2:
                # return 0

            directions = [2**i for i, action in enumerate(actions) if add(self.agent, action) in self.obstacles]

            return sum(directions)


            # flags = 0
            # if obstacle.x < self.agent.x:
            #     flags += 1
            # elif obstacle.x == self.agent.x:
            #     flags += 2
            # else:
            #     flags += 4

            # if obstacle.y < self.agent.y:
            #     flags += 8
            # elif obstacle.y == self.agent.y:
            #     flags += 16
            # else:
            #     flags += 32

            # return flags


class StatusWindow(object):
    win = None
    pattern = '%5s' + '%10s '*4

    def __init__(self, y, x):
        self.win = curses.newwin(15, 80, y, x)

    def draw(self, q):
        # states = set([s for s, a in q.store.keys()])
        states = list(q.states)[:12]
        for i, s in enumerate(states):
            args = [str(s)] + ['%6.4f' % q.scores[(s, a)] for a in actions]
            line = self.pattern % tuple(args)
            self.win.addstr(i + 2, 1, line[:64])

        # self.win.addstr(9, 1, '%10.5f - %10s - %d' % (score, action, state))

        self.win.refresh()

    def clear(self):
        self.win.erase()  # erase is way smoother than clear()
        self.win.addstr(1, 1, self.pattern % ('', 'up', 'down', 'left', 'right'))
        self.win.border()


class SidewalkWindow(object):
    win = None

    def __init__(self, width, length, y, x):
        # height, width, begin_y, begin_x
        self.win = curses.newwin(width + 2, length + 2, y, x)
        self.clear()

    def draw(self, sidewalk):
        for i, line in enumerate(sidewalk.lines()):
            self.win.addstr(i + 1, 1, line)
        self.win.refresh()

    def clear(self):
        self.win.erase()  # erase is way smoother than clear()
        self.win.addstr(1, 1, StatusWindow.pattern % ('', 'up', 'down', 'left', 'right'))
        self.win.border()

sidewalk_window = None
status_window = None
# a = 0.01, d = 0.2, eps = 0.9 are good values for the finish module

alpha = 0.001  # how quickly do we learn in general?
discount = 0.8  # how much do we believe what our next action can get us?
epsilon = 0.9  # how often do we venture away from what we know works?
sidewalk_width = 7
sidewalk_length = 40
actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up down left right


class Module(object):
    name = ''
    max_iterations = 100000000
    scores = None
    weight = 1

    def __init__(self, module_name, default_score, weight=1):
        self.name = module_name
        self.scores = defaultdict(lambda: default_score)
        self.weight = weight
        if module_name == 'obstacle':
            self.max_iterations = 1000

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


def episode(qs, draw=False):
    sidewalk = StateSpace(sidewalk_width, sidewalk_length, obstacles=10)
    status_window.clear()

    total_reward = 0
    for time in xrange(qs[0].max_iterations):
        scores_actions = []
        state = None
        for q in qs:
            state = sidewalk.current_state(q.name)
            if random.random() < epsilon:
                score, action = q.get_top_score_action(state)
            else:
                score, action = q.get_random_score_action(state)
            scores_actions.append((score*q.weight, action))
        random.shuffle(scores_actions)

        score, action = sorted(scores_actions, key=lambda sa: sa[0], reverse=True)[0]
        # actions_taken = defaultdict(int)
        # actions_taken[action] += 1
        # args = [' '] + [actions_taken[a] for a in actions]
        # status_window.win.addstr(12, 1, status_window.pattern % tuple(args))

        # now we have the chosen action, and q's record of the score for taking that action in this state
        # if sidewalk.complete:
            # curses.endwin()
            # print 'Modules', ', '.join([q.name for q in qs])
            # raise Exception("oh hai")
        move_reward = sidewalk.move(action)
        state_reward = sum(sidewalk.current_reward(q.name) for q in qs)
        total_reward += move_reward + state_reward

        if len(qs) == 1:
            if draw:
                sidewalk_window.draw(sidewalk)
                status_window.draw(q)
                # status_window.win.addstr(i + 1, 1, ', '.join([q.name for q in qs]))

            next_state = sidewalk.current_state(qs[0].name)
            best_score = max(q.scores[(next_state, a)] for a in actions)
            qs[0].scores[(state, action)] = score + alpha * (state_reward + (discount * best_score) - score)

        if sidewalk.complete and 'finish' in [q.name for q in qs]:
            break

    # errlog('%s: total_reward = %s, time = %d' % (','.join([q.name for q in qs]), total_reward, time))
    return total_reward / float(time)


def run(stdscr):
    global sidewalk_window, status_window
    sidewalk_window = SidewalkWindow(sidewalk_width, sidewalk_length, 2, 2)
    status_window = StatusWindow(sidewalk_width + 4, 2)

    # 2 modules, a) finish, b) avoid obstacles
    qs = [Module('obstacle', 1, 1), Module('finish', 1, 1)]

    errlog('\t'.join([q.name for q in qs] + ['combined']))
    for run in range(1000):
        q_results = [episode([q], draw=True) for q in qs] + [episode(qs)]

        errlog('\t'.join(['%.8f' % q_res for q_res in q_results]))

if __name__ == '__main__':
    curses.wrapper(run)
