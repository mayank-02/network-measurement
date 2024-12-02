import sys
import re
import pandas as pd
import matplotlib.pyplot as plt


def parse_iperf_log(log_file):
    # Initialize data storage for the three flows
    flows = {5201: [], 5202: [], 5203: []}
    offsets = {5201: 0, 5202: 10, 5203: 20}

    # Read the log file line by line
    with open(log_file, "r") as file:
        current_port = None
        for line in file:
            # Match lines indicating connection to a port
            match_port = re.search(r"port (\d+)", line)
            if match_port:
                port = int(match_port.group(1))
                if port in flows:
                    current_port = port

            # Match throughput data lines
            match_data = re.search(
                r"\[.*?\]\s+(\d+\.\d+)-(\d+\.\d+)\s+sec\s+([\d.]+)\s+MBytes\s+([\d.]+)\s+Mbits/sec",
                line,
            )
            if match_data and current_port in flows:
                start_time = float(match_data.group(1))
                throughput = float(match_data.group(4))
                adjusted_time = start_time + offsets[current_port]
                flows[current_port].append((adjusted_time, throughput))

    # Create a DataFrame for each flow
    flow_dfs = {}
    for port, data in flows.items():
        flow_dfs[port] = pd.DataFrame(data, columns=["Time (s)", "Throughput (Mbps)"])
    return flow_dfs


def plot_throughput(flow_dfs):
    plt.figure(figsize=(7, 4))
    flow_labels = {5201: "Flow 1", 5202: "Flow 2", 5203: "Flow 3"}
    for port, df in flow_dfs.items():
        plt.plot(df["Time (s)"], df["Throughput (Mbps)"], label=flow_labels[port])
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Mbps)")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Ensure a file argument is provided
    if len(sys.argv) < 2:
        print("Usage: python plot_iperf_log.py <log_file>")
        sys.exit(1)

    log_file = sys.argv[1]

    # Determine the algorithm based on the file name
    if "bbr" in log_file:
        algorithm = "BBR"
    elif "cubic" in log_file:
        algorithm = "CUBIC"
    else:
        algorithm = "Unknown"

    try:
        flow_dfs = parse_iperf_log(log_file)
        plot_throughput(flow_dfs, algorithm)
    except Exception as e:
        print(f"Error processing the log file: {e}")
