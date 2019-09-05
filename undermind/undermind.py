import db
import os
import sys
from itertools import combinations
import time
import traceback
import requests
import json

from args import args
from model import load_model, create_model, openbw, overmind
import model
import stats

N_STRAINS = 4
CWD = args.path

def create_or_get_strains():
    ind_data = db.get_strains()
    if not ind_data:
        for _ in range(N_STRAINS):
            db.create_strain()
    ind_data = db.get_strains()
    return list(map(lambda d: d[0], ind_data))

def reset_models(strains):
    for strain in strains:
        create_model(strain)

def create_or_load_models(strains):
    models = dict()
    for strain in strains:
        try:
            model = load_model(strain)
        except FileNotFoundError:
            model = create_model(strain)
        models[strain] = model
    return models

def schedule_generation(models):
    generation_id = db.create_generation()
    n_models = len(models)
    model_ids = []
    for strain_id, data in models.items():
        model_ids.append(db.create_model(strain_id, data))

    for (id1, id2) in combinations(model_ids, 2):
            db.create_job(generation_id, id1, id2)
    
    return generation_id

def wait_for_generation(generation_id):
    while not db.is_generation_done(generation_id):
        db.reset_timed_out()
        db.print_stats()
        time.sleep(0.5)

def wait_for_resume():
    for (generation,) in db.unfinished_generations():
        print(f"[Undermind] Waiting for straggling jobs in generation {generation}")
        wait_for_generation(generation)

def undermind_server():
    strains = create_or_get_strains()
    if args.reset_models:
        reset_models(strains)
    models = create_or_load_models(strains)
    os.makedirs(model.RESULT_PATH, exist_ok=True)
    if not args.reset_models:
        wait_for_resume()
    while True:
        generation_id = schedule_generation(models)
        print(f"[Undermind server] Created generation {generation_id}")
        wait_for_generation(generation_id)
        print(f"[Undermind server] Generation {generation_id} done")
        overminds = []
        files_to_delete = []
        for strain_id, model_data in models.items():
            res = db.get_results(strain_id, generation_id)
            result_files = []
            for job_id, data in res:
                result_file = os.path.join(CWD, model.RESULT_PATH, f"{strain_id}_{job_id}")
                open(result_file, 'wb').write(data)
                result_files.append(result_file)
                files_to_delete.append(result_file)
            strain_results_file = os.path.join(CWD, model.RESULT_PATH, f"{strain_id}_results")
            open(strain_results_file, "w").write("\n".join(result_files))
            strain_current_model_file = model.model_path(strain_id)
            overminds.append(overmind(["-update", strain_current_model_file, strain_results_file, strain_current_model_file]).wait())
        #[it.wait() for it in overminds]

        for f in files_to_delete:
            os.unlink(f)
        for strain_id in models:
            models[strain_id] = load_model(strain_id)
            stats_file = model.model_path(strain_id) + "_stats.json"
            stats.post_json_file("results", stats_file, dict(strain=strain_id, generation=generation_id))
        db.delete_results(generation_id)

        

def undermind_client():
    for job_id, generation_id, strain1_id, model1_data, strain2_id, model2_data in db.get_job():
        try:
            print(f"[Undermind client] Generation {generation_id} job {job_id} started")
            (result1, result2) = openbw(model1_data, model2_data, strain1_id, strain2_id, generation_id)
            print(f"[Undermind client] Generation {generation_id} job {job_id} done")
            mr1 = db.create_model(strain1_id, result1)
            mr2 = db.create_model(strain2_id, result2)
            print(f"[Undermind client] Models created")
            db.create_result(job_id, generation_id, mr1)
            db.create_result(job_id, generation_id, mr2)
            db.finish_job(job_id)
            print(f"[Undermind client] Results created")
        except Exception as e:
            print(f"[Undermind client] Job {job_id} has no pants!")
            traceback.print_exc()
            db.reset_job(job_id)
            

if args.server:
    if args.reset_index:
        stats.delete_index("results")
        stats.index_type("results", {
            'timestamp': {
                'type': 'date'
            }
        })
    undermind_server()
elif args.client:
    undermind_client()
# g = db.create_generation()
# print(db.get_strains() )
# m1 = db.create_strain()
# m2 = db.create_strain()
# db.create_job(g, m1, m2)
# db.create_job(g, m1, m2)
# db.create_job(g, m1, m2)
# db.create_job(g, m1, m2)
# db.create_job(g, m1, m2)
# db.create_job(g, m1, m2)
# db.create_job(g, m1, m2)
# print(db.get_strains())
