import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from math import ceil, floor, log2

from plot_setup import *

def plot():
    NUM_BANKS = 64
    NUM_ROWS = 128 * 1024
    PAGE_SIZE = 16 * 1024
    def get_graphene_bits(tRH):
        tREFW = 32000000
        tRC = 46
        k = 1
        num_table_entries = int(ceil((tREFW/tRC)/tRH * ((k+1)/(k)) - 1)) * NUM_BANKS
        num_row_bits = int(ceil(log2(NUM_ROWS)))
        num_trh_bits = int(ceil(log2(tRH))) + 1
        num_bits = num_table_entries * (num_row_bits + num_trh_bits)
        return num_bits

    def get_hydra_cpu_bits(tRH):
        tH = tRH // 2
        num_gcc_entries = 32 * 1024
        num_rcc_entries = 8 * 1024
        gcc_thresh = int(tH * 4/5)
        num_gcc_th_bits = int(ceil(log2(gcc_thresh))) + 1
        num_rcc_pad_bits = 16
        num_rcc_ctr_bits = int(ceil(log2(tH))) + 1
        return num_gcc_entries * num_gcc_th_bits + num_rcc_entries * (num_rcc_pad_bits + num_rcc_ctr_bits)

    def get_hydra_dram_bits(tRH):
        tH = tRH // 2
        num_th_bits = int(ceil(log2(tH))) + 1
        num_bits = num_th_bits * NUM_ROWS * NUM_BANKS
        return num_bits

    def get_prac_bits(tRH):
        num_trh_bits = int(ceil(log2(tRH))) + 1
        num_bits = num_trh_bits * NUM_ROWS * NUM_BANKS
        return num_bits

    def get_rfm_bits(tRH):
        num_trh_bits = int(ceil(log2(tRH))) + 1
        num_bits = num_trh_bits * NUM_BANKS
        return num_bits

    def get_chronus_bits(tRH):
        num_trh_bits = int(ceil(log2(tRH))) + 1
        num_bits = num_trh_bits * NUM_ROWS * NUM_BANKS
        return num_bits

    fig, ax = plt.subplots(1,1, figsize=(6, 1.8))
    ax.set_ylabel('Storage Overhead\n(MiB)', fontsize=10)
    ax.set_xlabel('RowHammer Threshold ($N_{RH}$)', fontsize=10)
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    ax.grid(axis='x', linestyle='--', linewidth=0.5, color='gray', zorder=0)

    ax.set_axisbelow(True)

    spec_mits = [("Graphene", get_graphene_bits), ("PRAC", get_prac_bits),\
                ("PRFM", get_rfm_bits), ("PRAC+PRFM", lambda x: get_prac_bits(x)),\
                ("Hydra", get_hydra_dram_bits), ("Chronus", get_chronus_bits)]

    storage_df = pd.DataFrame(columns=['configstr', 'tRH', 'storage_overhead'])

    for mit, fun in spec_mits:
        for tRH in [1024, 512, 256, 128, 64, 32, 20]:
            storage_df.loc[len(storage_df)] = [mit, tRH, fun(tRH) / 8 / 1024 / 1024]

    storage_df["itRH"] = 1 / storage_df["tRH"]

    hue_order = ["Chronus", "Graphene", "Hydra", "PRAC", "PRFM"]

    colors = sns.color_palette("pastel", len(["Chronus", "Chronus+PB", "Graphene", "Hydra", "PRFM", "PRAC-4", "PARA"]))
    sns.barplot(
        x='itRH', 
        y='storage_overhead', 
        hue="configstr",
        hue_order=hue_order,
        data=storage_df,
        ax=ax, 
        palette=[colors[0], colors[2], colors[3], colors[5], colors[4]],
        linewidth=0.5,
        capsize=0.1,
        errwidth=0.5,
        errcolor='black',
        edgecolor='black',
        width=0.5
    )

    ax.set_xticklabels([f"{int(x)}" for x in reversed(sorted(storage_df.tRH.unique()))])
    ax.set_xlim([-0.5, 6.5])

    handles, labels = ax.get_legend_handles_labels()

    num_bars_per_group = len(hue_order)
    sorted_bars = sorted(ax.patches, key=lambda x: x.get_x())
    nrh_grp_lookup = sorted(storage_df["tRH"].unique(), reverse=True)

    bar_idx = 0
    for i, bar in enumerate(sorted_bars):
        if bar.get_width() == 0 and bar.get_height() == 0:
            continue
        mit_idx = bar_idx % num_bars_per_group
        mit_grp = bar_idx // num_bars_per_group
        mit_name = hue_order[mit_idx]
        mit_bits = 0
        mit_trh = nrh_grp_lookup[mit_grp]
        for name, fun in spec_mits:
            if name == mit_name:
                mit_bits = fun(mit_trh)
        mit_bytes = mit_bits / 8 / 1024 / 1024
        if mit_name == "PRFM":
            anno = ax.annotate(
                f"{int(ceil(get_rfm_bits(mit_trh)/8))}B",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() + 0.03),
                xycoords='data',
                xytext=(7.7, 15),
                textcoords='offset points', 
                arrowprops=dict(arrowstyle="->", relpos=(0.5, 0.5), color='red'),
                ha='center',
                va='bottom',
                fontsize=11,
                color='red',
            )
        bar_idx += 1

    new_labels = [label if label != 'PRAC-Ideal' else 'PRAC-Optimistic' for label in labels]
    ax.legend(handles=handles, labels=new_labels, loc='center', ncol=5, fancybox=True, shadow=False,\
            handletextpad=0.35, columnspacing=0.45, bbox_to_anchor=(0.5, 1.15), fontsize=10)

    ax.set_yticks([i*1.5 for i in range(11)])
    ax.set_yticklabels(["0", "", "3", "", "6", "", "9", "", "12", "", "15"], fontsize=10)
    ax.set_ylim([0, 12.5])

    fig.savefig(f'{PLOT_DIR}/figure11.pdf', bbox_inches='tight')

if __name__ == "__main__":
    plot()