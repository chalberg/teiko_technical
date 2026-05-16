# dashboard run file
import streamlit as st
import pandas as pd

def _display_cell_frequencies(import_path: str) -> None:
    df = pd.read_csv(f"{import_path}/cell_population_frequencies.csv")
    with st.container(border=True):
        st.header("Cell Population Frequencies")

        # population & sample filters
        filtered_df = df.copy()
        col1, col2 = st.columns(2)
        with col1:
            sample_options = df["sample"].unique().tolist()
            sample_options.insert(0, "All Samples")
            selected_sample = st.selectbox("Select Sample(s)", sample_options)
        if selected_sample != "All Samples":
            filtered_df = filtered_df[filtered_df["sample"]==selected_sample]
            
        with col2:
            pop_options = df["population"].unique().tolist()
            pop_options.insert(0, "All Populations")
            selected_population = st.selectbox("Select Population(s)", pop_options)
        if selected_population != "All Populations":
            filtered_df = filtered_df[filtered_df["population"]==selected_population]
        
        # display
        st.dataframe(
            filtered_df,
            column_config={
                "percentage": st.column_config.NumberColumn(
                    "percentage",
                    help="Proportion of cell population in total cell count of sample",
                    format="%.2f%%"
                )
            },
            hide_index=True,
        )
    return

if __name__=="__main__":
    import_path = "exports"
    _display_cell_frequencies(import_path)