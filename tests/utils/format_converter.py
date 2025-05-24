import json
import msgpack
import bson
import orjson
import ujson
from pathlib import Path
import sys

# Add parent directory to path to import CBD
sys.path.append(str(Path(__file__).parent.parent.parent))
from cbd import CBD

class FormatConverter:
    @staticmethod
    def json_to_cbd(json_data):
        """Convert JSON data to CBD format."""
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        return CBD.serialize(json_data)
    
    @staticmethod
    def cbd_to_json(cbd_data):
        """Convert CBD data to JSON format."""
        data = CBD.deserialize(cbd_data)
        return json.dumps(data)
    
    @staticmethod
    def msgpack_to_cbd(msgpack_data):
        """Convert MessagePack data to CBD format."""
        if isinstance(msgpack_data, bytes):
            data = msgpack.unpackb(msgpack_data)
        else:
            data = msgpack_data
        return CBD.serialize(data)
    
    @staticmethod
    def cbd_to_msgpack(cbd_data):
        """Convert CBD data to MessagePack format."""
        data = CBD.deserialize(cbd_data)
        return msgpack.packb(data)
    
    @staticmethod
    def bson_to_cbd(bson_data):
        """Convert BSON data to CBD format."""
        if isinstance(bson_data, bytes):
            data = bson.loads(bson_data)
        else:
            data = bson_data
        return CBD.serialize(data)
    
    @staticmethod
    def cbd_to_bson(cbd_data):
        """Convert CBD data to BSON format."""
        data = CBD.deserialize(cbd_data)
        return bson.dumps(data)
    
    @staticmethod
    def orjson_to_cbd(orjson_data):
        """Convert orjson data to CBD format."""
        if isinstance(orjson_data, bytes):
            data = orjson.loads(orjson_data)
        else:
            data = orjson_data
        return CBD.serialize(data)
    
    @staticmethod
    def cbd_to_orjson(cbd_data):
        """Convert CBD data to orjson format."""
        data = CBD.deserialize(cbd_data)
        return orjson.dumps(data)
    
    @staticmethod
    def ujson_to_cbd(ujson_data):
        """Convert ujson data to CBD format."""
        if isinstance(ujson_data, str):
            data = ujson.loads(ujson_data)
        else:
            data = ujson_data
        return CBD.serialize(data)
    
    @staticmethod
    def cbd_to_ujson(cbd_data):
        """Convert CBD data to ujson format."""
        data = CBD.deserialize(cbd_data)
        return ujson.dumps(data)
    
    @staticmethod
    def convert_file(input_file, output_file, input_format, output_format):
        """Convert a file from one format to another."""
        # Read input file
        with open(input_file, 'rb' if input_format in ['cbd', 'msgpack', 'bson'] else 'r') as f:
            input_data = f.read()
        
        # Convert data
        if input_format == 'json':
            data = json.loads(input_data)
        elif input_format == 'msgpack':
            data = msgpack.unpackb(input_data)
        elif input_format == 'bson':
            data = bson.loads(input_data)
        elif input_format == 'orjson':
            data = orjson.loads(input_data)
        elif input_format == 'ujson':
            data = ujson.loads(input_data)
        elif input_format == 'cbd':
            data = CBD.deserialize(input_data)
        else:
            raise ValueError(f"Unsupported input format: {input_format}")
        
        # Convert to output format
        if output_format == 'json':
            output_data = json.dumps(data)
            mode = 'w'
        elif output_format == 'msgpack':
            output_data = msgpack.packb(data)
            mode = 'wb'
        elif output_format == 'bson':
            output_data = bson.dumps(data)
            mode = 'wb'
        elif output_format == 'orjson':
            output_data = orjson.dumps(data)
            mode = 'wb'
        elif output_format == 'ujson':
            output_data = ujson.dumps(data)
            mode = 'w'
        elif output_format == 'cbd':
            output_data = CBD.serialize(data)
            mode = 'wb'
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Write output file
        with open(output_file, mode) as f:
            f.write(output_data)
    
    @staticmethod
    def compare_formats(data, formats=None):
        """Compare the size of data in different formats."""
        if formats is None:
            formats = ['json', 'msgpack', 'bson', 'orjson', 'ujson', 'cbd']
        
        results = {}
        for fmt in formats:
            if fmt == 'json':
                serialized = json.dumps(data).encode('utf-8')
            elif fmt == 'msgpack':
                serialized = msgpack.packb(data)
            elif fmt == 'bson':
                serialized = bson.dumps(data)
            elif fmt == 'orjson':
                serialized = orjson.dumps(data)
            elif fmt == 'ujson':
                serialized = ujson.dumps(data).encode('utf-8')
            elif fmt == 'cbd':
                serialized = CBD.serialize(data)
            else:
                raise ValueError(f"Unsupported format: {fmt}")
            
            results[fmt] = len(serialized)
        
        return results

def main():
    """Command-line interface for format conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert between different serialization formats')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--input-format', '-i', required=True,
                      choices=['json', 'msgpack', 'bson', 'orjson', 'ujson', 'cbd'],
                      help='Input file format')
    parser.add_argument('--output-format', '-o', required=True,
                      choices=['json', 'msgpack', 'bson', 'orjson', 'ujson', 'cbd'],
                      help='Output file format')
    
    args = parser.parse_args()
    
    try:
        FormatConverter.convert_file(
            args.input_file,
            args.output_file,
            args.input_format,
            args.output_format
        )
        print(f"Successfully converted {args.input_file} from {args.input_format} to {args.output_format}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 