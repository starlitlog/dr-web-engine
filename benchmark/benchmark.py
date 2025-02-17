import psutil
import subprocess
import time
import json
import os

OXPATH_JAR_FOLDER = '/Users/ylliprifti/OneDrive/Dev/data-gather/'
CURRENT_CONFIG = 'iMac'

def get_memory_and_cpu_usage():
    """Capture the current memory and CPU usage."""
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    return cpu_usage, mem_usage


def run_command(command):
    """Run the command and capture the execution metrics."""
    start_time = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Initialize lists to capture metrics
    cpu_usage = []
    mem_usage = []

    # Monitor the process
    while process.poll() is None:
        cpu, mem = get_memory_and_cpu_usage()
        cpu_usage.append(cpu)
        mem_usage.append(mem)
        time.sleep(1)  # Sleep for a second before checking again

    process.wait()  # Wait for the process to finish
    end_time = time.time()
    execution_time = end_time - start_time  # Total execution time in seconds

    # Capture the output and format it
    stdout, stderr = process.communicate()
    return stdout, stderr, execution_time, cpu_usage, mem_usage


def get_output_file_size(output_file):
    """Get the size of the output file in bytes."""
    if os.path.exists(output_file):
        return os.path.getsize(output_file)
    else:
        return None  # File does not exist


def main():
    command1 = ["dr-web-engine", "-q", "queries/simple.json5", "-o", "simple.json", "--xvfb"]
    command2 = ["java", "-jar", f"{OXPATH_JAR_FOLDER}/bin/oxpath-cli.jar", "-q", "simple.oxpath", "-o",
                "simple.oxpath.json", "-f", "JSON", "--xvfb"]

    # Run both commands
    stdout1, stderr1, exec_time1, cpu_usage1, mem_usage1 = run_command(command1)
    stdout2, stderr2, exec_time2, cpu_usage2, mem_usage2 = run_command(command2)

    # Get output file size
    output_file_size1 = get_output_file_size("simple.json")
    output_file_size2 = get_output_file_size("simple.oxpath.json")

    # Create a results dict
    results = {
        "engine_1": {
            "execution_time": exec_time1,
            "output_file_size": output_file_size1,
            "cpu_usage": cpu_usage1,
            "memory_usage": mem_usage1,
            "stdout": stdout1.decode('utf-8'),
            "stderr": stderr1.decode('utf-8')
        },
        "engine_2": {
            "execution_time": exec_time2,
            "output_file_size": output_file_size2,
            "cpu_usage": cpu_usage2,
            "memory_usage": mem_usage2,
            "stdout": stdout2.decode('utf-8'),
            "stderr": stderr2.decode('utf-8')
        }
    }

    # Print results in JSON format
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()

