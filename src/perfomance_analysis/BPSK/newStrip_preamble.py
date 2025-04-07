#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Strip preamble (%UU]) and trailer (#EOF) from raw byte data.
"""

import sys
import os.path

_debug = 1  # Set to 0 to disable prints

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 strip_preamble.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        sys.exit(1)

    preamble = bytes([37, 85, 85, 93])  # % U U ]
    trailer = bytes([35, 69, 79, 70])   # # E O F

    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        data = f_in.read()
        
        start_idx = data.find(preamble)
        if start_idx == -1:
            print("Error: Preamble (%UU]) not found!")
            sys.exit(1)
        
        payload_start = start_idx + len(preamble)
        end_idx = data.find(trailer, payload_start)
        if end_idx == -1:
            print("Error: Trailer (#EOF) not found!")
            sys.exit(1)

        payload = data[payload_start:end_idx]
        
        if _debug:
            print(f"Preamble position: {start_idx}")
            print(f"Trailer position: {end_idx}")
            print(f"Payload (hex): {payload.hex()}")

        f_out.write(payload)

if __name__ == "__main__":
    main()
