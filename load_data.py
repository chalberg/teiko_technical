import sqlite3
import os
import pandas as pd
from queries import (
    createSamples,
    createSubjects,
    createCellCounts,
    insertSample,
    insertSubject,
    insertCellCount,
)

def _create_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(createSubjects)
    cursor.execute(createSamples)
    cursor.execute(createCellCounts)
    conn.commit()
    return

def _insert_subject(row: pd.Series, cursor: sqlite3.Cursor) -> None:
    data = (
        row.get("subject"),
        row.get("condition"),
        row.get("age"),
        row.get("sex"),
        row.get("treatment"),
        row.get("response"),
        row.get("project"),
    )
    if any(x is None for x in data):
        return
    cursor.execute(insertSubject, data)

def _insert_sample(row: pd.Series, cursor: sqlite3.Cursor) -> None:
    data = (
        row.get("sample"),
        row.get("subject"),
        row.get("sample_type"),
        row.get("time_from_treatment_start"),
    )
    if any(x is None for x in data):
        return
    cursor.execute(insertSample, data)

def _insert_cell_counts(row: pd.Series, cursor: sqlite3.Cursor) -> None:
    for pop in ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]:
        data = (
            row.get("sample"),
            pop,
            row.get(pop),
        )
        if any(x is None for x in data):
            continue
        cursor.execute(insertCellCount, data)

def _populate_tables(df: pd.DataFrame, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    for _, row in df.iterrows():
        _insert_subject(row, cursor)
        _insert_sample(row, cursor)
        _insert_cell_counts(row, cursor)
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
    cursor.execute("SELECT COUNT(*) FROM samples")
    sampleCount = cursor.fetchone()[0]
    if sampleCount != expectedSamples:
        raise ValueError(f"Found {sampleCount} samples, but expected {expectedSamples}.")

    # check subjects
    expectedSubjects = len(df["subject"].unique())
    cursor.execute("SELECT COUNT(*) FROM subjects")
    subjectCount = cursor.fetchone()[0]
    if subjectCount != expectedSubjects:
        raise ValueError(f"Found {subjectCount} subjects, but expected {expectedSubjects}.")
    
    # check cell counts - 5 counts / sample
    expectedCellCount = int(expectedSamples * 5)
    cursor.execute("SELECT COUNT(*) FROM cellCounts")
    cellCount = cursor.fetchone()[0]
    if cellCount != expectedCellCount:
        raise ValueError(f"Found {cellCount} cell counts, but expected {expectedCellCount}.")

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
