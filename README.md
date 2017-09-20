# DPA on a SHA256 PRNG
We propose and implement a DPA on a SHA256 PRNG which is similar to the one proposed for W-OTS+ secret key generation within XMSS (https://datatracker.ietf.org/doc/draft-irtf-cfrg-xmss-hash-based-signatures/).

A detailed description is available in my master thesis, which will be published shortly.

## License
Code delivered in this package by Matthias Julius Kannwischer is published under BSD (2-clause) license. Actual information about the specific license is to be found in each source code file.

## Dependencies
 - https://www.python.org/
 - http://www.numpy.org/
 - https://pypi.python.org/pypi/fixedint/0.1.2

## Quick Start
 - `cd simulation && make && cd ..`
 - 8-bit DPA attack
    - `./simulation/simulate 100 HW_BYTE ca79af4090c3ca6defec33d631704e018b8ca869c5e2ed26f0b65cf8bbdb5c86`
    - `./analysis/analyze_8bit.py leakage_100.bin secret_data.txt`
 - 32-bit DPA attack on AND
    - `./simulation/simulate 2000 HW ca79af4090c3ca6defec33d631704e018b8ca869c5e2ed26f0b65cf8bbdb5c86`
    - `./analysis/analyze_32bit_and.py leakage_2000.bin secret_data.txt 0.5`
 - 32-bit DPA attack on addition
    - `./simulation/simulate 1000 HW ca79af4090c3ca6defec33d631704e018b8ca869c5e2ed26f0b65cf8bbdb5c86`
    - `./analysis/analyze_32bit_addition.py leakage_1000.bin secret_data.txt 0.5`
 - Note: Success of attack depends upon seed. With the seeds above the attacks succeed. If you use different ones you may need more traces.
## Simulating Power Traces
- `make` in [`simulation/`](simulation/) builds the project
- The power simulation can be used by running `./simulation/simulate n t [k]`, e.g. `./simulation/simulate 1000 HW`
- The parameters are
  - `n` : number of traces, PRNG will be executed for indices: 0 <= i < n
  - `t` : leakage type (`HW`, `HW_BYTE`)
  - `k` : optional, 256-bit seed as hex string without 0x
  - If no `k` is given, a random one will be generated
- We implement 2 leakage modes
    - `HW`: leaking the Hamming weight of the result of each 32-bit operation
    - `HW_BYTE` : leaking the Hamming weight of each byte of the result separately (i.e. 4 data points per operation)
- The simulation produces two files
  - `leakage_<n>.bin` containing the power `n` simulation traces in 8 bit unsigned char binary format
  - `secret_data.txt` containing the seed and iv information - required for validating recovered keys later
- Additionally, for development and debugging purposes we implemented [`partial_leak_prng.c`](simulation/partial_leak_prng.c) which only leaks the relevant operations

## Running the DPA Attack
 - We implemented three DPA attack scripts
 - [analyze_8bit.py](analysis/analyze_8bit.py) implements the DPA in the 8-bit HW leakage model.
    - It can be used by running `./analysis/analyze_8bit.py traceFile secretDataFile`
    - The parameters are
      - `traceFile`: path the binary trace file created in the `HW_BYTE` mode
      - `secretDataFile`: path to the secret data file, usually `secret_data.txt`. This is just use for checking the result
  - [analyze_32bit_addition.py](analysis/analyze_32bit_addition.py) implements DPA1 in the 32-bit HW leakage model, i.e., an DPA on addition.
    - It can be used by running `./analysis/analyze_32bit_addition.py traceFile secretDataFile threshold`
    - The parameters are
      - `traceFile`: path the binary trace file created in the `HW` mode
      - `secretDataFile`: path to the secret data file, usually `secret_data.txt`. This is just use for checking the result
      - `threshold`: threshold used for picking key hypothesis. For different numbers of traces, different thresholds are optimal. See [dpa.py](analysis/dpa.py) for details. `0.5` works fine in most of the cases
  - [analyze_32bit_and.py](analysis/analyze_32bit_addition.py) implements DPA5 in the 32-bit HW leakage model, i.e. an DPA on AND
    - It can be used by running `./analysis/analyze_32bit_and.py traceFile secretDataFile threshold`
    - The parameters are
      - `traceFile`: path the binary trace file created in the `HW` mode
      - `secretDataFile`: path to the secret data file, usually `secret_data.txt`. This is used for checking the result AND to get the required values of E_1 (which is computed from D_0 and delta, which were originally recovered in DPA1 and DPA2). This is cheating - but we just wanted to evaluate DPA5.
      - `threshold`: threshold used for picking key hypothesis. For different numbers of traces, different thresholds are optimal. See [dpa.py](analysis/dpa.py) for details. `0.5` works fine in most of the cases

## Performing Experiments
- [`./experiment_1.sh`](experiment_1.sh) will reproduce the data for Figure 5.6
- [`./experiment_3.sh`](experiment_3.sh) will reproduce the data for Figure 5.8
- [`./experiment_5.sh`](experiment_3.sh) will reproduce the data for Figure 5.9
- [`./experiment_7.sh`](experiment_7.sh) will reproduce the data for Figure 5.7. It is required to uncomment line 88 in [dpa.py](analysis/dpa.py)
- [`experiment_2.sh`](other_experiments/experiment_2.sh) and [`experiment_6.sh`](other_experiments/experiment_6.sh) were just for sanity checking and don't produce valuable results. Therefore, they are left undocumented. Additionally, mysteriously `experiment_4.sh` is missing

## Reproducing Plots
- [plots/exp1_3_5.py](plots/exp1_3_5.py) can be used to reproduce Figure 5.6, Figure 5.8, Figure 5.9
- [plots/corr_over_time.py](plots/corr_over_time.py) can be used to reproduce Figure 5.4 and Figure 5.5
- [plots/corr_plot_trace.py](plots/plot_trace.py) can be used to reproduce Figure 5.3 ()
- [plots/partial_corr.py](plots/partial_corr.py) can be used to reproduce Figure 5.7 (see Experiment 7)
- For requirements see these files
- [plots/exp_1_3_5.py](plots/exp_2_6.py) can be used for the undocumented experiments that never made it into the thesis.

## Using the Code
- Feel free to use, modify, and redistribute the code (according to the license)
- `data/` is used to hold the experiment results
- `plots/` contains the script to reproduce the thesis plots
- See [simulation/README.md](simulation/README.md) and [analysis/README.md](analysis/README.md) for details of the two modules
