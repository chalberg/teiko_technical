# ETL for dashboard displays
import sqlite3
import pandas as pd
from queries import (
    getCellFrequencies,
    getMelanomaResponses
)

def op_cell_frequencies(conn: sqlite3.Connection, export_path: str) -> None:
    df = pd.read_sql_query(getCellFrequencies, conn)
    df = df.rename(columns={"sample_id": "sample"})
    df.to_csv(f"{export_path}/cell_population_frequencies.csv", index=False)
    return

def op_melanoma_response(conn: sqlite3.Connection, export_path: str) -> None:
    df = pd.read_sql_query(getMelanomaResponses, conn)
    print(df.head(15))
    df.to_csv(f"{export_path}/melanoma_responses.csv", index=False)
    return


if __name__=="__main__":
    export_path = "exports"
    conn = sqlite3.connect("cellcount.db")
    op_cell_frequencies(conn=conn, export_path=export_path)
    op_melanoma_response(conn=conn, export_path=export_path)