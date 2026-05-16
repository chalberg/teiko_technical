# ETL for dashboard displays
import sqlite3
import pandas as pd
from scipy import stats
import os
from queries import (
    getCellFrequencies,
    getMelanomaResponses,
    getBaselineSubset
)

def op_cell_frequencies(conn: sqlite3.Connection, export_path: str) -> None:
    df = pd.read_sql_query(getCellFrequencies, conn)
    df = df.rename(columns={"sample_id": "sample"})
    df.to_csv(f"{export_path}/cell_population_frequencies.csv", index=False)
    return

def op_melanoma_response(conn: sqlite3.Connection, export_path: str) -> None:
    df = pd.read_sql_query(getMelanomaResponses, conn)
    df.to_csv(f"{export_path}/melanoma_responses.csv", index=False)
    return


def op_ttest(export_path: str) -> None:
    ALPHA = 0.05
    df = pd.read_csv(f"{export_path}/melanoma_responses.csv")
    populations = df["population"].unique().tolist()
    n_tests = len(populations)

    results = []
    for pop in populations:
        pop_df = df[df["population"] == pop]
        responders = pop_df[pop_df["response"] == "yes"]["percentage"].values
        non_responders = pop_df[pop_df["response"] == "no"]["percentage"].values
        stat, p_value = stats.ttest_ind(responders, non_responders)
        p_corrected = min(p_value * n_tests, 1.0)
        results.append({
            "population": pop,
            "n_responders": len(responders),
            "n_non_responders": len(non_responders),
            "mean_pct_responders": round(float(pd.Series(responders).mean()), 2),
            "mean_pct_non_responders": round(float(pd.Series(non_responders).mean()), 2),
            "t_statistic": round(stat, 4),
            "p_value": round(p_value, 4),
            "p_value_bonferroni": round(p_corrected, 4),
            "significant": p_corrected < ALPHA,
        })

    pd.DataFrame(results).to_csv(f"{export_path}/ttest_results.csv", index=False)


def op_baseline_subset(conn: sqlite3.Connection, export_path: str) -> None:
    df = pd.read_sql_query(getBaselineSubset, conn)
    subjects = df.drop_duplicates(subset="subject_id")

    samples_by_project = (
        df.groupby("project")["sample_id"]
        .count()
        .reset_index()
        .rename(columns={"sample_id": "sample_count"})
    )
    subjects_by_response = (
        subjects.groupby("response")["subject_id"]
        .count()
        .reset_index()
        .rename(columns={"subject_id": "subject_count"})
    )
    subjects_by_sex = (
        subjects.groupby("sex")["subject_id"]
        .count()
        .reset_index()
        .rename(columns={"subject_id": "subject_count"})
    )

    samples_by_project.to_csv(f"{export_path}/baseline_samples_by_project.csv", index=False)
    subjects_by_response.to_csv(f"{export_path}/baseline_subjects_by_response.csv", index=False)
    subjects_by_sex.to_csv(f"{export_path}/baseline_subjects_by_sex.csv", index=False)

if __name__=="__main__":
    export_path = "exports"
    if not os.path.exists(export_path):
        os.mkdir(export_path)
        
    conn = sqlite3.connect("cellcount.db")
    op_cell_frequencies(conn=conn, export_path=export_path)
    op_melanoma_response(conn=conn, export_path=export_path)
    op_ttest(export_path=export_path)
    op_baseline_subset(conn=conn, export_path=export_path)