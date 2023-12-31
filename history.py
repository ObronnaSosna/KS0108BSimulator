import json
import ks0108b

commands = [[], [], []]


def add(cs, command):
    commands[cs].append(command)


def print():
    out = ""
    for i, cmds in enumerate(commands):
        out += f"CS{i}:\n"
        for command in cmds:
            out += f"{format(command,'010b')}  {ks0108b.commandLookup(command)}\n"
    return out


def save(filename):
    with open(filename, "w") as f:
        f.write(json.dumps(commands))


def saveHumanReadable(filename):
    with open(filename, "w") as f:
        f.write(print())


def load(filename):
    with open(filename, "r") as f:
        return json.loads(f.read())


def clear():
    commands = [[], [], []]
