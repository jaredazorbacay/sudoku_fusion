import subprocess
import csv
import os
import statistics

RUNS_PER_INSTANCE = 100
INSTANCE_FOLDER = "instances/9x9-dataset"
OUTPUT_FILE = "sudoku_results-9x9NoSA.csv"
TIMEOUT = "5"

# ✅ NEW: limit number of instance files
MAX_FILES = None    # set to None to run ALL files


def run_solver(file_path, timeout):
    cmd = [
        "./sudokusolver",
        "--file", file_path,
        "--timeout", timeout,
        "--saFreq", "0"
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


def main():

    # ✅ Collect and sort files
    files = sorted([
        os.path.join(INSTANCE_FOLDER, f)
        for f in os.listdir(INSTANCE_FOLDER)
        if f.endswith(".txt")
    ])

    # ✅ Apply max file limit
    if MAX_FILES is not None:
        files = files[:MAX_FILES]

    print(f"Running {len(files)} instance files")

    with open(OUTPUT_FILE, "w", newline="") as f:
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

        for file_path in files:
            print(f"\nRunning: {file_path}")

            times = []
            cycles_arr = []
            success_count = 0

            for r in range(RUNS_PER_INSTANCE):
                solved, t_value, cycles = run_solver(file_path, TIMEOUT)

                if solved:
                    success_count += 1
                    print("|", end="", flush=True)
                else:
                    print("x", end="", flush=True)

                if t_value is not None:
                    times.append(t_value)

                if cycles is not None:
                    cycles_arr.append(cycles)

            print()

            success_rate = (success_count / RUNS_PER_INSTANCE) * 100
            avg_time = statistics.mean(times) if times else 0
            std_time = statistics.stdev(times) if len(times) > 1 else 0
            avg_cycles = statistics.mean(cycles_arr) if cycles_arr else 0

            print(f" → Success: {success_rate:.2f}%")
            print(f"   Avg Time: {avg_time:.8f}")
            print(f"   Std Dev: {std_time:.8f}")
            print(f"   Avg Cycles: {avg_cycles:.2f}")

            writer.writerow([
                os.path.basename(file_path),
                RUNS_PER_INSTANCE,
                success_count,
                f"{success_rate:.2f}",
                f"{avg_time:.8f}",
                f"{std_time:.8f}",
                f"{avg_cycles:.2f}"
            ])

    print(f"\nDONE! Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()