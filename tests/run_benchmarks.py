import subprocess
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def run_benchmarks():
    # First generate test data
    subprocess.run(['python', 'tests/data/generate_test_data.py'])
    
    # Run pytest benchmarks
    result = subprocess.run(
        ['pytest', 'tests/benchmarks/benchmark_serialization.py', '-v', '--benchmark-only', '--benchmark-json=benchmark_results.json'],
        capture_output=True,
        text=True
    )
    
    print("Benchmark output:")
    print(result.stdout)
    
    if result.stderr:
        print("Errors:")
        print(result.stderr)

def generate_plots():
    # Load benchmark results
    with open('benchmark_results.json', 'r') as f:
        results = json.load(f)
    
    # Create plots directory
    plots_dir = Path('tests/plots')
    plots_dir.mkdir(exist_ok=True)
    
    # Extract data for plotting
    datasets = set()
    formats = ['json', 'orjson', 'ujson', 'msgpack', 'bson', 'cbd']
    times = {fmt: [] for fmt in formats}
    sizes = {fmt: [] for fmt in formats}
    
    for bench in results['benchmarks']:
        name = bench['name']
        if 'serialization' in name:
            dataset = name.split('[')[1].split(']')[0]
            datasets.add(dataset)
            format_name = name.split('_')[1]
            times[format_name].append(bench['stats']['mean'])
            sizes[format_name].append(bench['stats']['ops'])
    
    # Plot serialization times
    plt.figure(figsize=(12, 6))
    x = np.arange(len(datasets))
    width = 0.15
    
    for i, fmt in enumerate(formats):
        plt.bar(x + i*width, times[fmt], width, label=fmt)
    
    plt.xlabel('Dataset')
    plt.ylabel('Time (seconds)')
    plt.title('Serialization Time Comparison')
    plt.xticks(x + width*2.5, datasets, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'serialization_times.png')
    
    # Plot data sizes
    plt.figure(figsize=(12, 6))
    for i, fmt in enumerate(formats):
        plt.bar(x + i*width, sizes[fmt], width, label=fmt)
    
    plt.xlabel('Dataset')
    plt.ylabel('Size (bytes)')
    plt.title('Serialized Data Size Comparison')
    plt.xticks(x + width*2.5, datasets, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'data_sizes.png')

if __name__ == '__main__':
    run_benchmarks()
    generate_plots() 