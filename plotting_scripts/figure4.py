import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_setup import *

MAIN_PERF = "norm_weighted_speedup"
SHORT_NAME = "BH"
NUM_CORES = 4
MITIGATION_LIST = ["PRAC-4", "PRAC-2", "PRAC-1", "PRAC+PRFM", "PRFM"]

TRACE_COMBINATION_NAME = "hpcabenign"
TRACE_COMBINATION_FILE = f"{TRACE_COMBINATION_DIR}/{TRACE_COMBINATION_NAME}.mix"
CSV_DIR = f"{RESULT_DIR}/{TRACE_COMBINATION_NAME}/_csvs"

def plot(df):
    fig, ax = plt.subplots(1,1, figsize=(6, 1.8))
    plot_df = df[(df.tRH > 0)].copy()
    plot_df["itRH"] = 1 / plot_df["tRH"]
    hue_order = MITIGATION_LIST
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    ax.grid(axis='x', linestyle='--', linewidth=0.5, color='gray', zorder=0)

    ax.set_axisbelow(True)

    plot_df = plot_df[(plot_df["norm_weighted_speedup"] >= 0)]
    plot_df["norm_weighted_slowdown"] = 1 - plot_df["norm_weighted_speedup"]

    sns.barplot(
        x='itRH', 
        y='norm_weighted_speedup', 
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

    ax.axhline(1, color='black', linestyle='--', linewidth=1)
    ax.set_ylabel('Normalized\nWeighted Speedup', fontsize=10)
    ax.set_xlabel('RowHammer Threshold ($N_{RH}$)', fontsize=10)
    items = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    major = items[::2]
    minor = items[1:][::2]
    ax.set_yticks(major)
    ax.set_yticks(minor, minor=True)
    ax.set_yticklabels([str(item) for item in major], fontsize=10)
    ax.set_xlim([-0.5, 6.5])
    ax.set_ylim([0, 1.2])

    handles, labels = ax.get_legend_handles_labels()
    num_bars_per_group = len(MITIGATION_LIST)
    sorted_bars = sorted(ax.patches, key=lambda x: x.get_x())
    nrh_grp_lookup = sorted(plot_df["tRH"].unique(), reverse=True)

    bar_idx = 0
    for i, bar in enumerate(sorted_bars):
        if bar.get_width() == 0 and bar.get_height() == 0:
            continue
        mit_idx = bar_idx % num_bars_per_group
        mit_grp = bar_idx // num_bars_per_group
        mit_name = MITIGATION_LIST[mit_idx]
        mit_bits = 0
        mit_trh = nrh_grp_lookup[mit_grp]
        bar_idx += 1
        if mit_name == "PRAC-1" and mit_trh == 32:
            ax.annotate("not\nsafe", (bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() + 0.03), xytext=(0, 37),\
                arrowprops=dict(color='red', shrink=0.05, width=1, headwidth=3, headlength=3),\
                textcoords='offset points', ha='center', va='bottom', fontsize=10, color='red')
            bar.set_edgecolor('red')
            bar.set_linewidth(1)
            bar.set_zorder(5)
        if mit_name in ["PRAC-1", "PRAC-2"] and mit_trh == 20:
            bar.set_edgecolor('red')
            bar.set_linewidth(1)
            bar.set_zorder(5)

    new_labels = [label if label != 'PRAC-Ideal' else 'PRAC-Optimistic' for label in labels]
    ax.legend(handles=handles, labels=new_labels, loc='center', ncol=5, fancybox=True, shadow=False,
            handletextpad=0.35, columnspacing=0.45, bbox_to_anchor=(0.5, 1.15), fontsize=10)

    fig.savefig(f'{PLOT_DIR}/figure4.pdf', bbox_inches='tight')

if __name__ == "__main__":
    df = general_df_setup(CSV_DIR, TRACE_DIR, TRACE_COMBINATION_FILE, NUM_CORES)
    plot(df)