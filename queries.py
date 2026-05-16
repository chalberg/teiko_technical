createSubjects = """
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id TEXT PRIMARY KEY,
        condition TEXT,
        age INT,
        sex TEXT,
        treatment TEXT,
        response TEXT,
        project TEXT
    )
"""

createSamples = """
    CREATE TABLE IF NOT EXISTS samples (
        sample_id TEXT PRIMARY KEY,
        subject_id TEXT REFERENCES subjects(subject_id),
        sample_type TEXT,
        time_from_treatment_start INT,
        b_cell_count INT,
        cd8_t_cell_count INT,
        cd4_t_cell_count INT,
        nk_cell_count INT,
        monocyte_count INT
    )
"""

createCellCounts = """
    CREATE TABLE IF NOT EXISTS cellCounts (
        sample_id TEXT,
        population TEXT,
        count INT,
        PRIMARY KEY (sample_id, population)
    )
"""

insertSubject = """
    INSERT OR IGNORE INTO subjects (
        subject_id,
        condition,
        age,
        sex,
        treatment,
        response,
        project
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
"""

insertSample = """
    INSERT INTO samples (
        sample_id,
        subject_id,
        sample_type,
        time_from_treatment_start
    ) VALUES (?, ?, ?, ?)
"""

insertCellCount = """
    INSERT INTO cellCounts (
        sample_id,
        population,
        count
    ) VALUES (?, ?, ?)
"""

getSampleCount = """
    SELECT COUNT(*) FROM samples;
"""

getSubjectCount = """
    SELECT COUNT(*) FROM subjects;
"""
getCellFrequencies = """
    SELECT
        sample_id,
        SUM(count) OVER (PARTITION BY sample_id) as total_count,
        population,
        count,
        ROUND(100.0 * count / SUM(count) OVER (PARTITION BY sample_id), 2) as percentage
    FROM cellCounts
"""

# Compare the differences in cell population relative frequencies of
# melanoma patients receiving miraclib who respond (responders) versus those who do not (non-responders),
# with the overarching aim of predicting response to the treatment miraclib.
# Response information can be found in column "response", with
# value "yes" for responding and value "no" for non-responding.
#     Please only include PBMC samples.
getMelanomaMaleResponderAvgBCell = """
    SELECT ROUND(AVG(cc.count), 2) as avg_b_cell_count
    FROM subjects as sub
    JOIN samples as sam ON sub.subject_id = sam.subject_id
    JOIN cellCounts as cc ON sam.sample_id = cc.sample_id
    WHERE
        sub.condition = "melanoma" AND
        sub.sex = "M" AND
        sub.response = "yes" AND
        sam.sample_type = "PBMC" AND
        sam.time_from_treatment_start = 0 AND
        cc.population = "b_cell"
"""

getBaselineSubset = """
    SELECT
        sub.subject_id,
        sub.project,
        sub.response,
        sub.sex,
        sam.sample_id
    FROM subjects as sub
    JOIN samples as sam ON sub.subject_id = sam.subject_id
    WHERE
        sub.condition = "melanoma" AND
        sub.treatment = "miraclib" AND
        sam.sample_type = "PBMC" AND
        sam.time_from_treatment_start = 0
"""

getMelanomaResponses = """
    WITH c AS (
        SELECT
            sample_id,
            SUM(count) OVER (PARTITION BY sample_id) as total_count,
            population,
            count,
            ROUND(100.0 * count / SUM(count) OVER (PARTITION BY sample_id), 2) as percentage
        FROM cellCounts
    )
    SELECT
        sub.subject_id,
        sub.condition,
        sub.response,
        sub.treatment,
        sam.sample_id,
        sam.sample_type,
        c.percentage,
        c.population
    FROM
        subjects as sub
    LEFT JOIN samples as sam ON sub.subject_id = sam.subject_id
    LEFT JOIN c ON sam.sample_id = c.sample_id
    WHERE
        sub.condition = "melanoma" AND
        sub.treatment = "miraclib" AND
        sam.sample_type = "PBMC"
"""