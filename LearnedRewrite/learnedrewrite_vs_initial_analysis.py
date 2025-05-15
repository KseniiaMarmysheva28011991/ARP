import pandas as pd
from scipy.stats import shapiro, levene, mannwhitneyu
import numpy as np

# === Load input data ===
initial_df = pd.read_csv('Initial_queries_raw_results.csv')
sc_df = pd.read_csv('LearnedRewrite_raw_results.csv')
equivalence_df = pd.read_csv('LearnedRewrite_vs_Initial_queries_row_comparison.csv')
# === Create join_key for matching ===
initial_df['join_key'] = initial_df['TaskNo'].astype(str) + '_' + initial_df['ResponseId'].astype(str)
sc_df['join_key'] = sc_df['TaskNo'].astype(str) + '_' + sc_df['ResponseId'].astype(str)
equivalence_df['join_key'] = equivalence_df['TaskNo'].astype(str) + '_' + equivalence_df['ResponseId'].astype(str)

# === Merge initial and SC results ===
merged_df = pd.merge(sc_df, initial_df, on='join_key', suffixes=('_optimazed', '_initial'))

# === Function to perform statistical tests and compute metrics ===
def perform_tests(row):
    original_query = [row[f'time_pg_{i}_initial'] for i in range(1, 6)]
    optimized_query = [row[f'time_pg_{i}_optimazed'] for i in range(1, 6)]

    # Normality
    _, p_orig = shapiro(original_query)
    normality_orig = 'normal' if p_orig > 0.05 else 'not normal'

    _, p_opt = shapiro(optimized_query)
    normality_opt = 'normal' if p_opt > 0.05 else 'not normal'

    # Variance
    variance_initial = np.var(original_query, ddof=1)
    variance_optimazed = np.var(optimized_query, ddof=1)

    # Levene test for variance equality
    _, p_levene = levene(original_query, optimized_query)
    variance_equality = 'equal variances' if p_levene >= 0.05 else 'unequal variances'

    # Mann-Whitney U (one-sided test)
    _, p_mwu = mannwhitneyu(original_query, optimized_query, alternative='greater')
    significance = 'significant' if p_mwu < 0.05 else 'not significant'

    # Metric differences
    avg_pg_time_diff = row['avg_pg_time_optimazed'] - row['avg_pg_time_initial']
    median_pg_time_diff = row['median_pg_time_optimazed'] - row['median_pg_time_initial']
    avg_cost_diff = row['avg_cost_optimazed'] - row['avg_cost_initial']
    avg_rows_diff = row['avg_rows_optimazed'] - row['avg_rows_initial']

    return pd.Series({
        'normality_initial': normality_orig,
        'normality_optimazed': normality_opt,
        'variance_initial': variance_initial,
        'variance_optimazed': variance_optimazed,
        'variance_equality': variance_equality,
        'performance_difference': significance,
        'p_value_mannwhitney': p_mwu,
        'avg_pg_time_diff_optimazed_initial': avg_pg_time_diff,
        'median_pg_time_diff_optimazed_initial': median_pg_time_diff,
        'avg_cost_diff_optimazed_initial': avg_cost_diff,
        'avg_rows_diff_optimazed_initial': avg_rows_diff
    })

# === Apply the tests ===
results_df = merged_df.apply(perform_tests, axis=1)

# === Combine results ===
final_df = pd.concat([merged_df, results_df], axis=1)

# === Merge equivalence info ===
final_df = pd.merge(final_df, equivalence_df[['join_key', 'Final equivalence status']],
                    on='join_key', how='left')
final_df.rename(columns={'Final equivalence status': 'equivalent_query'}, inplace=True)

# === Save result ===
final_df.to_csv('LearnedRewrite_vs_Initial_queries_experiment_data.csv', index=False)
print("File saved: LearnedRewrite_vs_Initial_queries_experiment_data.csv")
