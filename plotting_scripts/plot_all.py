import figure4
import figure7
import figure8
import figure9
import figure10
import figure11

from plot_setup import *

def plot_all_figures():
    print(f"[INFO] Reading simulation data")
    ben_df = general_df_setup(f"{RESULT_DIR}/hpcabenign/_csvs", TRACE_DIR, f"{TRACE_COMBINATION_DIR}/hpcabenign.mix", 4)

    print(f"[INFO] Generating Figure4")
    figure4.plot(ben_df.copy())
    print(f"[INFO] Generated Figure4 to {PLOT_DIR}/figure4.pdf")

    print(f"[INFO] Generating Figure7")
    figure7.plot(f"{RESULT_DIR}/hpcasingle/_csvs/merged.csv", f"{TRACE_DIR}/mpki.csv")
    print(f"[INFO] Generated Figure7 to {PLOT_DIR}/figure7.pdf")

    print(f"[INFO] Generating Figure8")
    figure8.plot(ben_df.copy())
    print(f"[INFO] Generated Figure8 to {PLOT_DIR}/figure8.pdf")

    print(f"[INFO] Generating Figure9")
    figure9.plot(ben_df.copy())
    print(f"[INFO] Generated Figure9 to {PLOT_DIR}/figure9.pdf")

    print(f"[INFO] Generating Figure10")
    figure10.plot(ben_df.copy())
    print(f"[INFO] Generated Figure10 to {PLOT_DIR}/figure10.pdf")

    print(f"[INFO] Generating Figure11")
    figure11.plot()
    print(f"[INFO] Generated Figure11 to {PLOT_DIR}/figure11.pdf")

7
if __name__ == "__main__":
    plot_all_figures()