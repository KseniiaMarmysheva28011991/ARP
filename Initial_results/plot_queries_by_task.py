"""
Script to visualize the number of initial SQL queries per LeetCode task,
showing success and error counts per task.

Output:
- Bar chart saved to 'plots/queries_by_task.png'
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Load query results
df = pd.read_csv("Initial_queries_raw_results.csv")

# Identify queries with execution errors
df["is_error"] = df["avg_pg_time"].str.lower().str.contains("error", na=False)

# Aggregate success and error counts by TaskNo
summary = df.groupby("TaskNo").agg(
    total_queries=("TaskNo", "count"),
    error_queries=("is_error", "sum")
).reset_index()

summary["success_queries"] = summary["total_queries"] - summary["error_queries"]
summary["TaskNo"] = summary["TaskNo"].astype(int)
summary = summary.sort_values("TaskNo")

# Define colors for visualization
COLORS = {
    "success": "#7F86BC",
    "error": "#F8D56F"
}

# Plot bar chart
fig, ax = plt.subplots(figsize=(18, 8))
x = summary["TaskNo"].astype(str)
success = summary["success_queries"]
error = summary["error_queries"]

ax.bar(x, success, label="Success", color=COLORS["success"])
ax.bar(x, error, bottom=success, label="Error", color=COLORS["error"])

# Add counts as labels on bars
for i in range(len(x)):
    if success.iloc[i] > 0:
        ax.text(i, success.iloc[i] / 2, str(int(success.iloc[i])),
                ha='center', va='center', color='black', fontsize=10)
    if error.iloc[i] > 0:
        ax.text(i, success.iloc[i] + error.iloc[i] / 2, str(int(error.iloc[i])),
                ha='center', va='center', color='black', fontsize=10)

# Summary statistics text box
total_queries = df.shape[0]
error_queries = df["is_error"].sum()
success_queries = total_queries - error_queries

summary_text = (
    f"Total queries: {total_queries}\n"
    f"Success: {success_queries}\n"
    f"Errors: {error_queries}"
)

ax.text(0.99, 0.98, summary_text, transform=ax.transAxes,
        ha='right', va='top', fontsize=11, fontweight='bold')

# Axis and title configuration
ax.set_title("Number of Queries by LeetCode Task", fontsize=16, pad=15)
ax.set_xlabel("LeetCode Task No", fontsize=12)
ax.set_ylabel("Number of Queries", fontsize=12)
ax.set_ylim(0, 140)
ax.set_xticks(range(len(x)))
ax.set_xticklabels(x, rotation=90, fontsize=10)
ax.tick_params(axis='y', labelsize=10)

ax.legend(fontsize=10)

plt.tight_layout()

# Save plot
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/queries_by_task.png", dpi=300)
