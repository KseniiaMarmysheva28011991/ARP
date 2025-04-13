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
df_filtered = df.dropna(subset=['cost_SC_experiments'])

# === Function to plot custom boxplot with labels ===
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

# === Calculate means and labels for cost ===
mean_cost_SC = df_filtered['cost_SC'].mean()
mean_cost_SC_exp = df_filtered['cost_SC_experiments'].mean()
mean_cost_input = df_filtered['cost_input'].mean()
mean_cost_input_exp = df_filtered['cost_input_experiments'].mean()

cost_labels_input = [
    f'SlabCity data\nMean: {mean_cost_input:.2f}',
    f'Experiment data\nMean: {mean_cost_input_exp:.2f}'
]
cost_labels_SC = [
    f'SlabCity data\nMean: {mean_cost_SC:.2f}',
    f'Experiment data\nMean: {mean_cost_SC_exp:.2f}'
]
cost_columns_input = ['cost_input', 'cost_input_experiments']
cost_columns_SC = ['cost_SC', 'cost_SC_experiments']
cost_palette_input = {cost_labels_input[0]: '#A7AED2', cost_labels_input[1]: '#C8CA76'}
cost_palette_SC = {cost_labels_SC[0]: '#A7AED2', cost_labels_SC[1]: '#C8CA76'}

# === Plot and save cost comparison ===
fig1, axes1 = plt.subplots(1, 2, figsize=(14, 6))  # Changed to horizontal layout
add_custom_boxplot(axes1[0], df_filtered, cost_columns_input, cost_labels_input,
                   'Initial query cost: SlabCity vs Experiment', 'Cost (log scale)', cost_palette_input)
add_custom_boxplot(axes1[1], df_filtered, cost_columns_SC, cost_labels_SC,
                   'Optimized query cost: SlabCity vs Experiment', 'Cost (log scale)', cost_palette_SC)
fig1.suptitle("Query Cost Comparison (log scale)", fontsize=14)
fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
fig1.savefig(os.path.join(output_dir, "author_vs_experiment_cost_comparison.png"), dpi=300)
plt.close(fig1)

print("Plot saved.")
