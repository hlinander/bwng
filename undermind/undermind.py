import db
import sys
from itertools import combinations

from args import args
from model import load_model, create_model, openbw

N_STRAINS = 3

def create_or_get_strains():
    ind_data = db.get_strains()
    if not ind_data:
        for _ in range(N_STRAINS):
            db.create_strain()
    ind_data = db.get_strains()
    return list(map(lambda d: d[0], ind_data))

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
    model_ids = dict()
    for strain_id, data in models.items():
        model_ids[strain_id] = db.create_model(strain_id, generation_id, data)

    for (id1, id2) in combinations(models.keys(), 2):
            db.create_job(generation_id, id1, id2)
            
def undermind_server():
    strains = create_or_get_strains()
    models=create_or_load_models(strains)
    schedule_generation(models)

def undermind_client():
    for job_id, generation_id, strain1_id, model1_data, strain2_id, model2_data in db.get_job():
        (result1, result2) = openbw(model1_data, model2_data)
        mr1 = db.create_model(strain1_id, generation_id, result1, is_result=True)
        mr2 = db.create_model(strain2_id, generation_id, result2, is_result=True)
        db.report_result(job_id, mr1, mr2)

if args.server:
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
