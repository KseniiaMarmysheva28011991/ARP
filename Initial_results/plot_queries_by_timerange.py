"""
Script to visualize the distribution of SQL query execution times
from initial query results.

Output:
- Bar chart saved to 'plots/queries_by_timerange.png'
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Color for bars
COLOR_SUCCESS = "#7F86BC"

# Load query execution results
df = pd.read_csv("Initial_queries_raw_results.csv")

# Identify and exclude rows with execution errors
df["is_error"] = df["avg_pg_time"].str.lower().str.contains("error", na=False)
df_clean = df[~df["is_error"]].copy()

# Convert execution time to numeric
df_clean["avg_pg_time"] = pd.to_numeric(df_clean["avg_pg_time"], errors="coerce")
df_timeonly = df_clean.dropna(subset=["avg_pg_time"])

# Define time ranges (ms) and labels
bins = [0, 10, 20, 30, 40, 50, 100, 200, 300, 500, 1000, df_timeonly["avg_pg_time"].max() + 1]
labels = ["0–10", "10–20", "20–30", "30–40", "40–50",
          "50–100", "100–200", "200–300", "300–500", "500–1000", "1000+"]

# Categorize queries by execution time range
df_timeonly["time_range"] = pd.cut(df_timeonly["avg_pg_time"], bins=bins, labels=labels, right=False)

# Count queries in each time range
time_distribution = df_timeonly["time_range"].value_counts().sort_index()

# Plot bar chart
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(time_distribution.index.astype(str), time_distribution.values, color=COLOR_SUCCESS)

# Add count labels above each bar
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 2,
            f"{int(height)}", ha="center", va="bottom", fontsize=10)

# Total queries summary box
total_queries = df_timeonly.shape[0]
ax.text(0.99, 0.98, f"Total queries: {total_queries}",
        transform=ax.transAxes, ha='right', va='top', fontsize=12, fontweight='bold')

# Axis and title settings
ax.set_title("Number of Queries by Execution Time Ranges", fontsize=16, pad=15)
ax.set_xlabel("Execution Time Range (ms)", fontsize=12)
ax.set_ylabel("Number of Queries", fontsize=12)
ax.set_ylim(0, time_distribution.max() + 20)

plt.tight_layout()

# Save plot
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/queries_by_timerange.png", dpi=300)
