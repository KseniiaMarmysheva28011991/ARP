import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Colors
color_total = "#D5D6E8"
color_improved = "#B7B745"
color_shadow = "#505FA2"

# Load datasets
df_total = pd.read_csv("Initial_queries_raw_results.csv")
df_exp = pd.read_csv("SC_vs_Initial_queries_experiment_data.csv")

# Process total (all queries)
df_total = df_total.dropna(subset=['avg_pg_time'])
total_counts = df_total.groupby("TaskNo")["ResponseId"].count()

# Process improved queries (only statistically significant and equivalent ones)
df_exp = df_exp.dropna(subset=["avg_pg_time_initial", "avg_pg_time_sc"])
df_exp = df_exp[df_exp["equivalent_query"].astype(str).str.upper() == "TRUE"]
df_exp = df_exp[df_exp["performance_difference"] == "significant"]
df_exp = df_exp[df_exp["avg_pg_time_sc"] < df_exp["avg_pg_time_initial"]]
improved_counts = df_exp.groupby("TaskNo_initial")["ResponseId_initial"].count()

# Merge counts
result = pd.DataFrame({
    "Total": total_counts,
    "Improved": improved_counts
}).fillna(0).astype(int)

# Summary statistics
total_queries = result["Total"].sum()
total_improved = result["Improved"].sum()
overall_percent = round(100 * total_improved / total_queries, 2)
summary_text = (
    f"Total Info:\n"
    f"Optimized queries: {total_improved}\n"
    f"Total queries: {total_queries}\n"
    f"Optimization rate: {overall_percent}%"
)

# Plotting the chart
plt.figure(figsize=(18, 6))
x = list(range(len(result)))
task_labels = result.index.astype(str)

plt.bar(x, result["Total"], width=0.5, label='Total number of queries', color=color_total)
plt.bar(x, result["Improved"], width=0.5, label='Statistically optimized queries', color=color_improved)

# Add percentage annotations and top lines
for idx, (imp, total) in enumerate(zip(result["Improved"], result["Total"])):
    if total > 0 and imp > 0:
        xpos = x[idx]
        plt.hlines(y=imp, xmin=xpos - 0.25, xmax=xpos + 0.2, colors=color_shadow, linewidth=2)
        percent = round(100 * imp / total)
        plt.text(xpos + 0.22, imp, f"{percent}%", ha='left', va='center',
                 fontsize=8, color=color_shadow, fontweight='bold')

# Add value labels above bars
for idx, val in enumerate(result["Total"]):
    if val > 0:
        plt.text(x[idx], val + 2.5, str(val), ha='center', va='bottom', fontsize=9, color='black')

for idx, val in enumerate(result["Improved"]):
    if val > 0:
        plt.text(x[idx], val + 2.5, str(val), ha='center', va='bottom', fontsize=9, color='black')

# Summary block on the right
plt.text(x=max(x) + 0.5, y=max(result["Total"]) + 5,
         s=summary_text,
         ha='right', va='top',
         fontsize=10, color='black', fontweight='bold')

# Styling
plt.xlabel("TaskNo")
plt.xticks(ticks=x, labels=task_labels, rotation=90)
plt.ylabel("Number of queries")
plt.title("Coverage by TaskNo")
plt.legend()
sns.despine()

# Save the chart
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/coverage_by_task.png")

print("Plot saved.'")
