import matplotlib.pyplot as plt
import sys
import numpy as np

# Check if the file name is provided
if len(sys.argv) < 3:
    print("Usage: python plot_metrics.py log_file cubic/bbr [plot_bytes_retrans]")
    sys.exit(1)

# Get the log file name
log_file = sys.argv[1]
flask = "flask" in log_file
cca = sys.argv[2]
enable_bytes_retrans_plot = False
if len(sys.argv) == 4:
    enable_bytes_retrans_plot = bool(sys.argv[3])


# Lists to store the extracted data
cwnd_values = []
ssthresh_values = []
throughput_values = []
rtt_values = []
timestamps = []
bytes_retrans_values = []
bytes_retrans_timestamps = []
bytes_retrans_old = 0

# Parse the log file
try:
    with open(log_file, "r") as file:
        for line in file:
            # if "cwnd:" in line and " ssthresh:" in line:
            if ("cwnd:" in line) and ((flask) or (not flask and "data_segs_out:3 " not in line)):
                try:
                    timestamp = float(line.split()[0])  # Extract the first value as timestamp
                    timestamps.append(timestamp)
                except (ValueError, IndexError):
                    print(f"Failed to parse timestamp in line: {line.strip()}")
                    continue  # Skip this line if timestamp parsing fails
                
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
                    ssthresh_values.append(0)

                # Parse delivery_rate (Throughput)
                try:
                    delivery_rate_index = line.index("delivery_rate")
                    delivery_rate_value = float(line[delivery_rate_index + 14:].split()[0].replace("bps", ""))
                    delivery_rate_value /= 1e6  # Convert to Mbps
                    throughput_values.append(delivery_rate_value)
                except (ValueError, IndexError):
                    print(f"Failed to parse delivery_rate in line: {line.strip()}")
                    throughput_values.append(0)

                # Parse RTT
                try:
                    rtt_index = line.index("rtt:")
                    rtt_value = float(line[rtt_index + 4:].split('/')[0])  # Extract smoothed RTT
                    rtt_values.append(rtt_value)
                except (ValueError, IndexError):
                    print(f"Failed to parse RTT in line: {line.strip()}")

                try:
                    bytes_retrans_index = line.index("bytes_retrans:")
                    bytes_retrans_value = float(line[bytes_retrans_index + len("bytes_retrans:"):].split()[0])
                    if bytes_retrans_value != bytes_retrans_old:
                        bytes_retrans_new = bytes_retrans_value
                        bytes_retrans_value -= bytes_retrans_old
                        bytes_retrans_old = bytes_retrans_new
                        bytes_retrans_value /= 1e6 # Convert to Mb
                        bytes_retrans_values.append(bytes_retrans_value)
                        bytes_retrans_timestamps.append(timestamp)
                except (ValueError, IndexError):
                    print(f"No retrans")

except FileNotFoundError:
    print(f"Error: File '{log_file}' not found.")
    sys.exit(1)

# Calculate relative time for x-axis
if timestamps:
    relative_time = [(t - timestamps[0]) for t in timestamps]  # Start at t = 0
else:
    print("No valid timestamps found. Exiting.")
    sys.exit(1)

if bytes_retrans_timestamps:
    relative_bytes_retrans_time = [(t - timestamps[0]) for t in bytes_retrans_timestamps]  # Start at t = 0

# Calculate mean and stddev of RTT
mean_rtt = np.mean(rtt_values) if rtt_values else 0
stddev_rtt = np.std(rtt_values) if rtt_values else 0

# Create the figure and subplots with additional space between them
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), gridspec_kw={'hspace': 0.1}, constrained_layout=True)

# ---- First subplot: CWND and SSTHRESH ----
ax1.set_xlabel("Time (seconds)")

# Plot CWND, SSTHRESH on the primary y-axis
line_cwnd, = ax1.plot(relative_time, cwnd_values, linestyle='-', linewidth=2, color="#1f77b4", label="CWND")
# Add mean RTT and stddev RTT to the legend (without plotting them)
rtt_label = f"Mean RTT: {mean_rtt:.2f} ms, σ RTT: {stddev_rtt:.2f} ms"
handles_cwnd = [line_cwnd]
if cca == "cubic":
    ax1.set_ylabel("CWND and SSTHRESH (in MSS)")
    line_ssthresh, = ax1.plot(relative_time, ssthresh_values, linestyle='--', linewidth=2, color="#ff7f0e", label="SSTHRESH")
    handles_ssthresh = [line_ssthresh]
    ax1.legend(handles=handles_cwnd + handles_ssthresh + [plt.Line2D([0], [0], color="none", label=rtt_label)], loc='upper center', bbox_to_anchor=(0.5, 1.2),
          fancybox=True, ncol=5)

    if enable_bytes_retrans_plot and bytes_retrans_timestamps:
        ax1_bytes_retrans = ax1.twinx()
        ax1_bytes_retrans.set_ylabel("Bytes retransmitted (in Mb)", color="red")
        ax1_bytes_retrans.scatter(relative_bytes_retrans_time, bytes_retrans_values, color="red", marker = "x")
        ax1_bytes_retrans.tick_params(axis="y", labelcolor="red")
        ax1_bytes_retrans.set_ylim(0, max(bytes_retrans_values) * 1.1)  # Start from 0

else:
    ax1.set_ylabel("CWND (in MSS)")
    ax1.legend(handles=[plt.Line2D([0], [0], color="none", label=rtt_label)], loc='upper center', bbox_to_anchor=(0.5, 1.2),
          fancybox=True, ncol=5)

ax1.tick_params(axis="y")
ax1.grid(True)
ax1.set_ylim(0, max(cwnd_values) * 1.1)  # Start from 0

# ---- Second subplot: Throughput ----
ax2.set_xlabel("Time (seconds)")
ax2.set_ylabel("Throughput (Mbps)")

# Plot Throughput
line_throughput, = ax2.plot(relative_time, throughput_values, linestyle='-', linewidth=2, color="#2ca02c", label="Throughput")
ax2.tick_params(axis="y")
ax2.grid(True)
ax2.set_ylim(0, max(throughput_values) * 1.1)  # Start from 0

# Show the plots
plt.savefig("/Users/tanyasneh/Desktop/CSE222A/project/network-measurement/"+log_file[:-3]+"png", dpi=fig.dpi)
# plt.show()
