import subprocess
import os
from args import args

CWD = args.path

def run(command, extraenv=None):
    env = os.environ.copy()
    if extraenv is not None:
        env.update(extraenv)
    return subprocess.Popen(command, cwd=CWD, stdout=None, env=env)
