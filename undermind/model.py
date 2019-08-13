import os

from execute import run
from args import args

MODEL_PATH = 'models'
RESULT_PATH = 'results'
CWD = args.path

def load_model(strain):
    return open(os.path.join(CWD, MODEL_PATH, str(strain)), 'rb').read()

def load_result(strain):
    return open(os.path.join(CWD, RESULT_PATH, str(strain)), 'rb').read()

def write_model(strain, data):
    os.makedirs(MODEL_PATH, exist_ok=True)
    open(os.path.join(CWD, MODEL_PATH, str(strain)), 'wb').write(data)

def create_model(strain):
    overmind(['-create', os.path.join(MODEL_PATH, str(strain))]).wait()
    return load_model(strain)

def overmind(args):
    return run(['./Overmind'] + args)

def openbw(model1_data, model2_data):
    write_model(1, model1_data)
    write_model(2, model2_data)
    model1_env = {
        "OPENBW_LAN_MODE": "FILE", 
        "OPENBW_FILE_READ": "fifor", 
        "OPENBW_FILE_WRITE": "fifow",
        "BWAPI_CONFIG_AUTO_MENU__CHARACTER_NAME": "1_model1"
         }
    model2_env = {
        "OPENBW_LAN_MODE": "FILE", 
        "OPENBW_FILE_READ": "fifow", 
        "OPENBW_FILE_WRITE": "fifor",
        "BWAPI_CONFIG_AUTO_MENU__CHARACTER_NAME": "2_model2"
        }
    p1 = run(['./BWAPILauncher'], model1_env)
    p2 = run(['./BWAPILauncher'], model2_env)
    p1.wait()
    p2.wait()
    r1 = load_result(1)
    r2 = load_result(2)
    return (r1, r2)
