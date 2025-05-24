# CBD Benchmark Suite

This directory contains the benchmark suite for comparing CompactBinaryData (CBD) with other serialization formats.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the CBD implementation in the parent directory.

## Running Benchmarks

To run the benchmarks and generate comparison plots:

```bash
python tests/run_benchmarks.py
```

This will:
1. Generate test datasets of various sizes and types
2. Run benchmarks comparing CBD with JSON, orjson, ujson, MessagePack, and BSON
3. Generate comparison plots in the `tests/plots` directory

## Test Data

The benchmark suite uses several types of test data:
- Small dictionaries (shallow)
- Medium dictionaries (moderate nesting)
- Large dictionaries (deep nesting)
- Small arrays (100 items)
- Medium arrays (1000 items)
- Large arrays (10000 items)
- Mixed data (strings, numbers, booleans, nulls, nested structures)

## Benchmark Results

The benchmarks measure:
1. Serialization time
2. Deserialization time
3. Serialized data size

Results are saved in:
- `benchmark_results.json`: Raw benchmark data
- `tests/plots/serialization_times.png`: Comparison of serialization times
- `tests/plots/data_sizes.png`: Comparison of serialized data sizes

## Running Individual Tests

To run specific benchmark tests:

```bash
pytest tests/benchmarks/benchmark_serialization.py -v --benchmark-only
```

To run a specific test:

```bash
pytest tests/benchmarks/benchmark_serialization.py::test_cbd_serialization -v --benchmark-only
```

## Adding New Tests

To add new benchmark tests:
1. Add new test data generation in `tests/data/generate_test_data.py`
2. Add new benchmark functions in `tests/benchmarks/benchmark_serialization.py`
3. Update the plotting code in `tests/run_benchmarks.py` if necessary 