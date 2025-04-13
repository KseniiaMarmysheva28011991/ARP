import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# === Configuration ===
INPUT_FILE = "SC_vs_Initial_queries_experiment_data.csv"

# Load and filter data
df = pd.read_csv(INPUT_FILE)

# Exclude rows where equivalent_query = 'FALSE'
df = df[df["equivalent_query"].astype(str).str.upper() == "TRUE"]

# Calculate speedup ratio
df["times_faster"] = df["avg_pg_time_initial"] / df["avg_pg_time_sc"]
df = df[np.isfinite(df["times_faster"])]
df = df.dropna(subset=["times_faster", "TaskNo_initial", "ResponseId_initial"])

# Group by TaskNo (use the first difficulty value, as it is the same for all rows in a TaskNo group)
task_stats = df.groupby("TaskNo_initial").agg(
    avg_speedup=("times_faster", "mean"),
    count=("times_faster", "count"),
    difficulty=("Difficulty_sc", "first")
).reset_index()

# Set bar colors and labels
task_stats["color"] = task_stats["avg_speedup"].apply(lambda x: "#C8CA76" if x >= 1 else "#F6C83F")
task_stats["label"] = (
    task_stats["TaskNo_initial"].astype(int).astype(str)
    + " (" + task_stats["difficulty"].astype(str)
    + ", n=" + task_stats["count"].astype(str) + ")"
)

# Sort by average speedup (descending)
task_stats = task_stats.sort_values(by="avg_speedup", ascending=False).reset_index(drop=True)

# Plotting
plt.figure(figsize=(14, len(task_stats) * 0.3))
plt.barh(
    y=range(len(task_stats)),
    width=task_stats["avg_speedup"],
    color=task_stats["color"]
)

# Add text labels for each bar
for i, val in enumerate(task_stats["avg_speedup"]):
    plt.text(val, i, f"{val:.2f}×", va="center", ha="left", fontsize=8)

plt.xscale("log")
plt.gca().invert_yaxis()
plt.axvline(1, color="black", linestyle="--", linewidth=1)
plt.text(1.05, -0.5, "1×baseline (no speedup)", va="bottom", ha="left", fontsize=9, color="black")
plt.yticks(range(len(task_stats)), task_stats["label"])
plt.xlabel("Average Speedup (log scale)")
plt.ylabel("TaskNo (difficulty, query count)")
plt.title("Average Query Speedup by TaskNo (Initial vs SlabCity, Log Scale)")
plt.tight_layout()

# Save the chart
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/speedup_ratio_by_task.png")

print("Plot saved.")
