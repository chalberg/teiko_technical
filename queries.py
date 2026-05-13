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
        time_from_treatment_start,
        b_cell_count,
        cd8_t_cell_count,
        cd4_t_cell_count,
        nk_cell_count,
        monocyte_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

getSampleCount = """
    SELECT COUNT(*) FROM samples;
"""

getSubjectCount = """
    SELECT COUNT(*) FROM subjects;
"""