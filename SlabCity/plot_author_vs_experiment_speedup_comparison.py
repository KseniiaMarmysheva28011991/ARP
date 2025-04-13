import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# === Configuration ===
INPUT_FILE = "SlabCity_data_vs_experiment_data.csv"

# === Load data ===
df = pd.read_csv(INPUT_FILE)

# === First dataset: time_input / time_SC ===
df_1 = df[(df["time_input"] > 0) & (df["time_SC"] > 0)].copy()
df_1["speedup"] = df_1["time_input"] / df_1["time_SC"]
df_1["TaskNo"] = df_1["pid"]

avg_1 = df_1.groupby("TaskNo").agg(
    avg_speedup=("speedup", "mean"),
    count=("speedup", "count")
).reset_index()

# === Second dataset: time_input_experiment / time_SC_experiment ===
df_2 = df[(df["time_input_experiment"] > 0) & (df["time_SC_experiment"] > 0)].copy()
df_2["speedup_experiment"] = df_2["time_input_experiment"] / df_2["time_SC_experiment"]
df_2["TaskNo"] = df_2["pid"]

avg_2 = df_2.groupby("TaskNo").agg(
    avg_speedup_experiment=("speedup_experiment", "mean")
).reset_index()

# === Merge both summaries ===
merged = pd.merge(avg_1, avg_2, on="TaskNo", how="outer").fillna(1)
merged = merged.sort_values("avg_speedup", ascending=False).reset_index(drop=True)
merged["label"] = merged["TaskNo"].astype(int).astype(str) + " (n=" + merged["count"].astype(int).astype(str) + ")"

# === Plotting ===
bar_width = 0.4
indices = np.arange(len(merged))

plt.figure(figsize=(14, len(merged) * 0.4))
plt.barh(indices, merged["avg_speedup"], height=bar_width, label="SlabCity data", color="#A7AED2")
plt.barh(indices + bar_width, merged["avg_speedup_experiment"], height=bar_width, label="Experiment data", color="#C8CA76")

# Add value labels
for i, (val1, val2) in enumerate(zip(merged["avg_speedup"], merged["avg_speedup_experiment"])):
    plt.text(val1, i, f"{val1:.2f}×", va="center", ha="right", fontsize=7)
    plt.text(val2, i + bar_width, f"{val2:.2f}×", va="center", ha="right", fontsize=7)

# Formatting
plt.xscale("log")
plt.axvline(1, color="black", linestyle="--", linewidth=1)
plt.yticks(indices + bar_width / 2, merged["label"])
plt.xlabel("Average Speedup (log scale)")
plt.ylabel("TaskNo (with query count)")
plt.title("Average query speedup ratio by TaskNo: SlabCity data vs Experiment data (log scale)")
plt.legend()
plt.gca().invert_yaxis()
plt.tight_layout()

# Save the chart
os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/author_vs_experiments_speedup_comparison.png")

print("Plot saved.")
