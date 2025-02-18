import subprocess
import time
import json
import os
from pprint import pprint as pp

NR_RUNS = 10

EXEC_OXPATH = "docker run --cpus=2 --memory=1g -d -v ./queries:/app --rm " \
              "starlitlog/oxpath-runtime -q simple.oxpath -o simple.json -f JSON -xvfb -mval -jsonarr"

EXEC_DRWEB = "docker run --cpus=2 --memory=1g -d -v ./queries:/app --rm starlitlog/dr-web-engine " \
             "-q simple.json5 -o simple.drweb.json --xvfb"

PARAMS = [EXEC_OXPATH, 'simple.json', 'execution_results.json']
# PARAMS = [EXEC_DRWEB, 'simple.drweb.json', 'execution_results.drweb.json']


def run_command(command):
    """Run the command and capture the execution metrics."""
    start_time = time.time()

    # Split the command into a list
    command_list = command.split()

    # Run Docker command in detached mode
    process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Capture the container ID
    container_id, _ = process.communicate()
    container_id = container_id.strip().decode('utf-8')

    if not container_id:
        raise ValueError("Failed to get container ID. Ensure the Docker command is correct.")

    cpu_usage = []
    mem_usage = []

    # Monitor the process
    while True:
        time.sleep(0.1)  # Sleep briefly

        # Get CPU and memory usage via docker stats
        stats = subprocess.Popen(
            ['docker', 'stats', container_id, '--no-stream', '--format', '{{.CPUPerc}} {{.MemUsage}}'],
            stdout=subprocess.PIPE)
        output, _ = stats.communicate()  # Capture the output

        # Decode and output control
        cpu_mem = output.decode('utf-8').strip()
        print(f"Docker stats output: '{cpu_mem}'")  # Debug print

        if cpu_mem:
            try:
                parts = cpu_mem.split()
                cpu = parts[0]  # CPU percentage
                mem = parts[1]  # Memory usage
                cpu_usage.append(cpu)
                mem_usage.append(mem)
            except ValueError:
                print(f"Unexpected format: '{cpu_mem}'")
                continue  # Skip the rest of this loop if format is unexpected

        # Check the container's running state
        container_status = subprocess.run(['docker', 'inspect', '-f', '{{.State.Running}}', container_id],
                                          stdout=subprocess.PIPE, text=True)
        if container_status.stdout.strip() != 'true':
            break

    end_time = time.time()
    execution_time = end_time - start_time  # Total execution time in seconds

    return execution_time, cpu_usage, mem_usage

    return execution_time, cpu_usage, mem_usage


def get_output_file_size(output_file):
    """Get the size of the output file in bytes."""
    if os.path.exists(output_file):
        return os.path.getsize(output_file)
    else:
        return None  # File does not exist


def main():
    all_results = []  # Store results for all 100 executions

    cmd = PARAMS[0]
    o_file = PARAMS[1]
    o_json = PARAMS[2]

    for i in range(NR_RUNS):  # Run command 100 times
        exec_time, cpu_usage, mem_usage = run_command(cmd)

        # Get output file size
        output_file_size = get_output_file_size(f"queries/{o_file}")

        # Create a results dict for this execution
        result = {
            "execution_run": i + 1,
            "execution_time": exec_time,
            "output_file_size": output_file_size,
            "cpu_usage": cpu_usage,
            "memory_usage": mem_usage
        }

        pp(result)

        all_results.append(result)  # Append each run's results to the list

    # Print results in JSON format
    with open(f'{o_json}', 'w') as json_file:
        json.dump(all_results, json_file, indent=4)


if __name__ == "__main__":
    main()


