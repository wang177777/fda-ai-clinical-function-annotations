#!/usr/bin/env python3
"""Rebuild the two cohort tables from three fingerprinted historical originals.

All originals and all CSV metadata are verified in a temporary staging directory
before either output is written. No existing cohort table is used as an input.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path

from check_cohort_snapshot import (
    ROOT, SNAPSHOT_ID, SNAPSHOT_DATE, DISTRIBUTION_STATUS, MEMBERSHIP_COLUMNS, MANIFEST_COLUMNS,
    RAW_COLUMNS, MATCH_COMPANY, MATCH_DATE, check_snapshot, read_table,
    require, unique_index,
)

# Fingerprints and URLs transcribed from the retained June 29 originals/log.
ORIGINALS = (
    ('COHORT_20260629_CSV', 'fda_ai_enabled_devices_2026-06-29.csv',
     '4da0d15a1dcc7b6a7d45364f243e85aa4407ba3b63b6922a16fdbf96fea0d41d',
     132922, 'https://www.fda.gov/media/178541/download?attachment', 'CSV'),
    ('COHORT_20260629_XLSX', 'fda_ai_enabled_devices_2026-06-29.xlsx',
     'ced5c4a50d402eacc667fbfe99d62a2352cb5e68fdb58c5d8e0b18cc71acfc1b',
     122741, 'https://www.fda.gov/media/178540/download?attachment', 'XLSX'),
    ('COHORT_20260629_METADATA', 'source_metadata_2026-06-29.txt',
     'ce075cf084ae6c22dd52e4828bc79c5b8201fbb70278eb62b606e17b55b4d56c',
     1026, 'https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices', 'TXT'),
)


def csv_bytes(rows, columns):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\r\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def prepare_tables(repository, snapshot_csv, snapshot_xlsx, metadata_txt):
    """Return validated output bytes and a path-free report, without writing outputs."""
    originals, manifest = [], []
    for path, (artifact_id, name, digest, size, url, file_format) in zip(
            (snapshot_csv, snapshot_xlsx, metadata_txt), ORIGINALS):
        content = Path(path).read_bytes()
        require(hashlib.sha256(content).hexdigest() == digest, f'{artifact_id}: original SHA-256 mismatch')
        require(len(content) == size, f'{artifact_id}: original byte length mismatch')
        originals.append(content)
        manifest.append(dict(zip(MANIFEST_COLUMNS, (
            artifact_id, SNAPSHOT_ID, name, digest, size, SNAPSHOT_DATE, url,
            file_format, DISTRIBUTION_STATUS))))

    # Stage from verified bytes, avoiding an input change between hashing and use.
    with tempfile.TemporaryDirectory(prefix='cohort_mapping_build_') as temporary:
        staging = Path(temporary)
        (staging / 'data').mkdir()
        authorization_bytes = (Path(repository) / 'data' / 'authorizations.csv').read_bytes()
        (staging / 'data' / 'authorizations.csv').write_bytes(authorization_bytes)
        original_csv = staging / ORIGINALS[0][1]
        original_csv.write_bytes(originals[0])
        authors = unique_index(read_table(staging / 'data' / 'authorizations.csv'), 'submission_number', 'authorizations')
        raw_rows = read_table(original_csv, RAW_COLUMNS)
        members = []
        for position, raw in enumerate(raw_rows, start=1):
            key = raw['Submission Number']
            require(key in authors, f'{key}: snapshot key is absent from authorizations')
            members.append(dict(zip(MEMBERSHIP_COLUMNS, (
                key, SNAPSHOT_ID, position, raw['Primary Product Code'],
                MATCH_COMPANY if raw['Company'] != authors[key]['company'] else MATCH_DATE))))
        payloads = {
            'cohort_snapshot_membership.csv': csv_bytes(members, MEMBERSHIP_COLUMNS),
            'cohort_snapshot_manifest.csv': csv_bytes(manifest, MANIFEST_COLUMNS),
        }
        for name, content in payloads.items():
            (staging / 'data' / name).write_bytes(content)
        validation = check_snapshot(staging, original_csv)
    return payloads, {
        'status': 'PASS', 'snapshot_id': SNAPSHOT_ID,
        'original_artifacts_verified': [row[0] for row in ORIGINALS],
        'original_sha256': {row[0]: row[2] for row in ORIGINALS},
        'membership_rows': len(members), 'manifest_rows': len(manifest),
        'matched_original_metadata_cells': validation['matched_original_metadata_cells'],
        'company_whitespace_normalization_subjects': validation['company_whitespace_normalization_subjects'],
        'validation_completed_before_output_write': True,
        'existing_cohort_tables_used_as_inputs': False,
        'network_download_performed': False,
        'output_sha256': {name: hashlib.sha256(content).hexdigest() for name, content in payloads.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=ROOT, help='Root containing the current data/authorizations.csv')
    parser.add_argument('--snapshot-csv', type=Path, required=True)
    parser.add_argument('--snapshot-xlsx', type=Path, required=True)
    parser.add_argument('--metadata-txt', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, help='Destination directory for the two generated CSVs; default: repository/data')
    args = parser.parse_args()
    repository = args.repository.expanduser().resolve()
    inputs = [path.expanduser().resolve() for path in (args.snapshot_csv, args.snapshot_xlsx, args.metadata_txt)]
    output_dir = args.output_dir.expanduser().resolve() if args.output_dir else repository / 'data'
    try:
        protected = {*inputs, repository / 'data' / 'authorizations.csv'}
        for name in ('cohort_snapshot_membership.csv', 'cohort_snapshot_manifest.csv'):
            require((output_dir / name).resolve() not in protected, 'Output would overwrite a source input')
        payloads, report = prepare_tables(repository, *inputs)
        # No destination directory or output file is created before validation.
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in payloads.items():
            destination = output_dir / name
            if destination.exists() and destination.read_bytes() == content:
                continue
            temporary_path = None
            try:
                with tempfile.NamedTemporaryFile(dir=output_dir, prefix='.' + name + '.', delete=False) as stream:
                    temporary_path = Path(stream.name)
                    stream.write(content)
                os.replace(temporary_path, destination)
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, 'Cohort mapping build failed: ' + (str(error) if not isinstance(error, OSError) else 'could not read or write a required file') + '\n')
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
