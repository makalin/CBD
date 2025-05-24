# CompactBinaryData (CBD) Format Specification

**Version**: 0.1.0  
**Status**: Draft

CompactBinaryData (CBD) is a binary serialization format designed to provide a compact, JSON-compatible alternative for data exchange and storage. It achieves size efficiency through dictionary encoding of keys, bit-packed type identifiers, and variable-length number encoding, without relying on external compression algorithms like gzip. This specification defines the binary structure, encoding rules, and conventions for CBD.

## Design Goals
- **Compactness**: Achieve 40-60% size reduction compared to JSON for datasets with repetitive keys.
- **Performance**: Minimize serialization/deserialization overhead with simple, binary parsing.
- **JSON Compatibility**: Support all JSON data types (null, boolean, number, string, array, object) with lossless round-tripping.
- **Extensibility**: Reserve space for future data types and custom extensions.
- **Simplicity**: Maintain a straightforward format for easy implementation across languages.

## Binary Structure
A CBD document consists of three main sections, encoded sequentially in a binary stream:
1. **Header**: Identifies the format, version, and dictionary size.
2. **Dictionary**: Maps string keys to numeric IDs to reduce redundancy.
3. **Data**: Encodes the actual data using type identifiers and values.

### 1. Header
The header is a fixed-length structure that provides metadata about the CBD document.

| Field             | Size (bytes) | Description                              |
|-------------------|--------------|------------------------------------------|
| Magic Number      | 2            | Fixed value `0xCBD1` to identify CBD format. |
| Version           | 1            | Format version (`0x01` for v0.1.0).      |
| Dictionary Size   | 2            | Number of keys in the dictionary (uint16, big-endian). |

- **Total Size**: 5 bytes.
- **Notes**: The magic number ensures file type identification. The version allows for future extensions. Dictionary size is encoded as a 16-bit unsigned integer to support up to 65,535 unique keys.

### 2. Dictionary
The dictionary is a sequence of length-prefixed UTF-8 strings representing keys used in the data section. Each key is assigned a 1-based numeric ID (1, 2, 3, ...) based on its order in the dictionary.

| Field             | Size (bytes) | Description                              |
|-------------------|--------------|------------------------------------------|
| Length            | Variable     | Length of the key string (varint).       |
| Key               | Variable     | UTF-8 encoded string.                    |

- **Encoding**:
  - **Length**: A variable-length unsigned integer (varint, see below) indicating the number of bytes in the key string.
  - **Key**: The UTF-8 encoded string (e.g., "name", "age").
- **Notes**: The dictionary is written once at the start of the document. Keys are referenced by their 1-based index in the data section, reducing redundancy for repetitive keys.

### 3. Data
The data section encodes the actual data structure (object, array, or scalar) using a recursive structure. Each value is prefixed with a type byte.

#### Type Byte
The type byte is an 8-bit value that encodes the data type and additional metadata:
- **Bits 7-5 (3 bits)**: Type code (0-7).
- **Bit 0**: Container flag (1 for array/object, 0 for scalar types like null, boolean, number, string).
- **Bits 4-1**: Reserved for scalar types (e.g., boolean value or padding).

| Type          | Code (Binary) | Type Byte (Example) | Description                     |
|---------------|---------------|---------------------|---------------------------------|
| Null          | 000           | `0x00`              | Null value.                     |
| Boolean       | 001           | `0x20` (false), `0x21` (true) | Boolean value (bit 0: 0=false, 1=true). |
| Number        | 010           | `0x40`              | Integer (varint encoding).      |
| String        | 011           | `0x60`              | UTF-8 string (length-prefixed). |
| Array         | 100           | `0x81`              | Array (length-prefixed).        |
| Object        | 101           | `0xA1`              | Object (length-prefixed).       |
| Reserved      | 110, 111      | -                   | For future extensions.          |

#### Data Encoding
- **Null**: Type byte (`0x00`), no additional data.
- **Boolean**: Type byte (`0x20` for false, `0x21` for true).
- **Number**: Type byte (`0x40`), followed by a varint-encoded unsigned integer. (Note: v0.1.0 supports only integers; floats are planned for future versions.)
- **String**: Type byte (`0x60`), followed by a varint-encoded length, then the UTF-8 encoded string.
- **Array**: Type byte (`0x81`), followed by a varint-encoded length (number of elements), then the sequence of elements (each with its own type byte).
- **Object**: Type byte (`0xA1`), followed by a varint-encoded length (number of key-value pairs), then a sequence of key-value pairs. Each pair consists of a varint-encoded key ID (1-based dictionary index) and a value (with its own type byte).

#### Variable-Length Integer (Varint)
Varints encode unsigned integers compactly:
- Each byte uses 7 bits for data and 1 bit (MSB) to indicate continuation.
- If MSB is 1, another byte follows; if 0, it’s the last byte.
- Example: The number 300 (`0x12C`) is encoded as:
  - First byte: `0xAC` (128 | 44, where 44 is `0x2C`).
  - Second byte: `0x02` (300 >> 7 = 2).
  - Total: `0xAC 0x02` (2 bytes).

### Example: Sample Data
For the JSON data:
```json
{
  "name": "John",
  "age": 30,
  "scores": [95, 87, 92],
  "active": true
}
```

#### CBD Encoding
- **Header** (5 bytes):
  - Magic: `0xCBD1` (2 bytes).
  - Version: `0x01` (1 byte).
  - Dictionary Size: `0x0004` (2 bytes, 4 keys: "name", "age", "scores", "active").
- **Dictionary** (22 bytes):
  - "name": `0x04` (length 4), `6E 61 6D 65` (UTF-8 "name") = 5 bytes.
  - "age": `0x03`, `61 67 65` = 4 bytes.
  - "scores": `0x06`, `73 63 6F 72 65 73` = 7 bytes.
  - "active": `0x06`, `61 63 74 69 76 65` = 7 bytes.
- **Data** (19 bytes):
  - Object: `0xA1` (type byte), `0x04` (4 key-value pairs) = 2 bytes.
  - Pair 1: Key ID `0x01` (name), String `0x60`, `0x04`, `4A 6F 68 6E` (John) = 6 bytes.
  - Pair 2: Key ID `0x02` (age), Number `0x40`, `0x1E` (30) = 3 bytes.
  - Pair 3: Key ID `0x03` (scores), Array `0x81`, `0x03` (3 elements), Numbers (`0x40`, `0x5F` for 95; `0x40`, `0x57` for 87; `0x40`, `0x5C` for 92) = 9 bytes.
  - Pair 4: Key ID `0x04` (active), Boolean `0x21` (true) = 2 bytes.
- **Total Size**: 5 + 22 + 19 = **46 bytes**.

#### JSON Comparison
- JSON (UTF-8, minimal whitespace): `{"name":"John","age":30,"scores":[95,87,92],"active":true}` = **54 bytes**.
- **Size Reduction**: (54 - 46) / 54 × 100 ≈ **14.81%**.

### Notes
- **Size Efficiency**: CBD’s dictionary encoding shines with repetitive keys (e.g., arrays of objects with the same keys). For the sample, the dictionary (22 bytes) is a significant overhead, but in larger datasets, it amortizes across repeated key references.
- **Limitations**:
  - v0.1.0 supports only unsigned integers; floating-point numbers require a future extension.
  - Small datasets may have comparable size to JSON due to dictionary overhead.
- **Extensibility**: Reserved type codes (110, 111) allow for future types (e.g., dates, binary blobs).
- **Validation**: Implementations must check the magic number and version, ensure dictionary indices are valid, and handle varint overflow.

### Implementation Guidelines
- **Serialization**:
  1. Collect unique keys into a dictionary, assigning 1-based indices.
  2. Write header (magic, version, dictionary size).
  3. Write dictionary (length-prefixed strings).
  4. Recursively serialize data, using type bytes and varints.
- **Deserialization**:
  1. Validate magic number and version.
  2. Read dictionary into an array for key lookup.
  3. Recursively parse data based on type bytes, reconstructing the structure.
- **Error Handling**:
  - Check for invalid type codes, out-of-bounds dictionary indices, or truncated data.
  - Ensure varint decoding does not exceed buffer length.
- **Libraries**: Reference implementations are available in Python (see [cbd_serializer.py](https://github.com/makalin/CBD/blob/main/cbd_serializer.py)). Ports to JavaScript and Rust are planned.

### Example Binary Dump
For the sample data, the CBD binary stream (in hex) is:
```
CB D1 01 00 04 04 6E 61 6D 65 03 61 67 65 06 73 63 6F 72 65 73 06 61 63 74 69 76 65 A1 04 01 60 04 4A 6F 68 6E 02 40 1E 03 81 03 40 5F 40 57 40 5C 04 21
```

### Future Extensions
- **Floating-Point Numbers**: Add a compact float encoding (e.g., 4-byte or 8-byte IEEE 754).
- **Custom Types**: Use reserved type codes for dates, binary data, or user-defined types.
- **Streaming Support**: Enable parsing of partial or streaming data.
- **Schema Support**: Introduce optional schemas for validation and optimization.

## License
This specification is released under the MIT License. Implementations must adhere to the version specified in the header to ensure compatibility.

## Contact
For feedback or questions, open an issue at [github.com/makalin/CBD](https://github.com/makalin/CBD) or email [makalin@gmail.com](mailto:makalin@gmail.com).

---
*CompactBinaryData: Serialize smarter, not harder.*
