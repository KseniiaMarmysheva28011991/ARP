import pandas as pd
import matplotlib.pyplot as plt
import os

# Colors
color_success = "#7F86BC"

# Load CSV
df = pd.read_csv("Initial_queries_raw_results.csv")

# Flag error rows
df["is_error"] = df["avg_pg_time"].str.lower().str.contains("error", na=False)

# Filter out rows with errors and convert execution time to numeric
df_clean = df[~df["is_error"]].copy()
df_clean["avg_pg_time"] = pd.to_numeric(df_clean["avg_pg_time"], errors="coerce")
df_timeonly = df_clean.dropna(subset=["avg_pg_time"])

# Define execution time intervals and labels
bins = [0, 10, 20, 30, 40, 50, 100, 200, 300, 500, 1000, df_timeonly["avg_pg_time"].max() + 1]
labels = [
    "0–10", "10–20", "20–30", "30–40", "40–50",
    "50–100", "100–200", "200–300", "300–500", "500–1000", "1000+"
]

# Assign each query to a time range
df_timeonly["time_range"] = pd.cut(df_timeonly["avg_pg_time"], bins=bins, labels=labels, right=False)

# Count number of queries in each range
time_distribution = df_timeonly["time_range"].value_counts().sort_index()

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(time_distribution.index.astype(str), time_distribution.values, color=color_success)

# Add value labels above bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 2, f"{int(height)}", ha="center", va="bottom", fontsize=9)

# Add total query count
ax.text(0.99, 0.98, f"Total No of queries: {df_timeonly.shape[0]}", transform=ax.transAxes,
        ha='right', va='top', fontsize=11, fontweight='bold')

# Axis titles and limits
ax.set_title("Number of Queries by Execution Time Ranges")
ax.set_xlabel("Execution Time Range (ms)")
ax.set_ylabel("Number of Queries")
ax.set_ylim(0, time_distribution.max() + 20)

# Save the plot
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/queries_by_timerange.png", dpi=300)
print("Plot saved.")
