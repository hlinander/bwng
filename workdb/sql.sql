DROP DATABASE IF EXISTS scai;
CREATE DATABASE scai;
USE scai;
CREATE TABLE strains (
	id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	created TIMESTAMP DEFAULT NOW()
);
CREATE TABLE generations (
	id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	created TIMESTAMP DEFAULT NOW()
);
CREATE TABLE models (
	id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	strain_id INT UNSIGNED NOT NULL,
	data LONGBLOB,
	created TIMESTAMP DEFAULT NOW(),
	FOREIGN KEY (strain_id) REFERENCES strains(id)
);

CREATE TABLE jobs (
	id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	generation_id INT UNSIGNED NOT NULL,
	model1_id INT UNSIGNED NOT NULL,
	model2_id INT UNSIGNED NOT NULL,
	worker_name TEXT DEFAULT NULL,
	state INT DEFAULT 0,
	started TIMESTAMP DEFAULT NULL,
	created TIMESTAMP DEFAULT NOW(),
	FOREIGN KEY (generation_id) REFERENCES generations(id),
	FOREIGN KEY (model1_id) REFERENCES models(id) ON DELETE CASCADE,
	FOREIGN KEY (model2_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE TABLE results (
	id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
	job_id INT UNSIGNED NOT NULL,
	model_id INT UNSIGNED NOT NULL,
	generation_id INT UNSIGNED NOT NULL,
	created TIMESTAMP DEFAULT NOW(),
	FOREIGN KEY (job_id) REFERENCES jobs(id),
	FOREIGN KEY (generation_id) REFERENCES generations(id),
	FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);


CREATE VIEW timed_out AS SELECT
	jobs.id as job_id,
	jobs.generation_id as generation_id,
	jobs.model1_id as model1_id,
	jobs.model2_id as model2_id
FROM jobs WHERE 
	jobs.state=1 AND
	jobs.started < ADDDATE(NOW(), INTERVAL -1 MINUTE);

CREATE VIEW unfinished_generations AS SELECT
	DISTINCT jobs.generation_id
FROM jobs WHERE 
	state!=2;

CREATE VIEW job_models AS SELECT 
	jobs.id as job_id, 
	jobs.generation_id as generation_id,
	m1.strain_id AS strain1_id, 
	m1.data AS model1_data, 
	m2.strain_id as strain2_id, 
	m2.data as model2_data 
FROM jobs 
	INNER JOIN models AS m1 ON (m1.id = jobs.model1_id) 
	INNER JOIN models AS m2 ON (m2.id = jobs.model2_id);
