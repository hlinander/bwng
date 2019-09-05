import os

from execute import run
from args import args

MODEL_PATH = 'models'
RESULT_PATH = 'results'
CWD = args.path


def model_path(strain):
    return os.path.join(CWD, MODEL_PATH, args.name + str(strain)) 

def load_model(strain):
    return open(model_path(strain), 'rb').read()

def load_result(strain):
    path = os.path.join(CWD, RESULT_PATH, args.name + str(strain))
    result = open(path, 'rb').read()
    safe_unlink(path)
    return result

def write_model(strain, data):
    os.makedirs(MODEL_PATH, exist_ok=True)
    open(model_path(strain), 'wb').write(data)

def create_model(strain):
    overmind(['-create', model_path(strain)]).wait()
    return load_model(strain)

def overmind(args):
    return run(['./Overmind'] + args)

def openbw(model1_data, model2_data, strain1_id, strain2_id, generation_id):
    print("[Model] Writing models")
    write_model(strain1_id, model1_data)
    write_model(strain2_id, model2_data)
    model1_env = {
        "OPENBW_LAN_MODE": "LOCAL", 
        "OPENBW_LOCAL_PATH": f"{args.name}_local", 
        "BWAPI_CONFIG_AUTO_MENU__CHARACTER_NAME": f"{args.name}_{generation_id}_{strain1_id}_{strain2_id}"
         }
    model2_env = {
        "OPENBW_LAN_MODE": "LOCAL", 
        "OPENBW_LOCAL_PATH": f"{args.name}_local", 
        "BWAPI_CONFIG_AUTO_MENU__CHARACTER_NAME": f"{args.name}_{generation_id}_{strain2_id}_{strain1_id}"
        }
    print("[Model] Launching openbw")
    p1 = run(['./BWAPILauncher'], model1_env)
    p2 = run(['./BWAPILauncher'], model2_env)
    try:
        p1.wait(args.timeout)
        p2.wait(args.timeout)
        safe_unlink(os.path.join(CWD, f"{args.name}_local"))
    except:
        safe_unlink(os.path.join(CWD, f"{args.name}_local"))
        p1.kill()
        p2.kill()
        raise Exception("No pants!")
    r1 = load_result(strain1_id)
    r2 = load_result(strain2_id)
    return (r1, r2)

def safe_unlink(path):
    try:
        os.unlink(path)
    except:
        pass
