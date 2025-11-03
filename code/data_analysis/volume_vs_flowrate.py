import numpy as np
import matplotlib.pyplot as plt

# Define needle diameters
diameters = np.array([needle diameters])  # Example diameters in mm
Q_c_1 = np.array([critical flowrates first])
F_c_1 = np.array([critical Frqn])
V_c_1 = np.array([critical volumes])
Q_c_2 = np.array([critical flowrates secound])
# Example Data: (Flow Rate, Frequency, Volume, Std. Dev.) for 6 needles
data_sets = {
    needle 1 : """Flow Rate	Frequency	Volume	Std. Dev.""",
    
    needle 2 : """Flow Rate	Frequency	Volume	Std. Dev.""",
    
    needle 3: """Flow Rate	Frequency	Volume	Std. Dev.""",
}

# Define colors and markers for each needle diameter
colors = ['b', 'g', 'r', 'c', 'm', 'y']
markers = ['o', 's', 'D', '^', 'v', 'p']
Final_Volume = []
V_0 = []
# plt.figure(figsize=(10, 6))

# Process each dataset and plot
for i, (D, data_raw) in enumerate(data_sets.items()):
    Q_list, Frqn_list, Volume_list, StdDev_list = [], [], [], []

    for line in data_raw.splitlines():
        q, frqn, vol, std_dev = map(float, line.split())
        q_mm3_per_sec = q * 1000 / 60  # Convert Flow Rate to mm³/sec

        Q_list.append(q_mm3_per_sec)
        Frqn_list.append(frqn)
        Volume_list.append(vol)
        StdDev_list.append(std_dev)

    Q = np.array(Q_list)
    Frqn = np.array(Frqn_list)
    Volume = np.array(Volume_list)
    StdDev = np.array(StdDev_list)
    FlowRate_by_Freq = Q / Frqn
    Final_Volume.append(Volume[-1])
    V_0.append(Volume[0])
    # Plot Volume vs Flow Rate with error bars
    # plt.errorbar(Q, Volume, yerr=StdDev, fmt=markers[i], color=colors[i], label=f'Volume (D={D}mm)', ecolor='black', capsize=3)

    # # Plot (Flow Rate / Frequency) vs Flow Rate
    plt.scatter(Q, Volume[0]-Volume, color=colors[i], marker=markers[i], label = f'D={D}mm')

Final = np.array(Final_Volume)
A_exp = np.array(V_0)

# '''# Example plot: D² vs Q_c
# plt.figure(figsize=(8, 5))
# plt.scatter(V_0 , Diameter, color='blue', label='Data Points')
# plt.plot(V_0 , Diameter, color='red', linestyle='--', label='Line')

# # Labels using LaTeX formatting
# plt.xlabel(r"$V_0$ $(mm^3)$", fontsize = 18)  # Replace 'unit' with actual units
# plt.ylabel(r"$D$ (mm)", fontsize = 18)  # Or appropriate units
# plt.title(r"$D$ vs $V_0$ Plot", fontsize = 24)'''

# plt.xscale('log')
# plt.yscale('log')
# plt.xlim(10,10000)
# plt.ylim(.001,100)

# Labels, title, and legend
plt.xlabel(r'$Flow Rate$',fontsize=15)
plt.ylabel(r'$V_0-Volume$',fontsize=15)
# plt.title('Scaled Volume vs Flow Rate Graph for Different Needle Diameters(D)', fontsize = 18)
plt.legend()
plt.tight_layout()
plt.grid()

# # Show plot
# plt.show()
print(A_exp)