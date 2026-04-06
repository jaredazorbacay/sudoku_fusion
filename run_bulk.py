import subprocess
import csv
import os
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

RUNS_PER_INSTANCE = 50
INSTANCE_FOLDER = "instances/25x25-dataset"
TIMEOUT = "120"

MAX_FILES = None
NUM_THREADS = 7

# 🔹 Define your parameter list here
T0_VALUES = [0.805, 0.9, 0.999]


def run_solver(file_path, timeout, t0):
    cmd = [
        "./sudokusolver",
        "--file", file_path,
        "--timeout", timeout,
        "--alpha", str(t0)
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        out = result.stdout.strip().split("\n")

        if result.returncode == 0 and len(out) >= 3:
            time_value = float(out[1])
            cycles = int(out[2])
            return True, time_value, cycles

        return False, None, None

    except Exception:
        return False, None, None


def process_instance(file_path, t0):

    times = []
    cycles_arr = []
    success_count = 0

    for _ in range(RUNS_PER_INSTANCE):

        solved, t_value, cycles = run_solver(file_path, TIMEOUT, t0)

        if solved:
            success_count += 1

        if t_value is not None:
            times.append(t_value)

        if cycles is not None:
            cycles_arr.append(cycles)

    success_rate = (success_count/ RUNS_PER_INSTANCE) * 100
    avg_time = statistics.mean(times) if times else 0
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    avg_cycles = statistics.mean(cycles_arr) if cycles_arr else 0

    print(f"\nRunning: {file_path} | t0={t0}")
    print(f" → Success: {success_rate:.2f}%")
    print(f"   Avg Time: {avg_time:.8f}")
    print(f"   Std Dev: {std_time:.8f}")
    print(f"   Avg Cycles: {avg_cycles:.2f}")

    return [
        os.path.basename(file_path),
        RUNS_PER_INSTANCE * 2,
        success_count,
        f"{(success_rate*2):.2f}",
        f"{avg_time:.8f}",
        f"{std_time:.8f}",
        f"{avg_cycles:.2f}"
    ]


def run_for_t0(t0):

    print(f"\n========== RUNNING FOR t0 = {t0} ==========\n")

    files = sorted([
        os.path.join(INSTANCE_FOLDER, f)
        for f in os.listdir(INSTANCE_FOLDER)
        if f.endswith(".txt")
    ])

    if MAX_FILES is not None:
        files = files[:MAX_FILES]

    print(f"Processing {len(files)} files with {NUM_THREADS} threads")

    results = []

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:

        futures = [
            executor.submit(process_instance, f, t0)
            for f in files
        ]

        for future in as_completed(futures):
            results.append(future.result())

    # 🔹 Dynamic output filename per t0
    output_file = f"[25x25]coolingRate-{t0}.csv"

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Instance File",
            "Runs",
            "Successes",
            "Success Rate (%)",
            "Avg Time",
            "Std Dev Time",
            "Avg Cycles"
        ])

        for row in results:
            writer.writerow(row)

    print(f"\nDONE for t0={t0}! Saved to {output_file}")


def main():

    # 🔹 Run each t0 SEQUENTIALLY
    for t0 in T0_VALUES:
        run_for_t0(t0)


if __name__ == "__main__":
    main()