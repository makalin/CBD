import struct
import json
from io import BytesIO

class CBD:
    # Type codes (3-bit, padded to 1 byte with container flag and value bits)
    TYPE_NULL = 0 << 5  # 000xxxxx
    TYPE_BOOL = 1 << 5  # 001xxxxx
    TYPE_NUMBER = 2 << 5  # 010xxxxx
    TYPE_STRING = 3 << 5  # 011xxxxx
    TYPE_ARRAY = 4 << 5 | 1  # 10000001 (container)
    TYPE_OBJECT = 5 << 5 | 1  # 10100001 (container)
    
    @staticmethod
    def _encode_varint(n):
        """Encode an integer as a variable-length integer."""
        if n < 0:
            raise ValueError("Negative numbers not supported")
        buf = []
        while n > 127:
            buf.append((n & 127) | 128)
            n >>= 7
        buf.append(n)
        return bytes(buf)
    
    @staticmethod
    def _decode_varint(buffer, pos):
        """Decode a variable-length integer from buffer at pos."""
        n = 0
        shift = 0
        while True:
            b = buffer[pos]
            pos += 1
            n |= (b & 127) << shift
            if not (b & 128):
                break
            shift += 7
        return n, pos
    
    @staticmethod
    def serialize(data):
        """Serialize data to CBD binary format."""
        buffer = BytesIO()
        
        # Header: Magic (0xCBD1), Version (0x01), Dictionary Size
        keys = []
        def collect_keys(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k not in keys:
                        keys.append(k)
                    collect_keys(v)
            elif isinstance(obj, list):
                for v in obj:
                    collect_keys(v)
        collect_keys(data)
        
        buffer.write(struct.pack(">HBB", 0xCBD1, 0x01, len(keys)))
        
        # Dictionary: length-prefixed strings
        for key in keys:
            key_bytes = key.encode('utf-8')
            buffer.write(CBD._encode_varint(len(key_bytes)))
            buffer.write(key_bytes)
        
        # Data
        def serialize_value(val):
            if val is None:
                buffer.write(struct.pack("B", CBD.TYPE_NULL))
            elif isinstance(val, bool):
                buffer.write(struct.pack("B", CBD.TYPE_BOOL | int(val)))
            elif isinstance(val, (int, float)):
                buffer.write(struct.pack("B", CBD.TYPE_NUMBER))
                buffer.write(CBD._encode_varint(int(val)))
            elif isinstance(val, str):
                val_bytes = val.encode('utf-8')
                buffer.write(struct.pack("B", CBD.TYPE_STRING))
                buffer.write(CBD._encode_varint(len(val_bytes)))
                buffer.write(val_bytes)
            elif isinstance(val, list):
                buffer.write(struct.pack("B", CBD.TYPE_ARRAY))
                buffer.write(CBD._encode_varint(len(val)))
                for item in val:
                    serialize_value(item)
            elif isinstance(val, dict):
                buffer.write(struct.pack("B", CBD.TYPE_OBJECT))
                buffer.write(CBD._encode_varint(len(val)))
                for k, v in val.items():
                    buffer.write(CBD._encode_varint(keys.index(k) + 1))
                    serialize_value(v)
            else:
                raise ValueError(f"Unsupported type: {type(val)}")
        
        serialize_value(data)
        return buffer.getvalue()
    
    @staticmethod
    def deserialize(binary):
        """Deserialize CBD binary data to Python object."""
        buffer = binary
        pos = 0
        
        # Read header
        magic, version, dict_size = struct.unpack_from(">HBB", buffer, pos)
        pos += 4
        if magic != 0xCBD1 or version != 0x01:
            raise ValueError("Invalid CBD format or version")
        
        # Read dictionary
        keys = []
        for _ in range(dict_size):
            length, pos = CBD._decode_varint(buffer, pos)
            key = buffer[pos:pos+length].decode('utf-8')
            keys.append(key)
            pos += length
        
        def deserialize_value():
            nonlocal pos
            type_byte = buffer[pos]
            pos += 1
            type_code = type_byte >> 5
            
            if type_code == 0:  # Null
                return None
            elif type_code == 1:  # Boolean
                return bool(type_byte & 1)
            elif type_code == 2:  # Number
                val, pos2 = CBD._decode_varint(buffer, pos)
                pos = pos2
                return val
            elif type_code == 3:  # String
                length, pos2 = CBD._decode_varint(buffer, pos)
                pos = pos2
                val = buffer[pos:pos+length].decode('utf-8')
                pos += length
                return val
            elif type_code == 4:  # Array
                length, pos2 = CBD._decode_varint(buffer, pos)
                pos = pos2
                return [deserialize_value() for _ in range(length)]
            elif type_code == 5:  # Object
                length, pos2 = CBD._decode_varint(buffer, pos)
                pos = pos2
                obj = {}
                for _ in range(length):
                    key_idx, pos2 = CBD._decode_varint(buffer, pos)
                    pos = pos2
                    obj[keys[key_idx-1]] = deserialize_value()
                return obj
            else:
                raise ValueError(f"Unknown type code: {type_code}")
        
        return deserialize_value()

# Test and measure sizes
if __name__ == "__main__":
    data = {
        "name": "John",
        "age": 30,
        "scores": [95, 87, 92],
        "active": True
    }
    
    # JSON size
    json_data = json.dumps(data, separators=(',', ':'))
    json_size = len(json_data.encode('utf-8'))
    
    # CBD size
    cbd_data = CBD.serialize(data)
    cbd_size = len(cbd_data)
    
    # Verify deserialization
    deserialized = CBD.deserialize(cbd_data)
    
    print(f"Original data: {data}")
    print(f"Deserialized data: {deserialized}")
    print(f"JSON size: {json_size} bytes")
    print(f"CBD size: {cbd_size} bytes")
    print(f"Size reduction: {(json_size - cbd_size) / json_size * 100:.2f}%")