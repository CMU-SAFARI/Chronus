import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_setup import *

MAIN_PERF = "norm_weighted_speedup"
NUM_CORES = 4
MITIGATION_LIST = ["Chronus", "Chronus+PB", "Graphene", "Hydra", "PRFM", "PRAC-4", "PARA"]

TRACE_COMBINATION_NAME = "hpcabenign"
TRACE_COMBINATION_FILE = f"{TRACE_COMBINATION_DIR}/{TRACE_COMBINATION_NAME}.mix"
CSV_DIR = f"{RESULT_DIR}/{TRACE_COMBINATION_NAME}/_csvs"

def plot(df):
    fig, ax = plt.subplots(1, 1, figsize=(6, 1.8))

    plot_df = df[(df.tRH > 0)].copy()
    plot_df["itRH"] = 1 / plot_df["tRH"]

    hue_order = MITIGATION_LIST

    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    ax.grid(axis='x', linestyle='--', linewidth=0.5, color='gray', zorder=0)

    ax.set_axisbelow(True)

    sns.barplot(
        x='itRH', 
        y='norm_energy', 
        hue="configstr",
        hue_order=hue_order,
        data=plot_df,
        ax=ax, 
        palette="pastel",
        linewidth=0.5,
        capsize=0.1,
        errwidth=0.5,
        errcolor='black',
        edgecolor='black',
        width=0.9
    )

    ax.set_xticklabels([f"{int(x)}" for x in reversed(sorted(plot_df.tRH.unique()))])

    ax.axhline(1, color='black', linestyle='--', linewidth=1, zorder=10)
    ax.set_ylabel('Normalized\nEnergy Consumption', fontsize=10)
    ax.set_xlabel('RowHammer Threshold ($N_{RH}$)', fontsize=10)
    handles, labels = ax.get_legend_handles_labels()
    new_labels = [label if label != 'PRAC-Ideal' else 'PRAC-Optimistic' for label in labels]
    ax.legend(handles=handles, labels=new_labels, loc='center',  ncol=4, fancybox=True, shadow=False,
              handletextpad=0.5, columnspacing=0.75, bbox_to_anchor=(0.50, 1.25), fontsize=10)
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.set_yticks([1, 3, 5, 7, 9], minor=True)
    ax.set_yticklabels(["0", "2", "4", "6", "8", "10"], fontsize=10)
    ax.set_ylim([0, 10])

    fig.savefig(f'{PLOT_DIR}/figure10.pdf', bbox_inches='tight')

if __name__ == "__main__":
    df = general_df_setup(CSV_DIR, TRACE_DIR, TRACE_COMBINATION_FILE, NUM_CORES)
    plot(df)