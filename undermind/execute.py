import subprocess
import os
from args import args

CWD = args.path

def run(command, extraenv=None):
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH'] + ':/opt/intel/mkl/lib/intel64_lin/'
    env['LD_PRELOAD'] = '/opt/intel/mkl/lib/intel64/libmkl_def.so:/opt/intel/mkl/lib/intel64/libmkl_avx2.so:/opt/intel/mkl/lib/intel64/libmkl_core.so:/opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so:/opt/intel/mkl/lib/intel64/libmkl_intel_thread.so:/opt/intel/lib/intel64_lin/libiomp5.so'
    if extraenv is not None:
        env.update(extraenv)
    return subprocess.Popen(command, cwd=CWD, stdout=None, env=env)
