import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Colors ===
color_total = "#D5D6E8"
color_improved = "#B7B745"
color_shadow = "#505FA2"

# === Load data ===
df_total = pd.read_csv("Initial_queries_raw_results.csv")
df_exp = pd.read_csv("SC_vs_Initial_queries_experiment_data.csv")

# === Processing total queries (all initial queries) ===
df_total = df_total.dropna(subset=['avg_pg_time'])
total_by_difficulty = df_total.groupby("Difficulty")["ResponseId"].count().reset_index(name="Total")

# === Processing improved queries (only statistically significant and equivalent ones) ===
df_exp = df_exp.dropna(subset=["avg_pg_time_initial", "avg_pg_time_sc"])
df_exp = df_exp[df_exp["equivalent_query"].astype(str).str.upper() == "TRUE"]
df_exp = df_exp[df_exp["performance_difference"] == "significant"]
df_exp = df_exp[df_exp["avg_pg_time_sc"] < df_exp["avg_pg_time_initial"]]

# Grouping by difficulty level
improved_by_difficulty = df_exp.groupby("Difficulty_sc")["ResponseId_sc"].count().reset_index(name="Improved")

# === Merge and calculate improvement percentage ===
result = pd.merge(total_by_difficulty, improved_by_difficulty, left_on="Difficulty", right_on="Difficulty_sc", how='left')
result = result.drop(columns=["Difficulty_sc"]).fillna(0)
result["Improved"] = result["Improved"].astype(int)
result["Percent"] = (result["Improved"] / result["Total"] * 100).round(2)
result = result.sort_values(by="Total", ascending=False).reset_index(drop=True)

# === Summary information ===
total_queries = result["Total"].sum()
total_improved = result["Improved"].sum()
overall_percent = round(100 * total_improved / total_queries, 2)

summary_text = (
    f"Total Info:\n"
    f"Optimized queries: {total_improved}\n"
    f"Total queries: {total_queries}\n"
    f"Optimization rate: {overall_percent}%"
)

# === Plotting the chart ===
plt.figure(figsize=(14, 6))
x = range(len(result))

# Bars
plt.bar(x, result["Total"], width=0.5, color=color_total, label="Total Queries")
plt.bar(x, result["Improved"], width=0.5, color=color_improved, label="Improved Queries")

# Horizontal lines and percentage annotations
for idx, (imp, total, perc) in enumerate(zip(result["Improved"], result["Total"], result["Percent"])):
    if imp > 0:
        plt.hlines(y=imp, xmin=idx - 0.25, xmax=idx + 0.25, colors=color_shadow, linewidth=2)
        plt.text(idx + 0.28, imp, f"{perc}%", ha='left', va='center',
                 fontsize=9, color=color_shadow, fontweight='bold')

# Bar labels
for idx, (imp, total) in enumerate(zip(result["Improved"], result["Total"])):
    plt.text(idx, total + 4, str(int(total)), ha='center', fontsize=9, color='black')
    if imp > 0:
        plt.text(idx, imp + 4, str(int(imp)), ha='center', fontsize=9, color='black')

# Summary block inside the plot (same coordinates as legend)
plt.gca().text(
    0.99, 0.8, summary_text,
    transform=plt.gca().transAxes,
    ha='right', va='top',
    fontsize=10, fontweight='bold',
)

# Styling
plt.xlabel("Difficulty")
plt.ylabel("Number of Queries")
plt.xticks(ticks=x, labels=result["Difficulty"])
plt.title("Coverage by difficulty (SlabCity)")
plt.legend()
sns.despine()

# Save the plot
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/coverage_by_difficulty.png")

print("Plot saved.png'")
