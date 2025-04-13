import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Settings ===
sns.set(style="whitegrid")
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

# === Load and filter data ===
file_path = "SlabCity_data_vs_experiment_data.csv"
df = pd.read_csv(file_path)
df_filtered = df.dropna(subset=['time_SC_experiment'])

# === Function to draw custom boxplot with labels ===
def add_custom_boxplot(ax, data, columns, labels, title, ylabel, palette):
    subset = data[columns].copy()
    subset.columns = labels  # Rename columns for display

    sns.boxplot(data=subset, palette=palette, ax=ax)
    ax.set_yscale('log')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)

    for i, label in enumerate(labels):
        median = subset[label].median()
        ax.text(i, median, f'{median:.2f}', color='black', ha='center', va='bottom', fontsize=9, fontweight='bold')

# === Calculate means and labels for execution time ===
mean_time_SC = df_filtered['time_SC'].mean()
mean_time_SC_exp = df_filtered['time_SC_experiment'].mean()
mean_time_input = df_filtered['time_input'].mean()
mean_time_input_exp = df_filtered['time_input_experiment'].mean()

time_labels_input = [
    f'SlabCity data\nMean: {mean_time_input:.2f}',
    f'Experiment data\nMean: {mean_time_input_exp:.2f}'
]
time_labels_SC = [
    f'SlabCity data\nMean: {mean_time_SC:.2f}',
    f'Experiment data\nMean: {mean_time_SC_exp:.2f}'
]
time_columns_input = ['time_input', 'time_input_experiment']
time_columns_SC = ['time_SC', 'time_SC_experiment']
time_palette_input = {time_labels_input[0]: '#A7AED2', time_labels_input[1]: '#C8CA76'}
time_palette_SC = {time_labels_SC[0]: '#A7AED2', time_labels_SC[1]: '#C8CA76'}

# === Plot and save execution time comparison ===
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))  # 1 row, 2 columns
add_custom_boxplot(axes2[0], df_filtered, time_columns_input, time_labels_input,
                   'Initial execution time: SlabCity vs Experiment', 'Execution time (ms, log scale)', time_palette_input)
add_custom_boxplot(axes2[1], df_filtered, time_columns_SC, time_labels_SC,
                   'Optimized execution time: SlabCity vs Experiment', 'Execution time (ms, log scale)', time_palette_SC)
fig2.suptitle("Execution Time Comparison (log scale)", fontsize=14)
fig2.tight_layout(rect=[0, 0.03, 1, 0.95])
fig2.savefig(os.path.join(output_dir, "author_vs_experiment_time_comparison.png"), dpi=300)
plt.close(fig2)

print("Plot saved.")
