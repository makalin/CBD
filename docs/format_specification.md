# CBD Format Specification

**Version**: 0.1.0  
**Status**: Draft

## Overview

CompactBinaryData (CBD) is a binary serialization format designed for efficient data storage and transmission. This document specifies the binary format in detail.

## Design Goals
- **Compactness**: Achieve 40-60% size reduction compared to JSON for datasets with repetitive keys.
- **Performance**: Minimize serialization/deserialization overhead with simple, binary parsing.
- **JSON Compatibility**: Support all JSON data types (null, boolean, number, string, array, object) with lossless round-tripping.
- **Extensibility**: Reserve space for future data types and custom extensions.
- **Simplicity**: Maintain a straightforward format for easy implementation across languages.

## File Structure

A CBD file consists of three main sections:
1. Header
2. Dictionary
3. Data

### Header (5 bytes)

```
+----------------+----------------+----------------+
| Magic Number   | Version       | Dict Size     |
| (2 bytes)      | (1 byte)      | (2 bytes)     |
+----------------+----------------+----------------+
```

- **Magic Number**: `0xCBD1` (2 bytes)
  - Identifies CBD files
  - Helps detect file corruption
- **Version**: `0x01` (1 byte)
  - Current format version
  - Enables future format evolution
- **Dictionary Size**: (2 bytes)
  - Number of entries in the key dictionary
  - Big-endian unsigned integer
  - Supports up to 65,535 unique keys

### Dictionary

The dictionary is an array of UTF-8 encoded strings, used to compress repetitive keys in the data.

```
+----------------+----------------+----------------+
| String Length  | UTF-8 String  | ... (repeated) |
| (1-2 bytes)    | (n bytes)     |                |
+----------------+----------------+----------------+
```

- **String Length**: Variable-length encoding
  - 1 byte if length < 128
  - 2 bytes if length >= 128 (first bit set to 1)
- **UTF-8 String**: The actual key string
- **Notes**: Keys are assigned 1-based numeric IDs (1, 2, 3, ...) based on their order in the dictionary

### Data

The data section contains the serialized data structure, using a type system and variable-length encoding.

#### Type Byte
The type byte is an 8-bit value that encodes the data type and additional metadata:
- **Bits 7-5 (3 bits)**: Type code (0-7)
- **Bit 0**: Container flag (1 for array/object, 0 for scalar types)
- **Bits 4-1**: Reserved for scalar types (e.g., boolean value or padding)

| Type          | Code (Binary) | Type Byte (Example) | Description                     |
|---------------|---------------|---------------------|---------------------------------|
| Null          | 000           | `0x00`              | Null value                      |
| Boolean       | 001           | `0x20` (false), `0x21` (true) | Boolean value (bit 0: 0=false, 1=true) |
| Number        | 010           | `0x40`              | Integer (varint encoding)       |
| String        | 011           | `0x60`              | UTF-8 string (length-prefixed)  |
| Array         | 100           | `0x81`              | Array (length-prefixed)         |
| Object        | 101           | `0xA1`              | Object (length-prefixed)        |
| Reserved      | 110, 111      | -                   | For future extensions           |

#### Number Encoding

Numbers use variable-length encoding:

```
+----------------+----------------+----------------+
| Type (010)     | Number Format  | Value         |
| (3 bits)       | (2 bits)       | (n bytes)     |
+----------------+----------------+----------------+
```

Number formats:
- `00`: 32-bit integer
- `01`: 64-bit integer
- `10`: 32-bit float
- `11`: 64-bit float

#### String Encoding

```
+----------------+----------------+----------------+
| Type (011)     | Length        | UTF-8 Data    |
| (3 bits)       | (n bytes)     | (n bytes)     |
+----------------+----------------+----------------+
```

- Length uses variable-length encoding (same as dictionary strings)

#### Array Encoding

```
+----------------+----------------+----------------+
| Type (100)     | Length        | Elements      |
| (3 bits)       | (n bytes)     | (n bytes)     |
+----------------+----------------+----------------+
```

- Length uses variable-length encoding
- Elements are encoded sequentially

#### Object Encoding

```
+----------------+----------------+----------------+
| Type (101)     | Length        | Key-Value     |
| (3 bits)       | (n bytes)     | Pairs         |
+----------------+----------------+----------------+
```

- Length uses variable-length encoding
- Key-Value pairs are encoded sequentially
- Keys are dictionary indices (1-2 bytes)

### Variable-Length Integer (Varint)
Varints encode unsigned integers compactly:
- Each byte uses 7 bits for data and 1 bit (MSB) to indicate continuation
- If MSB is 1, another byte follows; if 0, it's the last byte
- Example: The number 300 (`0x12C`) is encoded as:
  - First byte: `0xAC` (128 | 44, where 44 is `0x2C`)
  - Second byte: `0x02` (300 >> 7 = 2)
  - Total: `0xAC 0x02` (2 bytes)

## Examples

### Simple Object

Input JSON:
```json
{
    "name": "John",
    "age": 30
}
```

CBD Structure:
```
Header:
CBD1 01 0002

Dictionary:
02 6E 61 6D 65    # "name"
03 61 67 65       # "age"

Data:
101 02            # Object with 2 pairs
01 011 04 4A 6F 68 6E  # Key 1, String "John"
02 010 00 1E       # Key 2, Number 30
```

### Complex Example

Input JSON:
```json
{
  "name": "John",
  "age": 30,
  "scores": [95, 87, 92],
  "active": true
}
```

CBD Encoding:
- **Header** (5 bytes):
  - Magic: `0xCBD1` (2 bytes)
  - Version: `0x01` (1 byte)
  - Dictionary Size: `0x0004` (2 bytes, 4 keys)
- **Dictionary** (22 bytes):
  - "name": `0x04`, `6E 61 6D 65` = 5 bytes
  - "age": `0x03`, `61 67 65` = 4 bytes
  - "scores": `0x06`, `73 63 6F 72 65 73` = 7 bytes
  - "active": `0x06`, `61 63 74 69 76 65` = 7 bytes
- **Data** (19 bytes):
  - Object: `0xA1`, `0x04` = 2 bytes
  - Pair 1: Key ID `0x01`, String `0x60`, `0x04`, `4A 6F 68 6E` = 6 bytes
  - Pair 2: Key ID `0x02`, Number `0x40`, `0x1E` = 3 bytes
  - Pair 3: Key ID `0x03`, Array `0x81`, `0x03`, Numbers = 9 bytes
  - Pair 4: Key ID `0x04`, Boolean `0x21` = 2 bytes
- **Total Size**: 46 bytes (vs. 54 bytes for JSON)

## Implementation Notes

1. **Endianness**: All multi-byte values are stored in big-endian format.
2. **Dictionary**: Keys are stored in order of first appearance.
3. **Type System**: The 3-bit type system allows for future extensions.
4. **Variable-Length Encoding**: Optimizes space for small values.
5. **UTF-8**: All strings are UTF-8 encoded for maximum compatibility.

### Implementation Guidelines
- **Serialization**:
  1. Collect unique keys into a dictionary, assigning 1-based indices
  2. Write header (magic, version, dictionary size)
  3. Write dictionary (length-prefixed strings)
  4. Recursively serialize data, using type bytes and varints
- **Deserialization**:
  1. Validate magic number and version
  2. Read dictionary into an array for key lookup
  3. Recursively parse data based on type bytes
- **Error Handling**:
  - Check for invalid type codes
  - Validate dictionary indices
  - Handle truncated data
  - Ensure varint decoding doesn't exceed buffer length

## Limitations
- v0.1.0 supports only unsigned integers; floating-point numbers require a future extension
- Small datasets may have comparable size to JSON due to dictionary overhead
- Dictionary size limited to 65,535 unique keys

## Version History

- **0.1.0**: Initial release
  - Basic type system
  - Dictionary compression
  - Variable-length encoding

## Future Extensions

The format reserves:
- Two type codes (110, 111) for future use
- Additional bits in the header for future features
- Space for custom type extensions

Planned extensions:
- **Floating-Point Numbers**: Add compact float encoding
- **Custom Types**: Use reserved type codes for dates, binary data
- **Streaming Support**: Enable parsing of partial data
- **Schema Support**: Optional schemas for validation

## License
This specification is released under the MIT License. Implementations must adhere to the version specified in the header to ensure compatibility.

## Contact
For feedback or questions, open an issue at [github.com/makalin/CBD](https://github.com/makalin/CBD) or email [makalin@gmail.com](mailto:makalin@gmail.com).

---
*CompactBinaryData: Serialize smarter, not harder.* 