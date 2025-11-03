import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

def extract_flow_rate(filename):
    match = re.search(r'(\d+(?:\.\d+)?)mlpmin', filename.lower())
    return float(match.group(1)) if match else None

def process_each_csv_separately(csv_folder):
    summary_data = []

    for file in glob.glob(os.path.join(csv_folder, "**/*.csv"), recursive=True):
        filename = os.path.basename(file)

        if 'jet_length' not in filename.lower():
            continue

        flow_rate = extract_flow_rate(filename)
        if flow_rate is None:
            print(f"[!] Could not extract flow rate from: {filename}")
            continue

        try:
            df = pd.read_csv(file)

            if 'Jet Length (pixels)' not in df.columns:
                print(f"Skipping '{filename}' – no 'Jet Length (pixels)' column.")
                continue

            jet_lengths = df['Jet Length (pixels)'].values
            adjusted_lengths = jet_lengths - 11
            valid_lengths = adjusted_lengths[adjusted_lengths > 0]

            if len(valid_lengths) == 0:
                print(f"No valid jet lengths in '{filename}' after adjustment.")
                continue

            mu, std = norm.fit(valid_lengths)

            # Plotting
            plt.figure(figsize=(8, 5))
            plt.hist(valid_lengths, bins=40, density=True, alpha=0.6, color='b', label='Jet Lengths')
            x = np.linspace(min(valid_lengths), max(valid_lengths), 100)
            p = norm.pdf(x, mu, std)
            plt.plot(x, p, 'r', linewidth=2, label=f'Fit: μ={mu:.2f}, σ={std:.2f}')

            plt.xlabel('Jet Length (pixels)')
            plt.ylabel('Density')
            plt.title(f'Histogram: {filename}')
            plt.legend()
            plt.grid(True)

            save_name = filename.replace(".csv", "_histogram.png")
            save_path = os.path.join(os.path.dirname(file), save_name)
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()

            # Save summary stats
            summary_data.append({
                "Flow Rate (ml/min)": flow_rate,
                "Mean (μ)": round(mu, 2),
                "Std Dev (σ)": round(std, 2),
                "Count": len(valid_lengths)
            })

            print(f"[✓] Processed: {filename} (Flow Rate: {flow_rate} ml/min)")
            print(f"    → Histogram saved to: {save_path}")
            print(f"    → μ = {mu:.2f}, σ = {std:.2f}\n")

        except Exception as e:
            print(f"[!] Error processing '{filename}': {e}")

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values(by="Flow Rate (ml/min)").reset_index(drop=True)
        summary_csv_path = os.path.join(csv_folder, "summary_stats_by_flowrate.csv")
        summary_df.to_csv(summary_csv_path, index=False)
        print(f"\n📄 Summary CSV saved to: {summary_csv_path}")
    else:
        print("No valid data found in any file.")

# MAIN
if __name__ == "__main__":
    csv_folder = r"CSV folder path"
    process_each_csv_separately(csv_folder)
