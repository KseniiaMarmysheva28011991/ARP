import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Colors ===
color_total = "#D5D6E8"
color_improved = "#B7B745"
color_shadow = "#505FA2"

# === Load input data ===
df_total = pd.read_csv("Initial_queries_raw_results.csv")
df_exp = pd.read_csv("SC_vs_Initial_queries_experiment_data.csv")

# === Process total (all queries) ===
df_total = df_total.dropna(subset=['avg_pg_time'])
bins = [0, 10, 20, 30, 40, 50, 100, 200, 300, 500, 1000, float('inf')]
labels = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-100", "100-200", "200-300", "300-500", "500-1000", "1000+"]
df_total['TimeRange'] = pd.cut(df_total['avg_pg_time'], bins=bins, labels=labels, right=False)
total_counts = df_total.groupby('TimeRange', observed=False).size().reset_index(name='Total')

# === Process improved queries (only significant & equivalent) ===
df_exp = df_exp.dropna(subset=["avg_pg_time_initial", "avg_pg_time_sc"])
df_exp = df_exp[df_exp["equivalent_query"].astype(str).str.upper() == "TRUE"]
df_exp = df_exp[df_exp["performance_difference"] == "significant"]
df_exp = df_exp[df_exp["avg_pg_time_sc"] < df_exp["avg_pg_time_initial"]]
df_exp['TimeRange'] = pd.cut(df_exp['avg_pg_time_initial'], bins=bins, labels=labels, right=False)
improved_counts = df_exp.groupby('TimeRange', observed=False).size().reset_index(name='Improved')

# === Merge and calculate improvement percentage ===
result = pd.merge(total_counts, improved_counts, on='TimeRange', how='left')
result['Improved'] = result['Improved'].fillna(0).astype(int)
result['Percent'] = (result['Improved'] / result['Total'] * 100).round(2)
result['TimeRange'] = pd.Categorical(result['TimeRange'], categories=labels, ordered=True)
result = result.sort_values('TimeRange').reset_index(drop=True)

# === Summary statistics ===
total_queries = result["Total"].sum()
total_improved = result["Improved"].sum()
overall_percent = round(100 * total_improved / total_queries, 2)

summary_text = (
    f"Total Info:\n"
    f"Optimized queries: {total_improved}\n"
    f"Total queries: {total_queries}\n"
    f"Optimization rate: {overall_percent}%"
)

# === Plot the bar chart ===
plt.figure(figsize=(14, 6))
x = range(len(result))

plt.bar(x, result['Total'], width=0.5, color=color_total, label='Total Queries')
plt.bar(x, result['Improved'], width=0.5, color=color_improved, label='Improved Queries')

for idx, (imp, total, perc) in enumerate(zip(result['Improved'], result['Total'], result['Percent'])):
    if imp > 0:
        plt.hlines(y=imp, xmin=idx - 0.25, xmax=idx + 0.25, colors=color_shadow, linewidth=2)
        plt.text(idx + 0.27, imp, f"{perc}%", ha='left', va='center',
                 fontsize=9, color=color_shadow, fontweight='bold')

for idx, (imp, total) in enumerate(zip(result['Improved'], result['Total'])):
    plt.text(idx, total + 2, str(int(total)), ha='center', fontsize=9, color='black')
    if imp > 0:
        plt.text(idx, imp + 2, str(int(imp)), ha='center', fontsize=9, color='black')

# Display summary text inside the plot area
plt.gca().text(
    0.99, 0.8, summary_text,
    transform=plt.gca().transAxes,
    ha='right', va='top',
    fontsize=10, fontweight='bold',
)

# Styling
plt.xlabel("Execution Time Range (ms)")
plt.xticks(ticks=x, labels=result["TimeRange"])
plt.ylabel("Number of Queries")
plt.title("Coverage by execution time range (SlabCity)")
plt.legend()
sns.despine()

# Save the figure
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/coverage_by_timerange.png")

print("Plot saved.")
