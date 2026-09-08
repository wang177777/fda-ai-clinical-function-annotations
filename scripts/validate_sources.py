#!/usr/bin/env python3
"""Check downloaded source file bytes against the versioned public manifests."""
import argparse
import csv
import json
from pathlib import Path
from download_sources import file_sha

ROOT = Path(__file__).resolve().parents[1]

def check(group='all', destination=ROOT):
    source = ROOT / 'source_materials'
    manifests = []
    if group in {'all', 'inputs'}:
        manifests.append(json.loads((source / 'input_manifest.json').read_text()))
    if group in {'all', 'documents'}:
        manifests.append(json.loads((source / 'original_document_manifest.json').read_text()))
    files = [r for m in manifests for r in m['files']]
    missing, mismatched = [], []
    for row in files:
        rel = Path(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        p = destination / rel
        if not p.is_file():
            missing.append(row['path'])
        elif p.stat().st_size != row['bytes'] or file_sha(p) != row['sha256']:
            mismatched.append(row['path'])
    result = {'status': 'PASS' if not missing and not mismatched else 'FAIL', 'group':group,
              'files_checked':len(files), 'missing_files':missing, 'mismatched_files':mismatched}
    if group in {'all', 'documents'}:
        documents = json.loads((source / 'original_document_manifest.json').read_text())
        published = {r['sha256'] for r in documents['files']}
        with (ROOT / 'data/source_records.csv').open(newline='') as stream:
            records = list(csv.DictReader(stream))
        expected = {r['document_sha256'] for r in records if r['document_sha256']}
        assert expected == published and len(published) == 3109
        result['recorded_document_hashes_accounted_for'] = len(expected)
        result['recorded_failed_or_unavailable_rows'] = documents['original_failed_or_unavailable_record_count']
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--group', choices=['all', 'inputs', 'documents'], default='all')
    p.add_argument('--destination', type=Path, default=ROOT)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = check(args.group, args.destination)
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text)
    print(text)
    if result['status'] != 'PASS': raise SystemExit(1)

if __name__ == '__main__': main()
