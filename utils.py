import json
import os.path


TODO_TEMPLATE = {"metadata": {"todo_count": 0}, "todos": {}}


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def read_todo_data(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        todo_data = read_json(filename)
    else:
        todo_data = TODO_TEMPLATE
    return todo_data


def write_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
