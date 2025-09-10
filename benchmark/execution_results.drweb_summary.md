
# Benchmark Analysis Report

## Summary
- **Total Runs**: 10
- **Timestamp**: 2025-09-09T22:03:11.680142
- **Command**: docker run --cpus=2 --memory=1g -d -v ./queries:/app --rm starlitlog/dr-web-engi...

## Execution Time Analysis
- **Average**: 4.14s
- **Median**: 3.04s
- **Min/Max**: 2.67s / 8.70s
- **Std Dev**: 2.16s
- **95th Percentile**: 8.70s
- **Variance**: 52.2%

## Resource Usage
### Peak CPU Usage
- **Average Peak**: 45.3%
- **Max Peak**: 67.8%

### Peak Memory Usage
- **Average Peak**: 141.0 MB
- **Max Peak**: 158.6 MB

## Performance Insights
- **Consistent Output**: No
- **Average Throughput**: 157.98 bytes/second
- **Performance Stability**: Low

## Recommendations
- High execution time variance detected. Consider investigating system load or resource contention.
- Inconsistent output file sizes detected. Investigate potential extraction issues.
