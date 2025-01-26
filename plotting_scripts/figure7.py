import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_setup import *

MAIN_PERF = "norm_weighted_speedup"
SHORT_NAME = "BH"
MITIGATION_LIST = ["Chronus", "Chronus-PB", "PRAC-4", "Graphene", "Hydra", "PRFM", "PARA"]

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
    mpkidf = mpkidf[mpkidf.benchmark != '450.soplex'] 
    mpkidf = mpkidf.head(26)
    
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
        "PRAC-Ideal": "Chronus-PB",
        "Chronus+PB": "Chronus-PB"
    })
    df["configstr"] = df["mitigation"]

    geo_df = pd.read_csv(data_path)
    geo_wldf = pd.read_csv(TRACE_COMBINATION_FILE, sep=',', header=None, names=['trace', 'w', 'benchmark'])
    geo_mpkidf = pd.read_csv(mpki_path)
    geo_df = geo_df.merge(geo_wldf, on='trace', how='left')
    geo_df = geo_df.merge(geo_mpkidf, on='benchmark', how='inner')
    geo_df = geo_df.sort_values(by=['MPKI'], ascending=False)
    base_df = geo_df[(geo_df.mitigation == "Dummy")]
    geo_df = geo_df.merge(base_df, on=['benchmark'], how='left', suffixes=('', '_base'))
    geo_df['speedup'] = geo_df['ipc_0'] / geo_df['ipc_0_base']
    geo_df["mitigation"] = geo_df["mitigation"].replace({
        "Dummy": "No Mitigation",
        "RFM": "PRFM",
        "PRAC-RFM": "PRAC+PRFM",
        "TOPRAC": "Chronus",
        "PRAC-Ideal": "Chronus-PB",
        "Chronus+PB": "Chronus-PB"
    })
    geo_df["configstr"] = geo_df["mitigation"]
    gmeans = []
    for (configstr, tRH), subdf in geo_df.groupby(['configstr', 'tRH']):
        speedups = subdf.speedup
        gmeans.append({
            'benchmark': f'geomean\n({len(subdf.speedup)})',
            'MPKI': subdf.MPKI.mean(),
            'configstr': configstr,
            'tRH': tRH,
            'speedup': gmean(speedups),
            "speedup_sem": sem(speedups),
        })
    gdf = pd.DataFrame(gmeans)

    df["speedup_sem"] = 0
    df = pd.concat([df[['benchmark', 'configstr', 'tRH', 'MPKI', 'speedup', 'speedup_sem']], gdf], ignore_index=True)

    correct = df[(df.configstr == "Chronus-PB") & (df.tRH == 256)]
    df = df[(df.configstr != "Chronus-PB") | (df.tRH <= 256)]
    for tRH in [512, 1024]:
        correct["tRH"] = tRH
        df = pd.concat([df, correct], ignore_index=True)

    fig, axes = plt.subplots(2, 1, figsize=(13, 3.5), sharex=True)
    upper_ax = axes[0]
    upper_ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    upper_ax.set_axisbelow(True)

    upper_data = df[(df.tRH==UPPER_TRH)]

    upper_bars = sns.barplot(
        x='benchmark', y='speedup',
        data=upper_data,
        hue='configstr', 
        hue_order=MITIGATION_LIST,
        linestyle='-',
        palette="pastel",
        ci="sd",
        capsize=0.1,
        errwidth=0.5,
        errcolor='black',
        edgecolor='black',
        ax=upper_ax,
    )

    geo_errs = upper_data[df.benchmark == "geomean\n(57)"]
    num_workloads = 20

    upper_err = []
    for mech in MITIGATION_LIST:
        upper_err += [0] * num_workloads + [geo_errs[df.configstr == mech]["speedup_sem"].values[0]]

    for bar, err in zip(upper_bars.patches, upper_err):
        if not np.isnan(err):  # Skip NaN error bars
            upper_ax.errorbar(
                x=bar.get_x() + bar.get_width() / 2,
                y=bar.get_height(),
                yerr=err,
                fmt='none',  # No marker
                ecolor='black',  # Error bar color
                capsize=0.1,  # Caps on error bars
                elinewidth=1
            )

    upper_ax.add_artist(plt.Rectangle((19.5, 0.2), 1, 1.0, fill=True, edgecolor="black", facecolor='#e5e5e5', linewidth=1, linestyle='-',  zorder=0))

    upper_ax.axhline(1, color='black', linestyle='--', linewidth=1)
    upper_ax.set_ylabel('Norm. Speedup')
    num_columns = 8
    # reorder = lambda l, nc: sum((l[i::nc] for i in range(nc)), [])
    # handles, labels = upper_ax.get_legend_handles_labels()
    upper_ax.legend(loc='center', ncol=num_columns, fancybox=True, shadow=False, handletextpad=0.5, columnspacing=0.75, bbox_to_anchor=(0.5, 1.20))
    upper_ax.set_ylim(0.2, 1.2)
    upper_ax.set_yticks([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
    upper_ax.set_yticklabels(['0.2', '', '0.4', '', '0.6', '', '0.8', '', '1.0', '', '1.2'])

    lower_ax = axes[1]
    lower_ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', zorder=0)
    lower_ax.set_axisbelow(True)
    lower_ax.text(0, 0, "")

    lower_data = df[(df.tRH==LOWER_TRH)]

    lower_bars = sns.barplot(
        x='benchmark', y='speedup',
        data=lower_data,
        hue='configstr', 
        hue_order=MITIGATION_LIST,
        linestyle='-',
        palette="pastel",
        errwidth=0.5,
        errcolor='black',
        edgecolor='black',
        ax=lower_ax
    )

    geo_errs = lower_data[df.benchmark == "geomean\n(57)"]
    num_workloads = 20

    lower_err = []
    for mech in MITIGATION_LIST:
        lower_err += [0] * num_workloads + [geo_errs[df.configstr == mech]["speedup_sem"].values[0]]

    for bar, err in zip(lower_bars.patches, lower_err):
        if not np.isnan(err):  # Skip NaN error bars
            lower_ax.errorbar(
                x=bar.get_x() + bar.get_width() / 2,
                y=bar.get_height(),
                yerr=err,
                fmt='none',  # No marker
                ecolor='black',  # Error bar color
                capsize=0.1,  # Caps on error bars
                elinewidth=1
            )

    lower_ax.add_artist(plt.Rectangle((19.5, 0.2), 1, 1.0, fill=True, edgecolor="black", facecolor='#e5e5e5', linewidth=1, linestyle='-',  zorder=0))

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

    upper_ax.set_xlim(-0.5, 20.5)
    lower_ax.set_xlim(-0.5, 20.5)
    upper_ax.text(0.01, 0.96, f"$N_{{RH}}$ = {UPPER_TRH}", ha="left", va="top", transform=upper_ax.transAxes)
    lower_ax.text(0.01, 0.96, f"$N_{{RH}}$ = {LOWER_TRH}", ha="left", va="top", transform=lower_ax.transAxes)

    fig.tight_layout()
    fig.savefig(f'{PLOT_DIR}/figure7.pdf', bbox_inches='tight')

if __name__ == "__main__":
    plot(f"{CSV_DIR}/merged.csv", f"{TRACE_DIR}/mpki.csv")
