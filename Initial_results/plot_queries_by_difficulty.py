"""
Script to visualize the number of initial SQL queries by task difficulty,
including counts of successful and failed queries.

Output:
- Bar chart saved to 'plots/queries_by_difficulty.png'
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Define colors for visualization
COLORS = {
    "success": "#7F86BC",
    "error": "#F8D56F"
}

# Load query results
df = pd.read_csv("Initial_queries_raw_results.csv")

# Mark queries with execution errors
df["is_error"] = df["avg_pg_time"].str.lower().str.contains("error", na=False)

# Count successful and error queries per difficulty level
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
success_counts = (
    df[~df["is_error"]]["Difficulty"]
    .value_counts()
    .reindex(DIFFICULTY_LEVELS, fill_value=0)
)
error_counts = (
    df[df["is_error"]]["Difficulty"]
    .value_counts()
    .reindex(DIFFICULTY_LEVELS, fill_value=0)
)

# Plot bar chart
fig, ax = plt.subplots(figsize=(8, 6))
x = range(len(DIFFICULTY_LEVELS))

ax.bar(x, success_counts.values, label="Success", color=COLORS["success"])
ax.bar(x, error_counts.values, bottom=success_counts.values, label="Error", color=COLORS["error"])

# Add value labels on top of bars
for i in x:
    total = success_counts.iloc[i] + error_counts.iloc[i]
    ax.text(i, total + 5, str(total), ha='center', va='bottom', fontsize=11)

# Summary text box
total_queries = len(df)
success_queries = success_counts.sum()
error_queries = error_counts.sum()

summary_text = (
    f"Total queries: {total_queries}\n"
    f"Success: {success_queries}\n"
    f"Errors: {error_queries}"
)

ax.text(0.98, 0.98, summary_text, transform=ax.transAxes,
        ha='right', va='top', fontsize=11, fontweight='bold')

# Axis and title configuration
ax.set_title("Number of Queries by Task Difficulty", fontsize=16, pad=15)
ax.set_xlabel("Task Difficulty Level", fontsize=12)
ax.set_ylabel("Number of Queries", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(DIFFICULTY_LEVELS, fontsize=11)
ax.set_ylim(0, max(success_counts.values + error_counts.values) + 50)

ax.legend(fontsize=10)

plt.tight_layout()

# Save plot
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/queries_by_difficulty.png", dpi=300)
