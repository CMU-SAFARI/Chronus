import figure4

from plot_setup import *

def plot_all_figures():
    print(f"[INFO] Reading simulation data")
    ben_df = general_df_setup(f"{RESULT_DIR}/hpcabenign/_csvs", TRACE_DIR, f"{TRACE_COMBINATION_DIR}/hpcabenign.mix", 4)

    print(f"[INFO] Generating Figure4")
    figure4.plot(ben_df.copy())
    print(f"[INFO] Generated Figure4 to {PLOT_DIR}/figure4.pdf")

if __name__ == "__main__":
    plot_all_figures()