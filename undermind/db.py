import time
import mysql.connector
from args import args

ctx = mysql.connector.connect(
    user=args.db_user, 
    password=args.db_pass, 
    host=args.db_host,
    database='scai', 
    auth_plugin='mysql_native_password',
    use_pure=True)
con = ctx.cursor()

def create_generation():
    query = "INSERT INTO generations () VALUES ()"
    con.execute(query)
    ctx.commit()
    return con.lastrowid

def create_strain():
    query = "INSERT INTO strains () VALUES ()"
    con.execute(query)
    ctx.commit()
    return con.lastrowid

def create_job(generation_id, model1_id, model2_id):
    query = "INSERT INTO jobs (generation_id, model1_id, model2_id) VALUES (%s, %s, %s)"
    con.execute(query, (generation_id, model1_id, model2_id))
    ctx.commit()
    return con.lastrowid

def report_result(job_id, result_model1_id, result_model2_id):
    query = f"UPDATE jobs SET model1_result_id=%s, model2_result_id=%s WHERE id=%s"
    con.execute(query, (result_model1_id, result_model2_id, job_id))
    ctx.commit()
    return con.lastrowid

def get_job():
    while True:
        query = f'UPDATE jobs SET state=1, worker_name="{args.name}" WHERE state=0 AND LAST_INSERT_ID(id) LIMIT 1'
        con.execute(query)
        ctx.commit()
        if con.rowcount > 0:
            query = f'SELECT LAST_INSERT_ID()'
            con.execute(query)
            job_id = con.fetchone()[0]
            query = f'SELECT job_id, generation_id, strain1_id, model1_data, strain2_id, model2_data FROM job_models WHERE job_id={job_id}'
            con.execute(query)
            res = con.fetchone()
            yield res
        else:
            print("[DB] Waiting for job...")
            time.sleep(1)


def create_model(strain_id, generation_id, data, is_result=False):
    query = "INSERT INTO models (strain_id, generation_id, is_result, data) VALUES (%s, %s, %s, _binary %s)"
    con.execute(query, (strain_id, generation_id, is_result, data))
    ctx.commit()
    return con.lastrowid

def get_strains():
    query = "SELECT * FROM strains"
    con.execute(query)
    return con.fetchall()