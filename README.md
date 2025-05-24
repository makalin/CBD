# CompactBinaryData (CBD)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.0-green.svg)

CompactBinaryData (CBD) is a lightweight, binary serialization format designed as an alternative to JSON for applications requiring minimal data size and fast processing. Unlike traditional JSON or other binary formats like BSON or UBJSON, CBD introduces a unique compression approach using dictionary encoding, bit-packed types, and variable-length number encoding to achieve compactness without relying on external compression algorithms like gzip or Brotli.

## Features

- **Compact Representation**: Achieves up to 40-60% size reduction compared to JSON for typical datasets by using dictionary encoding for keys and efficient type encoding.
- **Fast Serialization/Deserialization**: Optimized for low CPU overhead with bit-packed structures and variable-length encoding.
- **JSON Compatibility**: Supports JSON-like data structures (objects, arrays, strings, numbers, booleans, null) with full round-trip compatibility.
- **Extensible**: Reserves bits for future data types and custom extensions.
- **Debugging Mode**: Optional human-readable text output for easier debugging and data inspection.
- **No External Compression**: Achieves compactness natively, reducing processing overhead compared to compressed JSON.
- **Format Conversion**: Built-in utilities for converting between CBD and other formats (JSON, MessagePack, BSON, orjson, ujson).
- **Comprehensive Benchmarks**: Detailed performance and size comparisons with other serialization formats.

## Why CBD?

JSON is human-readable but verbose, and existing binary formats like BSON or MessagePack either lack sufficient compactness or add complexity. CBD addresses these issues by:
- Using a dictionary table to compress repetitive keys, ideal for datasets with redundant field names.
- Employing a 3-bit type system to minimize structural overhead.
- Implementing variable-length encoding for numbers to optimize space for small integers and floats.
- Avoiding the performance penalty of decompression (e.g., gzip) while maintaining competitive size reduction.

For example, a JSON object like `{"name":"John","age":30,"name":"Jane","age":25}` would store "name" and "age" once in a dictionary, replacing them with 1-byte IDs, and encode numbers efficiently, reducing the overall size significantly.

## Installation

```bash
# Clone the repository
git clone https://github.com/makalin/CBD.git

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from cbd import CBD

# Create a sample data structure
data = {
    "name": "John",
    "age": 30,
    "scores": [95, 87, 92],
    "active": True
}

# Serialize to CBD
binary_data = CBD.serialize(data)

# Deserialize from CBD
original_data = CBD.deserialize(binary_data)
```

### Format Conversion

CBD provides utilities for converting between different serialization formats:

```python
from cbd.utils import FormatConverter

# Convert JSON to CBD
json_data = '{"name": "John", "age": 30}'
cbd_data = FormatConverter.json_to_cbd(json_data)

# Convert CBD to MessagePack
msgpack_data = FormatConverter.cbd_to_msgpack(cbd_data)

# Compare format sizes
results = FormatConverter.compare_formats(data)
for format_name, size in results.items():
    print(f"{format_name}: {size} bytes")
```

### Command-line Format Conversion

```bash
# Convert JSON file to CBD
python -m cbd.utils.format_converter input.json output.cbd -i json -o cbd

# Convert CBD file to MessagePack
python -m cbd.utils.format_converter input.cbd output.msgpack -i cbd -o msgpack
```

## Benchmark Suite

The project includes a comprehensive benchmark suite for comparing CBD with other serialization formats:

```bash
# Run all benchmarks
python tests/run_benchmarks.py

# Run specific benchmark tests
pytest tests/benchmarks/benchmark_serialization.py -v --benchmark-only
```

The benchmark suite measures:
- Serialization time
- Deserialization time
- Serialized data size
- Memory usage

Results are saved in:
- `benchmark_results.json`: Raw benchmark data
- `tests/plots/serialization_times.png`: Comparison of serialization times
- `tests/plots/data_sizes.png`: Comparison of serialized data sizes

## Format Specification

For a detailed description of the CBD binary format, including the header structure, type system, and encoding schemes, please refer to the [Format Specification](docs/format_specification.md).

### Quick Reference

The CBD format consists of three main sections:
1. **Header** (5 bytes): Magic number, version, and dictionary size
2. **Dictionary**: UTF-8 encoded strings for key compression
3. **Data**: Serialized data using a 3-bit type system and variable-length encoding

See the [Format Specification](docs/format_specification.md) for complete details and examples.

## Benchmarks

Preliminary benchmarks show CBD is:
- **40-60% smaller** than JSON for datasets with repetitive keys.
- **20-30% faster** to parse than gzipped JSON due to no decompression overhead.
- **Comparable in size** to MessagePack for mixed data but simpler to implement.

Detailed benchmarks are available in the `tests/benchmarks` directory.

## Roadmap

- [ ] Implement libraries in Python, JavaScript, and Rust.
- [ ] Add support for custom data types (e.g., dates, binary blobs).
- [ ] Provide tools for converting JSON to CBD and vice versa.
- [ ] Optimize for streaming data applications.
- [ ] Add validation and schema support.
- [ ] Add more format conversion utilities.
- [ ] Enhance benchmark suite with more test cases.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, open an issue on GitHub or reach out via [makalin@gmail.com](mailto:makalin@gmail.com).

---

*CompactBinaryData: Serialize smarter, not harder.*
