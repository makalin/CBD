from format_converter import FormatConverter
import json

def main():
    # Example data
    data = {
        "name": "John Doe",
        "age": 30,
        "scores": [95, 87, 92],
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "country": "USA"
        },
        "active": True
    }
    
    # Convert between formats
    print("Original data:", json.dumps(data, indent=2))
    print("\nConverting between formats...")
    
    # JSON to CBD
    cbd_data = FormatConverter.json_to_cbd(data)
    print(f"\nJSON to CBD size: {len(cbd_data)} bytes")
    
    # CBD to MessagePack
    msgpack_data = FormatConverter.cbd_to_msgpack(cbd_data)
    print(f"CBD to MessagePack size: {len(msgpack_data)} bytes")
    
    # MessagePack to BSON
    bson_data = FormatConverter.msgpack_to_cbd(msgpack_data)
    bson_data = FormatConverter.cbd_to_bson(bson_data)
    print(f"MessagePack to BSON size: {len(bson_data)} bytes")
    
    # Compare all formats
    print("\nSize comparison for all formats:")
    results = FormatConverter.compare_formats(data)
    for format_name, size in results.items():
        print(f"{format_name:8}: {size:6} bytes")
    
    # Convert back to JSON to verify data integrity
    json_data = FormatConverter.cbd_to_json(cbd_data)
    print("\nVerifying data integrity...")
    print("Data matches:", json.loads(json_data) == data)

if __name__ == '__main__':
    main() 