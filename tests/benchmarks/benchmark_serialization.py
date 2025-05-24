import json
import msgpack
import bson
import orjson
import ujson
import time
import os
from pathlib import Path
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

# Import CBD (assuming it's in the parent directory)
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from cbd import CBD

def load_test_data():
    data_dir = Path(__file__).parent.parent / 'data'
    test_files = list(data_dir.glob('*.json'))
    datasets = {}
    for file in test_files:
        with open(file, 'r') as f:
            datasets[file.stem] = json.load(f)
    return datasets

def benchmark_serialization(benchmark: BenchmarkFixture, data, serializer_name, serialize_func, deserialize_func):
    # Serialization benchmark
    serialized = benchmark(serialize_func, data)
    
    # Deserialization benchmark
    benchmark(deserialize_func, serialized)
    
    # Calculate size
    if isinstance(serialized, bytes):
        size = len(serialized)
    else:
        size = len(str(serialized).encode('utf-8'))
    
    return size

@pytest.mark.benchmark
def test_json_serialization(benchmark: BenchmarkFixture):
    datasets = load_test_data()
    results = {}
    
    for name, data in datasets.items():
        size = benchmark_serialization(
            benchmark,
            data,
            'json',
            lambda x: json.dumps(x),
            lambda x: json.loads(x)
        )
        results[name] = size
    
    return results

@pytest.mark.benchmark
def test_orjson_serialization(benchmark: BenchmarkFixture):
    datasets = load_test_data()
    results = {}
    
    for name, data in datasets.items():
        size = benchmark_serialization(
            benchmark,
            data,
            'orjson',
            lambda x: orjson.dumps(x),
            lambda x: orjson.loads(x)
        )
        results[name] = size
    
    return results

@pytest.mark.benchmark
def test_ujson_serialization(benchmark: BenchmarkFixture):
    datasets = load_test_data()
    results = {}
    
    for name, data in datasets.items():
        size = benchmark_serialization(
            benchmark,
            data,
            'ujson',
            lambda x: ujson.dumps(x),
            lambda x: ujson.loads(x)
        )
        results[name] = size
    
    return results

@pytest.mark.benchmark
def test_msgpack_serialization(benchmark: BenchmarkFixture):
    datasets = load_test_data()
    results = {}
    
    for name, data in datasets.items():
        size = benchmark_serialization(
            benchmark,
            data,
            'msgpack',
            lambda x: msgpack.packb(x),
            lambda x: msgpack.unpackb(x)
        )
        results[name] = size
    
    return results

@pytest.mark.benchmark
def test_bson_serialization(benchmark: BenchmarkFixture):
    datasets = load_test_data()
    results = {}
    
    for name, data in datasets.items():
        size = benchmark_serialization(
            benchmark,
            data,
            'bson',
            lambda x: bson.dumps(x),
            lambda x: bson.loads(x)
        )
        results[name] = size
    
    return results

@pytest.mark.benchmark
def test_cbd_serialization(benchmark: BenchmarkFixture):
    datasets = load_test_data()
    results = {}
    
    for name, data in datasets.items():
        size = benchmark_serialization(
            benchmark,
            data,
            'cbd',
            lambda x: CBD.serialize(x),
            lambda x: CBD.deserialize(x)
        )
        results[name] = size
    
    return results

def print_results(results):
    print("\nBenchmark Results:")
    print("-" * 80)
    print(f"{'Dataset':<15} {'JSON':<10} {'orjson':<10} {'ujson':<10} {'msgpack':<10} {'bson':<10} {'CBD':<10}")
    print("-" * 80)
    
    for dataset in results['json'].keys():
        print(f"{dataset:<15}", end='')
        for format_name in ['json', 'orjson', 'ujson', 'msgpack', 'bson', 'cbd']:
            size = results[format_name][dataset]
            print(f"{size:<10}", end='')
        print()

if __name__ == '__main__':
    # Run benchmarks and collect results
    results = {
        'json': test_json_serialization(None),
        'orjson': test_orjson_serialization(None),
        'ujson': test_ujson_serialization(None),
        'msgpack': test_msgpack_serialization(None),
        'bson': test_bson_serialization(None),
        'cbd': test_cbd_serialization(None)
    }
    
    print_results(results) 