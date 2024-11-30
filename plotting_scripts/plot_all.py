from figure2 import plot_figure2
from figure7 import plot_figure7
from figure8 import plot_figure8
from figure9 import plot_figure9

from plot_setup import *

def plot_all_figures():
    print(f"[INFO] Reading simulation data")
    ben_df = general_df_setup(f"{RESULT_DIR}/hpcabenign/_csvs", TRACE_DIR, f"{TRACE_COMBINATION_DIR}/hpcabenign.mix", 4)

    print(f"[INFO] Generating Figure2")
    plot_figure2(ben_df.copy())
    print(f"[INFO] Generated Figure2 to {PLOT_DIR}/figure2.pdf")
    print(f"[INFO] Generating Figure7")
    plot_figure7(ben_df.copy())
    print(f"[INFO] Generated Figure7 to {PLOT_DIR}/figure7.pdf")
    print(f"[INFO] Generating Figure8")
    plot_figure8(ben_df.copy())
    print(f"[INFO] Generated Figure8 to {PLOT_DIR}/figure8.pdf")
    print(f"[INFO] Generating Figure9")
    plot_figure9(f"{RESULT_DIR}/hpcabenign/_csvs")
    print(f"[INFO] Generated Figure9 to {PLOT_DIR}/figure9.pdf")

if __name__ == "__main__":
    plot_all_figures()