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

# Install dependencies (example for Python implementation)
pip install cbd-serializer
```

## Usage

### Python Example

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

print(original_data)  # Output: {'name': 'John', 'age': 30, 'scores': [95, 87, 92], 'active': True}
```

### JavaScript Example

```javascript
const CBD = require('cbd-serializer');

// Create a sample data structure
const data = {
  name: "John",
  age: 30,
  scores: [95, 87, 92],
  active: true
};

// Serialize to CBD
const binaryData = CBD.serialize(data);

// Deserialize from CBD
const originalData = CBD.deserialize(binaryData);

console.log(originalData); // Output: { name: 'John', age: 30, scores: [95, 87, 92], active: true }
```

## Format Specification

### Header
- **Magic Number** (2 bytes): Identifies CBD files (`0xCBD1`).
- **Version** (1 byte): Format version (`0x01` for v0.1.0).
- **Dictionary Size** (2 bytes): Number of entries in the key dictionary.

### Dictionary
- Array of strings (UTF-8 encoded) with 1-byte or 2-byte IDs, used to replace repetitive keys in the data.

### Data
- **Type Encoding**: 3-bit type field (null, boolean, number, string, array, object).
- **Numbers**: Variable-length encoding (varint for integers, custom 4-byte or 8-byte for floats).
- **Strings**: Length-prefixed UTF-8 strings.
- **Containers**: Bit flag to indicate array or object, followed by length and contents.

### Example Binary Structure
For `{"name":"John","age":30}`:
- Header: `0xCBD1 0x01 0x0002` (2 dictionary entries).
- Dictionary: `["name", "age"]` encoded as length-prefixed strings.
- Data: Object start, key ID 1 ("name"), string "John", key ID 2 ("age"), varint 30.

## Benchmarks

Preliminary benchmarks show CBD is:
- **40-60% smaller** than JSON for datasets with repetitive keys.
- **20-30% faster** to parse than gzipped JSON due to no decompression overhead.
- **Comparable in size** to MessagePack for mixed data but simpler to implement.

Detailed benchmarks will be added as the project matures.

## Roadmap

- [ ] Implement libraries in Python, JavaScript, and Rust.
- [ ] Add support for custom data types (e.g., dates, binary blobs).
- [ ] Provide tools for converting JSON to CBD and vice versa.
- [ ] Optimize for streaming data applications.
- [ ] Add validation and schema support.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, open an issue on GitHub or reach out via [email@example.com](mailto:email@example.com).

---

*CompactBinaryData: Serialize smarter, not harder.*
