import sqlite3
import os
import pandas as pd
from queries import (
    createSamples,
    createSubjects,
    insertSample,
    insertSubject,
    getSampleCount,
    getSubjectCount
)

def _create_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(createSubjects)
    cursor.execute(createSamples)
    conn.commit()
    return

def _populate_tables(df: pd.DataFrame, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    for _, row in df.iterrows():
        subjectData = (
            row["subject"],
            row["condition"],
            row["age"],
            row["sex"],
            row["treatment"],
            row["response"],
            row["project"]
        )
        cursor.execute(insertSubject, subjectData)
        sampleData = (
            row["sample"],
            row["subject"],
            row["sample_type"],
            row["time_from_treatment_start"],
            row["b_cell"],
            row["cd8_t_cell"],
            row["cd4_t_cell"],
            row["nk_cell"],
            row["monocyte"]
        )
        cursor.execute(insertSample, sampleData)
    conn.commit()

def _load_cell_counts_df(import_path: str) -> pd.DataFrame:
    if not os.path.exists(import_path):
        raise FileNotFoundError(f"Failed to find cell count data at: {import_path}")
    return pd.read_csv(import_path, sep=",", header=0)

def _validate_table_counts(df: pd.DataFrame, conn:sqlite3.Connection) -> None:
    """
    Checks whether table counts match dataframe counts. Raises an error if mismatch is found.
    """
    # check samples
    cursor = conn.cursor()
    expectedSamples = len(df)
    cursor.execute(getSampleCount)
    sampleCount = cursor.fetchone()[0]
    if sampleCount != expectedSamples:
        raise ValueError(f"Found {sampleCount} samples, but expected {expectedSamples}.")

    # check subjects
    expectedSubjects = len(df["subject"].unique())
    cursor.execute(getSubjectCount)
    subjectCount = cursor.fetchone()[0]
    if subjectCount != expectedSubjects:
        raise ValueError(f"Found {subjectCount} subjects, but expected {expectedSubjects}.")

def _init_db(import_path: str) -> None:
    """
    Primary execution function to create and populate db for cell count data.
    """
    # initialize schema
    if os.path.exists("cellcount.db"):
        os.remove("cellcount.db")
    conn = sqlite3.connect("cellcount.db")
    try:
        _create_tables(conn)
    except Exception as e:
        conn.close()
        print(f"Error occured while creating tables.\nError: {e}")
        return
    
    # insert data
    try:
        df = _load_cell_counts_df(import_path)
        _populate_tables(df, conn)
    except Exception as e:
        conn.close()
        print(f"Error occured while inserting data into tables.\nError: {e}")
        return
    try:
        _validate_table_counts(df=df, conn=conn)
    except ValueError as e:
        print(e)
    finally:
        conn.close()
    
if __name__=="__main__":
    _init_db(import_path="imports/cell-count.csv")
