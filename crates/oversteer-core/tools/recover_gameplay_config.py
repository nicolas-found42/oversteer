"""Read-only bounded extraction of exact native gameplay field names from scripts.jfs.
Output is evidence, never an assertion that a named field's consumer is recovered.
"""
from pathlib import Path
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'artifacts/juiced2-recovery'
OUTPUT = ROOT / 'artifacts/juiced2-build/core-native-gameplay-config.json'
header = (SOURCE / 'scripts.jfshdr').read_bytes()
archive = (SOURCE / 'scripts.jfs').read_bytes()
records = []
formats = set()
errors = []
count = struct.unpack_from('>I', header)[0]
assert count <= 2000
for index in range(count):
    key, offset, packed_size, size, _, _ = struct.unpack_from('>6I', header, 4 + index * 24)
    assert size <= 8_000_000
    try:
        packed = archive[offset:offset + packed_size]
        data = packed if packed_size == size else zlib.decompress(packed)
        assert len(data) == size
        if data[:4] != b'\x02' * 4:
            try:
                source_text=data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            rows=[]
            for line in source_text.splitlines():
                line=line.split(';',1)[0].strip()
                if not line: continue
                values=[]
                for token in line.split():
                    try: value=float(token) if '.' in token else int(token)
                    except ValueError: value=token
                    values.append(value)
                rows.append(values)
            hits=[row for row in rows if any(isinstance(value,str) and any(term in value.lower() for term in ('drift','spook','dna','wager','pinkslip','league','bet','score','goal')) for value in row)]
            if hits:
                records.append(dict(index=index,key=f'{key:08x}',offset=offset,packed_size=packed_size,decoded_size=size,sha256=hashlib.sha256(data).hexdigest(),encoding='text',hits=hits,fields=rows,source_text=source_text))
            continue
        start, cursor = struct.unpack_from('>II', data, 4)
        format_rows = data[start:cursor].split(b'\x03')[0].decode().strip().splitlines()
        formats.update(''.join(format_rows))
        rows = []
        for format_row in format_rows:
            values = []
            for field in format_row:
                if field not in 'sif':
                    raise ValueError(f'unknown format {field!r}')
                value = struct.unpack_from('>f' if field == 'f' else '>i', data, cursor)[0]
                cursor += 4
                if field == 's':
                    value = data[value:data.index(0, value)].decode()
                values.append(value)
            rows.append(values)
        assert cursor == len(data)
        # Exact literal field families named in the accepted recovery task.
        hits = [row for row in rows if row and isinstance(row[0], str)
                and any(isinstance(value,str) and any(term in value.lower() for term in ('drift', 'spook', 'dna', 'wager', 'pinkslip', 'league', 'bet','score','goal')) for value in row)]
        if hits:
            records.append(dict(index=index, key=f'{key:08x}', offset=offset,
                                packed_size=packed_size, decoded_size=size,
                                sha256=hashlib.sha256(data).hexdigest(), hits=hits, fields=rows))
    except Exception as error:
        errors.append(dict(index=index, key=f'{key:08x}', error=str(error)))
OUTPUT.write_text(json.dumps(dict(source='scripts.jfs', record_count=count,
                                 matched_records=records, formats=sorted(formats), errors=errors), indent=2))
print(json.dumps(dict(scanned=count, matched=len(records), errors=len(errors), output=str(OUTPUT))))
for record in records:
    if record.get('encoding')=='text': print(record['index'], record['key'], json.dumps(record['hits'])[:900])
