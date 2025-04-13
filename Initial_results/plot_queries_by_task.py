
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load CSV
df = pd.read_csv("Initial_queries_raw_results.csv")

# Mark errors
df["is_error"] = df["avg_pg_time"].str.lower().str.contains("error", na=False)

# Group by TaskNo and calculate counts
summary = df.groupby("TaskNo").agg(
    total_queries=("TaskNo", "count"),
    error_queries=("is_error", "sum")
).reset_index()

summary["success_queries"] = summary["total_queries"] - summary["error_queries"]
summary["TaskNo"] = summary["TaskNo"].astype(int)
summary = summary.sort_values("TaskNo")

colors = {
    "success": "#7F86BC",
    "error": "#F8D56F"
}

fig, ax = plt.subplots(figsize=(18, 8))

x = summary["TaskNo"].astype(str)
success = summary["success_queries"]
error = summary["error_queries"]

bars_success = ax.bar(x, success, label="Success", color=colors["success"])
bars_error = ax.bar(x, error, bottom=success, label="Error", color=colors["error"])

# Add text labels to each bar
for i in range(len(x)):
    if success[i] > 0:
        ax.text(i, success[i] / 2, str(int(success[i])), ha='center', va='center', color='black', fontsize=8)
    if error[i] > 0:
        ax.text(i, success[i] + error[i] / 2, str(int(error[i])), ha='center', va='center', color='black', fontsize=8)

# Add summary text
total_queries = df.shape[0]
error_queries = df["is_error"].sum()
success_queries = total_queries - error_queries

summary_text = (
    f"Total No of queries: {total_queries}\n"
    f"Success queries: {success_queries}\n"
    f"Errors queries: {error_queries}"
)

ax.text(0.99, 0.98, summary_text, transform=ax.transAxes,
        ha='right', va='top', fontsize=11, fontweight='bold')

ax.set_title("Number of Queries by LeetCode Task")
ax.set_xlabel("LeetCode Task No")
ax.set_ylabel("Number of Queries")
ax.set_ylim(0, 140)
ax.set_xticks(range(len(x)))
ax.set_xticklabels(x, rotation=90)
ax.legend()
plt.tight_layout()
plt.savefig("plots/queries_by_task.png", dpi=300)
print("Plot saved.")
