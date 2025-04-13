import pandas as pd
import matplotlib.pyplot as plt
import os

# Colors
color_success = "#7F86BC"

# Load CSV
df = pd.read_csv("Initial_queries_raw_results.csv")

# Flag error rows
df["is_error"] = df["avg_pg_time"].str.lower().str.contains("error", na=False)

# Keep only successful queries
df_clean = df[~df["is_error"]].copy()

# Count queries by difficulty level (Easy, Medium, Hard)
difficulty_counts = df_clean["Difficulty"].value_counts().reindex(["Easy", "Medium", "Hard"], fill_value=0)

# Plot
fig, ax = plt.subplots(figsize=(6, 6))
bars = ax.bar(difficulty_counts.index, difficulty_counts.values, color=color_success)

# Add value labels above bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 5, f"{int(height)}", ha='center', va='bottom', fontsize=10)

# Add summary in top-right corner
ax.text(0.99, 0.98, f"Total No of queries: {df_clean.shape[0]}", transform=ax.transAxes,
        ha='right', va='top', fontsize=11, fontweight='bold')

# Axis titles and limits
ax.set_title("Number of Queries by Task Difficulty")
ax.set_xlabel("Task Difficulty Level (LeetCode)")
ax.set_ylabel("Number of Queries")
ax.set_ylim(0, max(difficulty_counts.values) + 50)

# Save the plot
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/queries_by_difficulty.png", dpi=300)
print("Plot saved.")
