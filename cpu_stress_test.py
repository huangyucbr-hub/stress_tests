import multiprocessing
import time
import math
import os
import sys
from datetime import datetime
import psutil

duration = 60 * 30  # Test duration in seconds

# Heavy computation function to maximize CPU load
def compute_load(iterations):
    result = 0
    for i in range(iterations):
        # Simplified but intense computation
        result += math.sqrt(i + 1) * math.sin(i) * math.cos(i) * math.exp(i % 50)
    return result

# Stress test for a single process
def stress_process(start_time, duration, iterations_per_loop):
    end_time = start_time + duration
    while time.time() < end_time:
        compute_load(iterations_per_loop)

# Monitor CPU and print progress
def monitor_cpu(start_time):
    last_update = 0
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        progress = min(elapsed / duration * 100, 100)
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        if time.time() - last_update >= 1:
            sys.stdout.write(f"\rProgress: {progress:.1f}% | CPU Usage: {cpu_usage:.1f}% | Elapsed: {elapsed:.1f}s")
            sys.stdout.flush()
            last_update = time.time()
        time.sleep(0.1)
    cpu_usage = psutil.cpu_percent(interval=0.1)
    sys.stdout.write(f"\rProgress: 100.0% | CPU Usage: {cpu_usage:.1f}% | Elapsed: {duration:.1f}s\n")
    sys.stdout.flush()

# Main stress test function
def run_cpu_stress_test(duration=60, intensity=20000000):  # Doubled intensity
    num_cores = os.cpu_count()
    processes = []
    
    # Set start time in the main process
    start_time = time.time()
    print(f"Starting CPU stress test on {num_cores} cores for {duration} seconds...")

    # Start CPU monitoring process
    monitor_proc = multiprocessing.Process(target=monitor_cpu, args=(start_time,))
    monitor_proc.start()

    # Launch a process for each CPU core
    for _ in range(num_cores):
        p = multiprocessing.Process(target=stress_process, args=(start_time, duration, intensity))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()
    monitor_proc.join()

    # Calculate elapsed time after all processes finish
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Calculate a performance score
    operations = num_cores * intensity * (duration / elapsed_time) * 1000
    score = operations / 1e6  # Normalize to millions of operations

    return {
        "cores": num_cores,
        "elapsed_time": elapsed_time,
        "score": score
    }

# Log results to a file
def log_results(results):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"cpu_test_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"CPU Stress Test Results\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Cores Used: {results['cores']}\n")
        f.write(f"Elapsed Time: {results['elapsed_time']:.2f} seconds\n")
        f.write(f"Performance Score: {results['score']:.2f} MOPS\n")
    return filename

# Main execution
if __name__ == "__main__":
    multiprocessing.freeze_support()  # Required for Windows

    print("CPU Stress Test Script (Command Line Version - Max Load)")
    print("Press Ctrl+C to stop early if needed.\n")

    try:
        # Run the test
        results = run_cpu_stress_test(duration=duration, intensity=20000000)

        # Display final results
        print(f"\nTest Complete!")
        print(f"Cores Used: {results['cores']}")
        print(f"Elapsed Time: {results['elapsed_time']:.2f} seconds")
        print(f"Performance Score: {results['score']:.2f} MOPS (Millions of Operations Per Second)")

        # Save results to a file
        log_file = log_results(results)
        print(f"Results saved to: {log_file}")

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)