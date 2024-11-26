import matplotlib.pyplot as plt
import sys
import numpy as np


# Check if the file name is provided
if len(sys.argv) != 2:
    print("Usage: python plot_metrics.py <log_file>")
    sys.exit(1)


# Get the log file name
log_file = sys.argv[1]


# Lists to store the extracted data
cwnd_values = []
ssthresh_values = []
throughput_values = []
rtt_values = []


# Parse the log file
try:
    with open(log_file, "r") as file:
        for line in file:
            if "cwnd:" in line and " ssthresh:" in line:
                # Parse CWND
                try:
                    cwnd_index = line.index("cwnd:")
                    cwnd_value = int(line[cwnd_index + 5:].split()[0])
                    cwnd_values.append(cwnd_value)
                except (ValueError, IndexError):
                    print(f"Failed to parse CWND in line: {line.strip()}")


                # Parse SSTHRESH
                try:
                    ssthresh_index = line.index(" ssthresh:")
                    ssthresh_value = int(line[ssthresh_index + 10:].split()[0])
                    ssthresh_values.append(ssthresh_value)
                except (ValueError, IndexError):
                    print(f"Failed to parse SSTHRESH in line: {line.strip()}")


                # Parse delivery_rate (Throughput)
                try:
                    delivery_rate_index = line.index("delivery_rate")
                    delivery_rate_value = float(line[delivery_rate_index + 14:].split()[0].replace("bps", ""))
                    delivery_rate_value /= 1e6  # Convert to Mbps
                    throughput_values.append(delivery_rate_value)
                except (ValueError, IndexError):
                    print(f"Failed to parse delivery_rate in line: {line.strip()}")


                # Parse RTT
                try:
                    rtt_index = line.index("rtt:")
                    rtt_value = float(line[rtt_index + 4:].split('/')[0])  # Extract smoothed RTT
                    rtt_values.append(rtt_value)
                except (ValueError, IndexError):
                    print(f"Failed to parse RTT in line: {line.strip()}")
except FileNotFoundError:
    print(f"Error: File '{log_file}' not found.")
    sys.exit(1)


# Scale x-axis values to 0.1-second granularity
time_values = np.arange(len(cwnd_values)) * 0.1


# Calculate mean RTT
mean_rtt = np.mean(rtt_values) if rtt_values else 0


# Create the figure and subplots with additional space between them
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'hspace': 0.1}, constrained_layout=True)


# ---- First subplot: CWND and SSTHRESH ----
ax1.set_title("CWND and SSTHRESH Over Time")
ax1.set_xlabel("Time (seconds)")


# Plot CWND on the primary y-axis
ax1.set_ylabel("CWND (in MSS)", color="#1f77b4")
line_cwnd, = ax1.plot(time_values, cwnd_values, linestyle='-', linewidth=2, color="#1f77b4", label="CWND")
ax1.tick_params(axis="y", labelcolor="#1f77b4")
ax1.grid(True)


# Create a secondary y-axis for SSTHRESH
ax1_ssthresh = ax1.twinx()
ax1_ssthresh.set_ylabel("SSTHRESH (in MSS)", color="#ff7f0e")
line_ssthresh, = ax1_ssthresh.plot(time_values, ssthresh_values, linestyle='--', linewidth=2, color="#ff7f0e", label="SSTHRESH")
ax1_ssthresh.tick_params(axis="y", labelcolor="#ff7f0e")


# Add mean RTT to the legend (without plotting it)
mean_rtt_label = f"Mean RTT: {mean_rtt:.2f} ms"
handles_cwnd = [line_cwnd]
handles_ssthresh = [line_ssthresh]
ax1.legend(handles=handles_cwnd + handles_ssthresh + [plt.Line2D([0], [0], color="none", label=mean_rtt_label)],
           loc="upper right", fontsize=10)


# ---- Second subplot: Throughput ----
ax2.set_title("Throughput Over Time")
ax2.set_xlabel("Time (seconds)")
ax2.set_ylabel("Throughput (Mbps)")


# Plot Throughput
line_throughput, = ax2.plot(time_values, throughput_values, linestyle='-', linewidth=2, color="#2ca02c", label="Throughput")
ax2.tick_params(axis="y")
ax2.grid(True)


# Add legend
ax2.legend(handles=[line_throughput], loc="upper right", fontsize=10)


# Add a global title and adjust layout

# Show the plots
plt.show()
