import subprocess
import time
import json
import os
import statistics
import csv
from typing import Dict, List, Any
from datetime import datetime
from pprint import pprint as pp

NR_RUNS = 10

EXEC_OXPATH = "docker run --cpus=2 --memory=1g -d -v ./queries:/app --rm " \
              "oxpath-runtime -q simple.oxpath -o simple.json -f JSON -xvfb -mval -jsonarr"

EXEC_DRWEB = "docker run --cpus=2 --memory=1g -d -v ./queries:/app --rm starlitlog/dr-web-engine " \
             "-q simple.json5 -o simple.drweb.json --xvfb"

# PARAMS = [EXEC_OXPATH, 'simple.json', 'execution_results.json']
PARAMS = [EXEC_DRWEB, 'simple.drweb.json', 'execution_results.drweb.json']


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
        time.sleep(1)  # Sleep briefly

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


def parse_memory_usage(mem_str: str) -> float:
    """Parse memory usage string (e.g., '123.4MiB / 1GiB') to MB."""
    try:
        if '/' in mem_str:
            used_part = mem_str.split('/')[0].strip()
        else:
            used_part = mem_str.strip()
        
        if 'MiB' in used_part:
            return float(used_part.replace('MiB', '').strip())
        elif 'GiB' in used_part:
            return float(used_part.replace('GiB', '').strip()) * 1024
        elif 'KiB' in used_part:
            return float(used_part.replace('KiB', '').strip()) / 1024
        elif 'B' in used_part:
            return float(used_part.replace('B', '').strip()) / (1024 * 1024)
        else:
            return 0.0
    except (ValueError, AttributeError):
        return 0.0


def parse_cpu_usage(cpu_str: str) -> float:
    """Parse CPU usage string (e.g., '45.67%') to float."""
    try:
        return float(cpu_str.replace('%', '').strip())
    except (ValueError, AttributeError):
        return 0.0


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate comprehensive statistics for a list of values."""
    if not values:
        return {}
    
    return {
        'min': min(values),
        'max': max(values),
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
        'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
        'p99': statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
    }


def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze benchmark results and provide comprehensive statistics."""
    execution_times = [r['execution_time'] for r in results]
    file_sizes = [r['output_file_size'] for r in results if r['output_file_size'] is not None]
    
    # Parse CPU and memory usage
    all_cpu_usage = []
    all_memory_usage = []
    
    for result in results:
        cpu_values = [parse_cpu_usage(cpu) for cpu in result.get('cpu_usage', [])]
        memory_values = [parse_memory_usage(mem) for mem in result.get('memory_usage', [])]
        
        if cpu_values:
            all_cpu_usage.extend(cpu_values)
        if memory_values:
            all_memory_usage.extend(memory_values)
    
    # Calculate peak usage per run
    peak_cpu_per_run = []
    peak_memory_per_run = []
    avg_cpu_per_run = []
    avg_memory_per_run = []
    
    for result in results:
        cpu_values = [parse_cpu_usage(cpu) for cpu in result.get('cpu_usage', [])]
        memory_values = [parse_memory_usage(mem) for mem in result.get('memory_usage', [])]
        
        if cpu_values:
            peak_cpu_per_run.append(max(cpu_values))
            avg_cpu_per_run.append(statistics.mean(cpu_values))
        if memory_values:
            peak_memory_per_run.append(max(memory_values))
            avg_memory_per_run.append(statistics.mean(memory_values))
    
    analysis = {
        'benchmark_info': {
            'total_runs': len(results),
            'timestamp': datetime.now().isoformat(),
            'command': PARAMS[0] if 'PARAMS' in globals() else 'Unknown'
        },
        'execution_time': {
            'statistics': calculate_statistics(execution_times),
            'unit': 'seconds'
        },
        'output_file_size': {
            'statistics': calculate_statistics(file_sizes),
            'unit': 'bytes',
            'consistent': len(set(file_sizes)) == 1 if file_sizes else False
        },
        'resource_usage': {
            'peak_cpu_per_run': {
                'statistics': calculate_statistics(peak_cpu_per_run),
                'unit': 'percent'
            },
            'average_cpu_per_run': {
                'statistics': calculate_statistics(avg_cpu_per_run),
                'unit': 'percent'
            },
            'peak_memory_per_run': {
                'statistics': calculate_statistics(peak_memory_per_run),
                'unit': 'MB'
            },
            'average_memory_per_run': {
                'statistics': calculate_statistics(avg_memory_per_run),
                'unit': 'MB'
            }
        },
        'performance_insights': {
            'execution_time_variance': statistics.stdev(execution_times) / statistics.mean(execution_times) * 100 if execution_times and statistics.mean(execution_times) > 0 else 0.0,
            'consistent_output': len(set(file_sizes)) == 1 if file_sizes else False,
            'average_throughput': statistics.mean([size / time for size, time in zip(file_sizes, execution_times)]) if file_sizes and execution_times else 0.0
        }
    }
    
    return analysis


def generate_summary_report(analysis: Dict[str, Any]) -> str:
    """Generate a human-readable summary report."""
    exec_stats = analysis['execution_time']['statistics']
    resource_stats = analysis['resource_usage']
    insights = analysis['performance_insights']
    
    report = f"""
# Benchmark Analysis Report

## Summary
- **Total Runs**: {analysis['benchmark_info']['total_runs']}
- **Timestamp**: {analysis['benchmark_info']['timestamp']}
- **Command**: {analysis['benchmark_info']['command'][:80]}...

## Execution Time Analysis
- **Average**: {exec_stats.get('mean', 0):.2f}s
- **Median**: {exec_stats.get('median', 0):.2f}s
- **Min/Max**: {exec_stats.get('min', 0):.2f}s / {exec_stats.get('max', 0):.2f}s
- **Std Dev**: {exec_stats.get('std_dev', 0):.2f}s
- **95th Percentile**: {exec_stats.get('p95', 0):.2f}s
- **Variance**: {insights.get('execution_time_variance', 0):.1f}%

## Resource Usage
### Peak CPU Usage
- **Average Peak**: {resource_stats['peak_cpu_per_run']['statistics'].get('mean', 0):.1f}%
- **Max Peak**: {resource_stats['peak_cpu_per_run']['statistics'].get('max', 0):.1f}%

### Peak Memory Usage
- **Average Peak**: {resource_stats['peak_memory_per_run']['statistics'].get('mean', 0):.1f} MB
- **Max Peak**: {resource_stats['peak_memory_per_run']['statistics'].get('max', 0):.1f} MB

## Performance Insights
- **Consistent Output**: {'Yes' if insights.get('consistent_output') else 'No'}
- **Average Throughput**: {insights.get('average_throughput', 0):.2f} bytes/second
- **Performance Stability**: {'High' if insights.get('execution_time_variance', 100) < 10 else 'Medium' if insights.get('execution_time_variance', 100) < 25 else 'Low'}

## Recommendations
"""
    
    if insights.get('execution_time_variance', 100) > 25:
        report += "- High execution time variance detected. Consider investigating system load or resource contention.\n"
    
    if resource_stats['peak_memory_per_run']['statistics'].get('max', 0) > 500:
        report += "- High memory usage detected. Consider memory optimization.\n"
    
    if exec_stats.get('mean', 0) > 30:
        report += "- Long execution times detected. Consider performance optimization.\n"
    
    if not insights.get('consistent_output'):
        report += "- Inconsistent output file sizes detected. Investigate potential extraction issues.\n"
    
    return report


def export_to_csv(results: List[Dict[str, Any]], filename: str) -> None:
    """Export results to CSV format for further analysis."""
    if not results:
        return
    
    flattened_results = []
    for result in results:
        cpu_values = [parse_cpu_usage(cpu) for cpu in result.get('cpu_usage', [])]
        memory_values = [parse_memory_usage(mem) for mem in result.get('memory_usage', [])]
        
        flattened_result = {
            'run': result['execution_run'],
            'execution_time': result['execution_time'],
            'output_file_size': result.get('output_file_size'),
            'peak_cpu': max(cpu_values) if cpu_values else 0,
            'avg_cpu': statistics.mean(cpu_values) if cpu_values else 0,
            'peak_memory_mb': max(memory_values) if memory_values else 0,
            'avg_memory_mb': statistics.mean(memory_values) if memory_values else 0
        }
        flattened_results.append(flattened_result)
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['run', 'execution_time', 'output_file_size', 'peak_cpu', 'avg_cpu', 'peak_memory_mb', 'avg_memory_mb']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_results)


def get_output_file_size(output_file):
    """Get the size of the output file in bytes."""
    if os.path.exists(output_file):
        return os.path.getsize(output_file)
    else:
        return None  # File does not exist


def main():
    all_results = []  # Store results for all runs
    
    cmd = PARAMS[0]
    o_file = PARAMS[1]
    o_json = PARAMS[2]
    
    print(f"Starting benchmark with {NR_RUNS} runs...")
    print(f"Command: {cmd}")
    print("=" * 60)
    
    for i in range(NR_RUNS):
        print(f"\nRun {i + 1}/{NR_RUNS}")
        print("-" * 30)
        
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
        
        # Show quick stats for this run
        cpu_values = [parse_cpu_usage(cpu) for cpu in cpu_usage]
        mem_values = [parse_memory_usage(mem) for mem in mem_usage]
        
        print(f"Execution Time: {exec_time:.2f}s")
        print(f"Output Size: {output_file_size} bytes")
        print(f"Peak CPU: {max(cpu_values) if cpu_values else 0:.1f}%")
        print(f"Peak Memory: {max(mem_values) if mem_values else 0:.1f} MB")
        
        all_results.append(result)
    
    print("\n" + "=" * 60)
    print("Benchmark completed! Analyzing results...")
    
    # Save raw results to JSON
    with open(f'{o_json}', 'w') as json_file:
        json.dump(all_results, json_file, indent=4)
    print(f"Raw results saved to: {o_json}")
    
    # Generate comprehensive analysis
    analysis = analyze_results(all_results)
    analysis_file = o_json.replace('.json', '_analysis.json')
    with open(analysis_file, 'w') as json_file:
        json.dump(analysis, json_file, indent=4)
    print(f"Analysis saved to: {analysis_file}")
    
    # Generate summary report
    summary = generate_summary_report(analysis)
    summary_file = o_json.replace('.json', '_summary.md')
    with open(summary_file, 'w') as f:
        f.write(summary)
    print(f"Summary report saved to: {summary_file}")
    
    # Export to CSV for spreadsheet analysis
    csv_file = o_json.replace('.json', '_data.csv')
    export_to_csv(all_results, csv_file)
    print(f"CSV data exported to: {csv_file}")
    
    # Display summary in console
    print("\n" + summary)
    
    print("\nBenchmark analysis complete!")


if __name__ == "__main__":
    main()


