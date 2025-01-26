import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_setup import *

MAIN_PERF = "norm_weighted_speedup"
NUM_CORES = 4
MITIGATION_LIST = ["Chronus", "Chronus-PB", "PRAC-4", "Graphene", "Hydra", "PRFM", "PARA"]

TRACE_COMBINATION_NAME = "hpcabenign"
TRACE_COMBINATION_FILE = f"{TRACE_COMBINATION_DIR}/{TRACE_COMBINATION_NAME}.mix"
CSV_DIR = f"{RESULT_DIR}/{TRACE_COMBINATION_NAME}/_csvs"

def plot(df):
    fig, ax = plt.subplots(1,1, figsize=(6, 1.5))
    plot_df = df.copy()
    plot_df["itRH"] = 1 / plot_df["tRH"]
    TRH = 32

    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)

    ax.set_axisbelow(True)

    hue_order = MITIGATION_LIST
    x_order = ['HHHH', 'HHMM', 'HHLL', 'MMMM', 'MMLL', 'LLLL', 'geomean\n(60)']

    ax = sns.barplot(
        x='label',
        y='norm_weighted_speedup',
        hue="configstr", 
        hue_order=hue_order,
        data=plot_df[plot_df.tRH == TRH],
        ax=ax, 
        order=x_order,
        palette="pastel",
        ci=68,
        linewidth=0.5,
        capsize=0.1,
        errwidth=0.5,
        errcolor='black',
        edgecolor='black',
        width=0.8
    )

    ax.axhline(1, color='black', linestyle='--', linewidth=1)
    ax.set_ylabel('Normalized\nWeighted Speedup', fontsize=10)
    ax.set_xlabel('Workload Memory Intensity', fontsize=10)
    items = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    major = items[::2]
    minor = items[1:][::2]
    ax.set_yticks(major)
    ax.set_yticks(minor, minor=True)
    ax.set_yticklabels([str(item) for item in major], fontsize=10)
    ax.set_xlim([-0.5, 6.5])
    ax.set_ylim([0, 1.2])

    handles, labels = ax.get_legend_handles_labels()

    new_labels = [label if label != 'PRAC-Ideal' else 'PRAC-Optimistic' for label in labels]
    num_columns = 4
    reorder = lambda l, nc: sum((l[i::nc] for i in range(nc)), [])
    ax.legend(handles=reorder(handles, num_columns), labels=reorder(new_labels, num_columns), loc='center', ncol=num_columns, fancybox=True, shadow=False,\
            handletextpad=0.35, columnspacing=0.45, bbox_to_anchor=(0.5, 1.25), fontsize=10)

    ax.add_artist(plt.Rectangle((5.5, 0), 6, 1.3, fill=True, edgecolor="black", facecolor='#e5e5e5', linewidth=1, linestyle='-',  zorder=0))

    fig.savefig(f'{PLOT_DIR}/figure9.pdf', bbox_inches='tight')

if __name__ == "__main__":
    df = general_df_setup(CSV_DIR, TRACE_DIR, TRACE_COMBINATION_FILE, NUM_CORES)
    plot(df)