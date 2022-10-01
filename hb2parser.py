import argparse
from struct import unpack
from os.path import join

BLOCK_SIZE = 96 #bytes
N_BLOCKS = 10
parser = argparse.ArgumentParser(description=
"""Extract .HB2 firmware format.
It should be able to detect the correct offset. Otherwise put it manually.
Use an hex-editor and look for the first occurence of such a pattern:
  (4 bytes position)(4 bytes size)(filename)
 ^---- Offset""",formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("path", type=str)
parser.add_argument("--offset",type=lambda x: int(x,0))
parser.add_argument("--extract", metavar="extract_path", type=str)
parser.add_argument("--list",action='store_true')
args = parser.parse_args()
path = args.path
offset = args.offset
extract_path = args.extract
listing = args.list


positions = []
sizes = []
filenames = []
## Detecting  offset
consecutive_null = 0
with open(path,'rb') as binary_stream:
    while True:
        byte =  binary_stream.read(1)
        if byte == b'\x00':
            consecutive_null += 1
        else:
            if consecutive_null >= 272:
                break
            consecutive_null = 0
        
        detected_offset = binary_stream.tell()
    
if offset is None:
    offset = detected_offset
else:
    if offset != detected_offset:
        print(f"Warning: input_offset({offset}) != detected_offset({detected_offset}")

with open(path,'rb') as binary_stream:
    binary_stream.seek(offset)
    current_position = offset
    while True:
        block = binary_stream.read(BLOCK_SIZE)
        current_position += BLOCK_SIZE
        position = unpack("I",block[:4])[0]
        size = unpack("I", block[4:8])[0]
        filename = block[8:].split(b'\x00')[0].decode('utf-8')
        positions.append(position)
        sizes.append(size)
        filenames.append(filename)
        if current_position+BLOCK_SIZE > positions[0]:
            break
        if listing:
            print(f"{position:>10} {size:>10} {filename:>10}")
    
    if extract_path is not None:
        for p,s,fn in zip(positions,sizes,filenames):
            binary_stream.seek(p)
            with open(join(extract_path, fn), 'wb') as output_stream:
                output_stream.write(binary_stream.read(s))
