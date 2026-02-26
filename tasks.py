#!/usr/bin/env python3

from os import listdir, mkdir
from os.path import exists, dirname, isdir, isfile, realpath
import sys

HERE = dirname(realpath(__file__))
TASK_DIR = f"{HERE}/tasks"

SEP = '|'
MAX_DESC_LEN = 20 # maximum characters to display for a task


def fail(*msg):
    print(*msg, file=sys.stderr)
    sys.exit(1)


# check that task dir exists
if not exists(TASK_DIR):
    mkdir(TASK_DIR)
    print("Created task directory in", TASK_DIR)
elif not isdir(TASK_DIR):
    fail("Task directory exists but isn't a directory:", TASK_DIR)


def get_lanes():
    """Read and return lanes from lane files from task directory.
    This function returns a list of lanes, each lane being a dictionary with
    the keys 'name' and 'tasks'. lane['tasks'] is a list of dictionaries with
    the keys 'description', 'number', and possibly 'details'.
    """
    global TASK_DIR

    # read files from lane directory
    item_names = [name for name in listdir(path=TASK_DIR) if name != 'lanes']

    # sort lanes
    lanes_file = TASK_DIR + "/lanes"
    if isfile(lanes_file):
        with open(lanes_file, 'r') as f:
            lane_names = []
            for line in f.readlines():
                lane_name = line.strip()
                if lane_name not in item_names:
                    fail("Lanes file found, but contains unknown lane name:", lane_name)
                lane_names.append(lane_name)
    else:
        print("No lanes file found, sorting lanes alphabetically")
        lane_names = sorted(item_names)

    # read tasks
    lanes = []
    for n in lane_names:
        p = TASK_DIR + "/" + n
        if isdir(p):
            continue
        lane = {'name': n, 'tasks': []}
        with open(p,'r') as f:
            for l in f.readlines():
                task = {}
                items = [i.strip() for i in l.split(SEP)]
                task['description'] = items[0]
                if len(items) > 1:
                    task['details'] = items[1]
                lane['tasks'].append(task)
        lanes.append(lane)

    # highest intersecting diagonal = highest manhattan distance
    highest_diag_i = max(i+len(lane['tasks']) for i,lane in enumerate(lanes))

    # numerate tasks (diagonally)
    task_n = 1
    for diag_i in range(highest_diag_i):
        for lane_i in range(diag_i+1):
            task_i = diag_i - lane_i

            # if there's a task at that position, give it a number
            def _getn(l, n):
                if -len(l) <= n and n < len(l):
                    return l[n]
                return None
            lane, task = _getn(lanes, lane_i), None
            if lane:
                task = _getn(lane['tasks'], task_i)
            if task:
                task['number'] = task_n
                task_n += 1

    return lanes


def overview():
    """Show all lanes and the tasks in them"""
    lanes = get_lanes()

    # calculate column width
    for lane in lanes:
        lane_col_width = len(lane['name'])
        for task in lane['tasks']:
            task_col_width = len(f"{task['number']} {task['description']}")
            lane_col_width = max(lane_col_width, task_col_width)
        lane['width'] = min(lane_col_width, MAX_DESC_LEN)

    # print lane names
    for lane in lanes:
        print('| ', end='')
        s = f"{lane['name']:<{lane['width']}}"
        if len(s) > lane['width']:
            s = s[:lane['width']-3] + "..."
        print(s, end=' ')
    print(' |')

    # print separator line
    for lane in lanes:
        print('|-', end='')
        print('-' * lane['width'], end='-')
    print('-|')

    # print task descriptions
    rows = max(len(lane['tasks']) for lane in lanes)
    for row_i in range(rows):
        for lane in lanes:
            print('| ', end='')
            task, s = None, ''
            if row_i < len(lane['tasks']):
                task = lane['tasks'][row_i]
                s = f"{task.get('number')} "
            if row_i < len(lane['tasks']):
                s += task['description']
            if len(s) > lane['width']:
                s = s[:lane['width']-3] + "..."
            print(f"{s:<{lane['width']}}", end=' ')
        print(' |')


def main():
    if len(sys.argv) <= 1:
        overview()
    else:
        cmd = sys.argv[1]
        pass # TODO
        print(cmd)


if __name__ == "__main__":
    main()


# TODO save "<desc> | <details>" (details can be multiline)
