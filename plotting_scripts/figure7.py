import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_setup import *

MAIN_PERF = "norm_weighted_speedup"
SHORT_NAME = "BH"
MITIGATION_LIST = ["Chronus", "Chronus+PB", "Graphene", "Hydra", "PRFM", "PRAC-4", "PARA"]

TRACE_COMBINATION_NAME = "hpcasingle"
TRACE_COMBINATION_FILE = f"{TRACE_COMBINATION_DIR}/{TRACE_COMBINATION_NAME}.mix"
CSV_DIR = f"{RESULT_DIR}/{TRACE_COMBINATION_NAME}/_csvs"

def plot(data_path, mpki_path):
    df = pd.read_csv(data_path)
    wldf = pd.read_csv(TRACE_COMBINATION_FILE, sep=',', header=None, names=['trace', 'w', 'benchmark'])
    mpkidf = pd.read_csv(mpki_path)
    mpkidf = mpkidf[mpkidf.benchmark != 'gups']
    mpkidf = mpkidf.sort_values(by=['MPKI'], ascending=False)
    mpkidf = mpkidf[mpkidf.benchmark != '433.milc'] 
    mpkidf = mpkidf.head(13)
    
    UPPER_TRH, LOWER_TRH = 1024, 32

    df = df.merge(wldf, on='trace', how='left')
    df = df.merge(mpkidf, on='benchmark', how='inner')
    df = df.sort_values(by=['MPKI'], ascending=False)

    base_df = df[(df.mitigation == "Dummy")]
    df = df.merge(base_df, on=['benchmark'], how='left', suffixes=('', '_base'))
    df['speedup'] = df['ipc_0'] / df['ipc_0_base']
    df["mitigation"] = df["mitigation"].replace({
        "Dummy": "No Mitigation",
        "RFM": "PRFM",
        "PRAC-RFM": "PRAC+PRFM",
        "TOPRAC": "Chronus",
        "PRAC-Ideal": "Chronus+PB"
    })
    df["configstr"] = df["mitigation"]

    gmeans = []
    for (configstr, tRH), subdf in df.groupby(['configstr', 'tRH']):
        gmeans.append({
            'benchmark': 'geomean',
            'MPKI': subdf.MPKI.mean(),
            'configstr': configstr,
            'tRH': tRH,
            'speedup': gmean(subdf.speedup)
        })
    gdf = pd.DataFrame(gmeans)

    df = pd.concat([df[['benchmark', 'configstr', 'tRH', 'MPKI', 'speedup']], gdf], ignore_index=True)

    correct = df[(df.configstr == "Chronus+PB") & (df.tRH == 256)]
    df = df[(df.configstr != "Chronus+PB") | (df.tRH <= 256)]
    for tRH in [512, 1024]:
        correct["tRH"] = tRH
        df = pd.concat([df, correct], ignore_index=True)

    fig, axes = plt.subplots(2, 1, figsize=(6, 4), sharex=True)
    upper_ax = axes[0]
    upper_ax.add_artist(plt.Rectangle((6.5, 0.2), 5.5, 1.0, fill=True, edgecolor="black", facecolor='#e5e5e5', linewidth=1, linestyle='-',  zorder=0))
    upper_ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    upper_ax.set_axisbelow(True)

    sns.barplot(
        x='benchmark', y='speedup', data=df[(df.tRH==UPPER_TRH)],
        hue='configstr', 
        hue_order=MITIGATION_LIST,
        linestyle='-',
        edgecolor='black',
        palette="pastel",
        ax=upper_ax
    )

    upper_ax.axhline(1, color='black', linestyle='--', linewidth=1)
    upper_ax.set_ylabel('Norm. Speedup')
    upper_ax.legend(loc='center',  ncol=4, fancybox=True, shadow=False, handletextpad=0.5, columnspacing=0.75, bbox_to_anchor=(0.5, 1.30)),
    upper_ax.set_ylim(0.2, 1.2)
    upper_ax.set_yticks([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
    upper_ax.set_yticklabels(['0.2', '', '0.4', '', '0.6', '', '0.8', '', '1.0', '', '1.2'])

    lower_ax = axes[1]
    lower_ax.add_artist(plt.Rectangle((6.5, 0.2), 5.5, 1.0, fill=True, edgecolor="black", facecolor='#e5e5e5', linewidth=1, linestyle='-',  zorder=0))
    lower_ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    lower_ax.set_axisbelow(True)
    lower_ax.text(0, 0, "")

    sns.barplot(
        x='benchmark', y='speedup', data=df[(df.tRH==LOWER_TRH)],
        hue='configstr', 
        hue_order=MITIGATION_LIST,
        linestyle='-',
        edgecolor='black',
        palette="pastel",
        ax=lower_ax
    )

    lower_ax.set_xlabel('Benchmarks')
    lower_ax.axhline(1, color='black', linestyle='--', linewidth=1)
    lower_ax.set_ylabel('Norm. Speedup')
    lower_ax.set_xlabel(None)
    if lower_ax.get_legend():
        lower_ax.get_legend().remove()
    lower_ax.set_ylim(0.2, 1.2)
    lower_ax.set_yticks([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
    lower_ax.set_yticklabels(['0.2', '', '0.4', '', '0.6', '', '0.8', '', '1.0', '', '1.2'])
    lower_ax.set_xticklabels(lower_ax.get_xticklabels(), rotation=30, horizontalalignment='center')

    upper_ax.text(0.01, 0.96, f"$N_{{RH}}$ = {UPPER_TRH}", ha="left", va="top", transform=upper_ax.transAxes)
    lower_ax.text(0.01, 0.96, f"$N_{{RH}}$ = {LOWER_TRH}", ha="left", va="top", transform=lower_ax.transAxes)

    fig.tight_layout()
    fig.savefig(f'{PLOT_DIR}/figure7.pdf', bbox_inches='tight')

if __name__ == "__main__":
    plot(f"{CSV_DIR}/merged.csv", f"{TRACE_DIR}/mpki.csv")
