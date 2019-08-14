import time
import mysql.connector
from args import args
import gzip

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

def reset_job(job_id):
    query = "UPDATE jobs SET state=0 WHERE id=%s"
    con.execute(query, (job_id,))
    ctx.commit()

def create_result(job_id, generation_id, result_model_id):
    query = 'INSERT INTO results (job_id, model_id, generation_id) VALUES (%s, %s, %s)'
    con.execute(query, (job_id, result_model_id, generation_id))
    ctx.commit()
    return con.lastrowid

def get_results(strain_id, generation_id):
    query = """
        SELECT results.job_id, models.data FROM results 
            INNER JOIN models ON (models.strain_id=%s AND models.id=results.model_id) 
        WHERE generation_id=%s
        """
    con.execute(query, (strain_id, generation_id))
    res = con.fetchall()
    ctx.commit()
    res = [(it[0], gzip.decompress(it[1])) for it in res]
    return res

def is_generation_done(generation_id):
    query = """
        SELECT r.n_results >= 2 * j.n_jobs as done FROM 
            (SELECT COUNT(id) AS n_jobs FROM jobs 
                WHERE (state=1 OR state=0) AND generation_id=%s) j 
        JOIN (SELECT COUNT(id) as n_results FROM results WHERE generation_id=%s) r ON (TRUE);
        """
    con.execute(query, (generation_id, generation_id))
    res = bool(con.fetchone()[0])
    ctx.commit()
    return res

def get_job():
    while True:
        query = f'UPDATE jobs SET state=1, worker_name="{args.name}" WHERE state=0 AND LAST_INSERT_ID(id) LIMIT 1'
        con.execute(query)
        ctx.commit()
        if con.rowcount > 0:
            query = f'SELECT job_id, generation_id, strain1_id, model1_data, strain2_id, model2_data FROM job_models WHERE job_id=LAST_INSERT_ID()'
            con.execute(query)
            res = list(con.fetchone())
            ctx.commit()
            res[3] = gzip.decompress(res[3])
            res[5] = gzip.decompress(res[5])
            yield res
        else:
            print("[DB] Waiting for job...")
            time.sleep(0.5)


def create_model(strain_id, data):
    query = "INSERT INTO models (strain_id, data) VALUES (%s, %s)"
    con.execute(query, (strain_id, gzip.compress(data, 1)))
    ctx.commit()
    return con.lastrowid

def get_strains():
    query = "SELECT * FROM strains"
    con.execute(query)
    res = con.fetchall()
    ctx.commit()
    return res