# A Study of Cubic and BBR under Varied Application Workloads

## Overview
This project analyzes and compares the behavior of two congestion control algorithms (CCAs): Cubic and BBR. The analysis is conducted using two types of applications: bulk traffic and a Flask-based web server. The goal is to understand the performance characteristics of the CCAs under varying network conditions, including delay and packet loss, and to evaluate their fairness when multiple flows share the same bottleneck.

## Goals
1. Understand the functioning of Cubic (loss-based CCA) and BBR (rate-based CCA).
2. Compare their behavior using:
   - Bulk traffic (iperf3)
   - Web server (Flask server)
3. Analyze key metrics such as:
   - Congestion window (CWND)
   - Slow start threshold (SSTHRESH)
   - Throughput
   - RTT
   - Packet loss behavior
   - Flow completion times
   - Fairness (only for bulk traffic)

## Requirements
- `tc` tool (Linux Traffic Control)
- `ss` tool for TCP socket statistics
- iperf3
- Python 3.x
- `ts` to timestamp command outputs

## Setup

### Congestion Control Algorithm

1. Check current congestion control algorithms
   ```bash
   sudo sysctl -a | grep congest
   ```

1. Switch to BBR:
   ```bash
   # Load the `tcp_bbr` module
   sudo modprobe tcp_bbr

   # Verify that the module is loaded:
   lsmod | grep bbr

   # Check available CCAs again to confirm `bbr` is listed:
   sudo sysctl -a | grep congest

   # Enable BBR as the active CCA
   sudo sysctl -w net.ipv4.tcp_congestion_control=bbr

   # Verify that BBR is now the active CCA
   sysctl net.ipv4.tcp_congestion_control
   ```

1. Revert to the default Cubic:
   ```bash
   # Enable CUBIC as the active CCA
   sudo sysctl -w net.ipv4.tcp_congestion_control=cubic

   # Verify that CUBIC is now the active CCA
   sysctl net.ipv4.tcp_congestion_control
   ```

### Network Configuration

1. Install the required tools on both client and server:
    ```bash
    sudo apt -y update
    sudo apt install -y iperf3 python3-pip
    sudo apt install moreutils
    ```

1. Start the iperf3 server on the server machine:
    ```bash
    iperf3 -s
    ```

1. Configure network delay and packet loss at client:
    - Extract the interface name:
      ```bash
      ip link show
      ```
    - Add a delay of 20ms:
      ```bash
      sudo tc qdisc add dev <interface> root netem delay 20ms
      ```
    - Introduce packet loss as desired:
      ```bash
      sudo tc qdisc change dev <interface> root netem delay 20ms loss 0.005%
      ```

1. Verify the configuration:
   ```
   tc qdisc show dev <interface>
   ```

1. Monitor the network conditions:
   ```
   ./monitor.sh <log-file> <server-ip>
   ```

1. Run the iperf3 client:
   ```bash
   iperf3 -c <server-ip> -t 60
   ```

1. Run the Flask server:
   ```bash
   sudo apt install python3-pip python3.12-venv
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install Flask
   python3 server.py
   ```

1. Reset network conditions:
   ```
   sudo tc qdisc del dev <interface> root
   ```

1. In case of fairness analysis, run multiple iperf3 clients simultaneously.
   ```bash
   # Server
   sudo tc qdisc del dev <interface> root
   
   # Client
   sudo tc qdisc del dev <interface> root
   # Add a Token Bucket Filter (TBF) with a rate of 600mbit and a delay of 20ms
   sudo tc qdisc add dev <interface> root tbf rate 600mbit delay 20ms
   # Run 3 iperf3 clients in the background (-c <server-ip> -p <server-port> -t <seconds> > <log-file>) 
   (iperf3 -c <server1-ip> -p <server1-port> -t 300 > client1.log) & (sleep 10; iperf3 -c <server2-ip> -p <server2-port> -t 300 > client2.log) & (sleep 20; iperf3 -c <server3-ip> -p <server3-port> -t 300 > client3.log) &
   ```

### Data Collection

We use the `ss` tool to collect CWND, SSTHRESH, RTT, and throughput data at regular intervals (e.g., 100ms). For more details, refer to the `monitor.sh` script.

### Plotting

We use Python scripts to plot the data collected during the experiments. For more details, refer to the `plot.py` script.

## References
1. [CUBIC: A New TCP-Friendly High-Speed TCP Variant](https://www.cs.princeton.edu/courses/archive/fall16/cos561/papers/Cubic08.pdf)
2. [BBR: Congestion-Based Congestion Control](https://queue.acm.org/detail.cfm?id=3022184)
3. [`tc`](https://man7.org/linux/man-pages/man8/tc.8.html)
4. [`iperf3`](https://software.es.net/iperf/)
5. [`ss`](https://man7.org/linux/man-pages/man8/ss.8.html)
6. Python matplotlib Documentation
7. [TCP congestion control](https://witestlab.poly.edu/blog/tcp-congestion-control-basics)

## Authors

- [Mayank Jain](https://jainmayank.me)
- [Tanya Sneh](https:/github.com/tanya06)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
