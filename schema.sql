CREATE TABLE IF NOT EXISTS runs (
  run_accession INTEGER PRIMARY KEY AUTOINCREMENT,
  run_date TEXT NOT NULL,
  machine_type TEXT NOT NULL,
  machine_kit TEXT NOT NULL,
  lane INTEGER NOT NULL,
  data_uri TEXT NOT NULL,
  comment TEXT NOT NULL,
  admin_comment TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS samples (
  sample_accession INTEGER PRIMARY KEY AUTOINCREMENT,
  sample_name TEXT NOT NULL,
  run_accession INTEGER
    REFERENCES runs(run_accession)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  barcode_sequence TEXT NOT NULL,
  primer_sequence TEXT DEFAULT NULL,
  sample_type TEXT DEFAULT NULL,
  subject_id TEXT DEFAULT NULL,
  host_species TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS annotations (
  `sample_accession` INTEGER
    REFERENCES samples(sample_accession)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  `key` TEXT NOT NULL,
  `val` TEXT NOT NULL
);

CREATE VIEW runs_samplecounts AS
  SELECT 
    `runs`.`run_accession` AS `run_accession`,
    `runs`.`run_date` AS `run_date`,
    `runs`.`machine_type` AS `machine_type`,
    `runs`.`machine_kit` AS `machine_kit`,
    `runs`.`lane` AS `lane`,
    `runs`.`data_uri` AS `data_uri`,
    `runs`.`comment` AS `comment`,
    count(`samples`.`sample_accession`) AS `sample_count` 
  FROM (
    `runs` LEFT OUTER JOIN `samples` ON (
      `runs`.`run_accession` = `samples`.`run_accession`))
  GROUP BY `runs`.`run_accession` 
  ORDER BY 
      `runs`.`run_date` DESC,
      `runs`.`machine_type`,
      `runs`.`machine_kit`,
      `runs`.`lane`;

CREATE VIEW runs_samples AS
  SELECT 
    `samples`.`sample_accession` AS `sample_accession`,
    `samples`.`sample_name` AS `sample_name`,
    `samples`.`barcode_sequence` AS `barcode_sequence`,
    `samples`.`primer_sequence` AS `primer_sequence`,
    `runs`.`run_accession` AS `run_accession`,
    `runs`.`run_date` AS `run_date`,
    `runs`.`machine_type` AS `machine_type`,
    `runs`.`machine_kit` AS `machine_kit`,
    `runs`.`lane` AS `lane`,
    `runs`.`data_uri` AS `data_uri`,
    `runs`.`comment` AS `run_comment` 
  FROM (`runs` JOIN `samples` ON (
    `runs`.`run_accession` = `samples`.`run_accession`))
  ORDER BY
    `runs`.`run_date` DESC,
    `runs`.`machine_type`,
    `runs`.`machine_kit`,
    `runs`.`lane`,
    `samples`.`sample_accession`;

CREATE VIEW annotation_keys AS
  SELECT
    `annotations`.`key` AS `key`,
    count(`annotations`.`key`) AS `key_counts`
  FROM `annotations`
  GROUP BY `annotations`.`key`;

CREATE VIEW annotation_vals_by_run AS
  SELECT
    `samples`.`run_accession` AS `run_accession`,
    `runs`.`run_date` AS `run_date`,
    `runs`.`comment` AS `run_comment`,
    `annotations`.`key` AS `key`,
    `annotations`.`val` AS `val`,
    `runs`.`run_date` AS `run_date`,
    `runs`.`comment` AS `run_comment`,
    `annotations`.`key` AS `key`,
    `annotations`.`val` AS `val`,
    COUNT(`annotations`.`sample_accession`) AS `sample_count`
  FROM ((`annotations` JOIN `samples` ON (
    `annotations`.`sample_accession` = `samples`.`sample_accession`))
    JOIN `runs` ON (
      `samples`.`run_accession` = `runs`.`run_accession`))
  GROUP BY 
    `samples`.`run_accession`,
    `annotations`.`key`,
    `annotations`.`val`
  ORDER BY
    `annotations`.`key`,
    `runs`.`run_date` DESC, 
    `samples`.`run_accession`, 
    COUNT(`annotations`.`sample_accession`) DESC,
    `annotations`.`val`;
