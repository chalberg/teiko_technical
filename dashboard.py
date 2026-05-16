# dashboard run file
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

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

@st.cache_data
def _load_melanoma_responses(import_path: str) -> pd.DataFrame:
    return pd.read_csv(f"{import_path}/melanoma_responses.csv")

def _display_boxplots(import_path: str) -> None:
    df = _load_melanoma_responses(import_path)
    with st.container(border=True):
        st.header("Cell Population Frequencies by Response Group")
        st.caption("Melanoma patients treated with miraclib — PBMC samples only")
        fig = px.box(
            df,
            x="response",
            y="percentage",
            facet_col="population",
            color="response",
            color_discrete_map={"yes": "green", "no": "red"},
            labels={"response": "Response", "percentage": "Frequency (%)"},
        )
        fig.update_layout(showlegend=False)
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig, use_container_width=True)

def _display_normality_analysis(import_path: str) -> None:
    df = _load_melanoma_responses(import_path)
    populations = df["population"].unique().tolist()
    groups = [("yes", "Responders", "green"), ("no", "Non-Responders", "red")]

    with st.container(border=True):
        st.header("Normality Analysis")
        st.caption("Points following the reference line indicate normally distributed data.")

        # Q-Q plots: rows (group) x cols (cell population)
        fig = make_subplots(
            rows=2, cols=len(populations),
            column_titles=populations,
            row_titles=["Responders", "Non-Responders"],
            horizontal_spacing=0.06,
            vertical_spacing=0.12,
        )
        for col_idx, pop in enumerate(populations, 1):
            for row_idx, (response, label, color) in enumerate(groups, 1):
                data = df[(df["population"] == pop) & (df["response"] == response)]["percentage"].values
                (theoretical_q, observed_q), (slope, intercept, _) = stats.probplot(data)
                fig.add_trace(go.Scatter(
                    x=theoretical_q, y=observed_q,
                    mode="markers",
                    name=label,
                    marker=dict(color=color, size=5),
                    showlegend=(col_idx == 1),
                ), row=row_idx, col=col_idx)
                line_x = [float(min(theoretical_q)), float(max(theoretical_q))]
                line_y = [slope * x + intercept for x in line_x]
                fig.add_trace(go.Scatter(
                    x=line_x, y=line_y,
                    mode="lines",
                    line=dict(color="gray", dash="dash", width=1),
                    showlegend=False,
                ), row=row_idx, col=col_idx)

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def _load_ttest_results(import_path: str) -> pd.DataFrame:
    return pd.read_csv(f"{import_path}/ttest_results.csv")

def _display_ttest_results(import_path: str) -> None:
    df = _load_ttest_results(import_path)
    with st.container(border=True):
        st.header("Statistical Analysis: Responders vs Non-Responders")
        st.markdown("""
            **Test:** Student's t-test (independent samples, equal variance assumed)

            **Groups:** Melanoma patients treated with miraclib & PBMC sample types

            **Null hypothesis:** No difference in mean cell population frequency between responders and non-responders

            **Confidence level:** alpha = 0.05 (Bonferroni correction divides alpha across 5 populations)

            **Normality:** See Q-Q plots above
        """)
        st.dataframe(
            df,
            column_config={
                "population": st.column_config.TextColumn("Population"),
                "n_responders": st.column_config.NumberColumn("N (Responders)"),
                "n_non_responders": st.column_config.NumberColumn("N (Non-Responders)"),
                "mean_pct_responders": st.column_config.NumberColumn("Mean % (Responders)", format="%.2f%%"),
                "mean_pct_non_responders": st.column_config.NumberColumn("Mean % (Non-Responders)", format="%.2f%%"),
                "t_statistic": st.column_config.NumberColumn("t Statistic"),
                "p_value": st.column_config.NumberColumn("p-value"),
                "p_value_bonferroni": st.column_config.NumberColumn("p-value (Bonferroni)"),
                "significant": st.column_config.CheckboxColumn("Significant?"),
            },
            hide_index=True,
        )

def _display_baseline_analysis(import_path: str) -> None:
    samples_by_project = pd.read_csv(f"{import_path}/baseline_samples_by_project.csv")
    subjects_by_response = pd.read_csv(f"{import_path}/baseline_subjects_by_response.csv")
    subjects_by_sex = pd.read_csv(f"{import_path}/baseline_subjects_by_sex.csv")

    with st.container(border=True):
        st.header("Baseline Subset Analysis")
        st.caption(
            "Population:"
            "Melanoma patients"
            " & Treated with miraclib"
            " & PBMC samples at baseline (time from treatment start = 0)"
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Samples by Project")
            st.dataframe(samples_by_project, hide_index=True)
        with col2:
            st.subheader("Subjects by Response")
            st.dataframe(subjects_by_response, hide_index=True)
        with col3:
            st.subheader("Subjects by Sex")
            st.dataframe(subjects_by_sex, hide_index=True)

if __name__=="__main__":
    import_path = "exports"
    _display_cell_frequencies(import_path)
    _display_boxplots(import_path)
    _display_normality_analysis(import_path)
    _display_ttest_results(import_path)
    _display_baseline_analysis(import_path)