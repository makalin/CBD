import json
import random
import string
import numpy as np
from datetime import datetime, timedelta

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_nested_dict(depth=3, max_items=5):
    if depth == 0:
        return random.choice([
            random.randint(-1000, 1000),
            random.random(),
            generate_random_string(),
            random.choice([True, False]),
            None
        ])
    
    result = {}
    num_items = random.randint(1, max_items)
    for _ in range(num_items):
        key = generate_random_string(8)
        if random.random() < 0.3:  # 30% chance to create nested structure
            result[key] = generate_nested_dict(depth - 1, max_items)
        else:
            result[key] = generate_nested_dict(0, max_items)
    return result

def generate_array(size=1000):
    return [generate_nested_dict(depth=2, max_items=3) for _ in range(size)]

def generate_test_datasets():
    datasets = {
        'small_dict': generate_nested_dict(depth=2, max_items=5),
        'medium_dict': generate_nested_dict(depth=3, max_items=10),
        'large_dict': generate_nested_dict(depth=4, max_items=20),
        'small_array': generate_array(100),
        'medium_array': generate_array(1000),
        'large_array': generate_array(10000),
        'mixed_data': {
            'strings': [generate_random_string(20) for _ in range(100)],
            'numbers': [random.random() for _ in range(100)],
            'integers': [random.randint(-1000, 1000) for _ in range(100)],
            'booleans': [random.choice([True, False]) for _ in range(100)],
            'nulls': [None] * 10,
            'nested': generate_nested_dict(depth=3, max_items=5)
        }
    }
    
    # Save datasets to JSON files
    for name, data in datasets.items():
        with open(f'tests/data/{name}.json', 'w') as f:
            json.dump(data, f)

if __name__ == '__main__':
    generate_test_datasets() 