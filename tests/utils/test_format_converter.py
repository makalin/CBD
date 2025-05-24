import pytest
import json
import msgpack
import bson
import orjson
import ujson
from pathlib import Path
import tempfile
import os

from .format_converter import FormatConverter

# Test data
TEST_DATA = {
    "string": "Hello, World!",
    "number": 42,
    "float": 3.14159,
    "boolean": True,
    "null": None,
    "array": [1, 2, 3, 4, 5],
    "object": {
        "nested": {
            "key": "value"
        }
    }
}

def test_json_conversion():
    # Test JSON to CBD
    json_str = json.dumps(TEST_DATA)
    cbd_data = FormatConverter.json_to_cbd(json_str)
    assert isinstance(cbd_data, bytes)
    
    # Test CBD to JSON
    json_data = FormatConverter.cbd_to_json(cbd_data)
    assert isinstance(json_data, str)
    assert json.loads(json_data) == TEST_DATA

def test_msgpack_conversion():
    # Test MessagePack to CBD
    msgpack_data = msgpack.packb(TEST_DATA)
    cbd_data = FormatConverter.msgpack_to_cbd(msgpack_data)
    assert isinstance(cbd_data, bytes)
    
    # Test CBD to MessagePack
    msgpack_data = FormatConverter.cbd_to_msgpack(cbd_data)
    assert isinstance(msgpack_data, bytes)
    assert msgpack.unpackb(msgpack_data) == TEST_DATA

def test_bson_conversion():
    # Test BSON to CBD
    bson_data = bson.dumps(TEST_DATA)
    cbd_data = FormatConverter.bson_to_cbd(bson_data)
    assert isinstance(cbd_data, bytes)
    
    # Test CBD to BSON
    bson_data = FormatConverter.cbd_to_bson(cbd_data)
    assert isinstance(bson_data, bytes)
    assert bson.loads(bson_data) == TEST_DATA

def test_orjson_conversion():
    # Test orjson to CBD
    orjson_data = orjson.dumps(TEST_DATA)
    cbd_data = FormatConverter.orjson_to_cbd(orjson_data)
    assert isinstance(cbd_data, bytes)
    
    # Test CBD to orjson
    orjson_data = FormatConverter.cbd_to_orjson(cbd_data)
    assert isinstance(orjson_data, bytes)
    assert orjson.loads(orjson_data) == TEST_DATA

def test_ujson_conversion():
    # Test ujson to CBD
    ujson_str = ujson.dumps(TEST_DATA)
    cbd_data = FormatConverter.ujson_to_cbd(ujson_str)
    assert isinstance(cbd_data, bytes)
    
    # Test CBD to ujson
    ujson_data = FormatConverter.cbd_to_ujson(cbd_data)
    assert isinstance(ujson_data, str)
    assert ujson.loads(ujson_data) == TEST_DATA

def test_file_conversion():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        input_file = os.path.join(temp_dir, 'input.json')
        output_file = os.path.join(temp_dir, 'output.cbd')
        
        # Write test data to input file
        with open(input_file, 'w') as f:
            json.dump(TEST_DATA, f)
        
        # Convert JSON to CBD
        FormatConverter.convert_file(input_file, output_file, 'json', 'cbd')
        
        # Verify output file exists and contains data
        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0
        
        # Convert back to JSON and verify
        output_json = os.path.join(temp_dir, 'output.json')
        FormatConverter.convert_file(output_file, output_json, 'cbd', 'json')
        
        with open(output_json, 'r') as f:
            result = json.load(f)
            assert result == TEST_DATA

def test_compare_formats():
    results = FormatConverter.compare_formats(TEST_DATA)
    
    # Verify all formats are present in results
    assert set(results.keys()) == {'json', 'msgpack', 'bson', 'orjson', 'ujson', 'cbd'}
    
    # Verify all sizes are positive integers
    for size in results.values():
        assert isinstance(size, int)
        assert size > 0

def test_invalid_input_format():
    with pytest.raises(ValueError):
        FormatConverter.convert_file('input.txt', 'output.cbd', 'invalid', 'cbd')

def test_invalid_output_format():
    with pytest.raises(ValueError):
        FormatConverter.convert_file('input.json', 'output.txt', 'json', 'invalid')

def test_nonexistent_input_file():
    with pytest.raises(FileNotFoundError):
        FormatConverter.convert_file('nonexistent.json', 'output.cbd', 'json', 'cbd') 