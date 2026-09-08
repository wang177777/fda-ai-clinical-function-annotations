#!/usr/bin/env python3
"""Check the public cohort map, optionally against the retained historical CSV.

No network requests are made. Without --snapshot-csv, this checks public mapping
structure and fingerprint syntax only. Use --output to save the JSON report;
the default is stdout, so routine checks preserve earlier validation records.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ID = 'FDA_AI_LIST_2026-06-29'
SNAPSHOT_DATE = '2026-06-29'
DISTRIBUTION_STATUS = 'DISTRIBUTED_IN_RELEASE_SOURCE_ARCHIVES'
COHORT_SIZE = 1524
MATCH_DATE = 'MATCH_AFTER_DATE_NORMALIZATION'
MATCH_COMPANY = 'MATCH_AFTER_DATE_AND_COMPANY_TRIM'
MEMBERSHIP_COLUMNS = ['submission_number', 'snapshot_id', 'snapshot_row_number', 'primary_product_code', 'metadata_match_status']
MANIFEST_COLUMNS = ['snapshot_artifact_id', 'snapshot_id', 'artifact_name', 'artifact_sha256', 'artifact_bytes', 'recorded_access_date', 'recorded_source_url', 'artifact_format', 'distribution_status']
RAW_COLUMNS = ['Date of Final Decision', 'Submission Number', 'Device', 'Company', 'Panel (Lead)', 'Primary Product Code']
ARTIFACTS = {'COHORT_20260629_CSV': 'CSV', 'COHORT_20260629_XLSX': 'XLSX', 'COHORT_20260629_METADATA': 'TXT'}
COMPANY_TRIM_SUBJECTS = {'DEN220024', 'DEN230027'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_table(path, columns=None):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if columns is not None:
            require(reader.fieldnames == columns, f'{path.name}: unexpected column names or order')
        rows = list(reader)
    require(all(None not in row and all(value is not None for value in row.values()) for row in rows), f'{path.name}: malformed CSV row')
    return rows


def unique_index(rows, key, name):
    result = {}
    for row in rows:
        require(row[key] not in result, f'{name}: duplicate {key} {row[key]!r}')
        result[row[key]] = row
    return result


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_snapshot(repository=ROOT, snapshot_csv=None):
    """Return a path-free report; raise ValueError on a failed consistency check."""
    repository = Path(repository)
    data = repository / 'data'
    member_path = data / 'cohort_snapshot_membership.csv'
    manifest_path = data / 'cohort_snapshot_manifest.csv'
    authorization_path = data / 'authorizations.csv'
    members = read_table(member_path, MEMBERSHIP_COLUMNS)
    manifest = read_table(manifest_path, MANIFEST_COLUMNS)
    authorizations = unique_index(read_table(authorization_path), 'submission_number', 'authorizations')
    mapping = unique_index(members, 'submission_number', 'cohort_snapshot_membership')
    artifacts = unique_index(manifest, 'snapshot_artifact_id', 'cohort_snapshot_manifest')
    require(len(members) == len(authorizations) == COHORT_SIZE, 'Unexpected cohort size')
    require(set(mapping) == set(authorizations), 'Snapshot membership keys differ from current authorization keys')
    require(set(artifacts) == set(ARTIFACTS), 'Expected one CSV, one XLSX and one metadata artifact')
    row_numbers = []
    for row in members:
        require(row['snapshot_id'] == SNAPSHOT_ID, 'Unknown membership snapshot_id')
        require(re.fullmatch(r'[1-9][0-9]*', row['snapshot_row_number']) is not None, 'Invalid snapshot row number')
        row_numbers.append(int(row['snapshot_row_number']))
        require(re.fullmatch(r'[A-Z]{3}', row['primary_product_code']) is not None, 'Invalid primary product code')
        require(row['metadata_match_status'] in {MATCH_DATE, MATCH_COMPANY}, 'Unknown metadata match status')
    require(sorted(row_numbers) == list(range(1, COHORT_SIZE + 1)), 'Snapshot row numbers must cover 1 through 1524 exactly once')
    require({row['submission_number'] for row in members if row['metadata_match_status'] == MATCH_COMPANY} == COMPANY_TRIM_SUBJECTS,
            'Unexpected reported company-whitespace normalization set')
    for row in manifest:
        require(row['snapshot_id'] == SNAPSHOT_ID, 'Unknown manifest snapshot_id')
        require(row['artifact_name'] == Path(row['artifact_name']).name and '/' not in row['artifact_name'] and '\\' not in row['artifact_name'], 'Artifact name must be a basename without a private path')
        require(re.fullmatch(r'[0-9a-f]{64}', row['artifact_sha256']) is not None, 'Invalid artifact SHA-256 syntax')
        require(re.fullmatch(r'[1-9][0-9]*', row['artifact_bytes']) is not None, 'Invalid artifact byte length')
        require(date.fromisoformat(row['recorded_access_date']).isoformat() == SNAPSHOT_DATE, 'Unexpected recorded access date')
        parsed = urlsplit(row['recorded_source_url'])
        require(parsed.scheme == 'https' and parsed.netloc in {'www.fda.gov', 'fda.gov'}, 'Expected an FDA HTTPS source URL')
        require(row['artifact_format'] == ARTIFACTS[row['snapshot_artifact_id']], 'Artifact identifier/format mismatch')
        require(row['distribution_status'] == DISTRIBUTION_STATUS, 'Unexpected raw-artifact distribution status')
    report = {
        'status': 'PASS',
        'snapshot_id': SNAPSHOT_ID,
        'recorded_access_date': SNAPSHOT_DATE,
        'check_mode': 'PUBLIC_MAPPING_AND_FINGERPRINT_SYNTAX',
        'public_membership_rows': len(members),
        'matching_current_authorization_keys': len(mapping),
        'original_row_numbers_complete_and_unique': True,
        'artifact_manifest_rows': len(manifest),
        'artifact_fingerprint_syntax_checks': len(manifest),
        'reported_metadata_match_status_counts': dict(sorted(Counter(row['metadata_match_status'] for row in members).items())),
        'raw_artifact_bytes_checked_in_this_run': [],
        'original_csv_metadata_comparison': 'NOT_RUN_WITHOUT_RETAINED_CSV',
        'public_input_sha256': {path.name: sha256(path) for path in (member_path, manifest_path, authorization_path)},
        'network_download_performed': False,
        'interpretation': 'Public mapping checks test keys, row numbering and manifest syntax. Original-byte and six-column comparisons require the retained CSV. Recorded access dates are historical provenance, not a newly authenticated retrieval time.',
    }
    if snapshot_csv is None:
        return report

    snapshot_csv = Path(snapshot_csv)
    csv_artifact = artifacts['COHORT_20260629_CSV']
    observed_hash = sha256(snapshot_csv)
    require(observed_hash == csv_artifact['artifact_sha256'], 'Supplied CSV SHA-256 differs from the retained snapshot fingerprint')
    require(snapshot_csv.stat().st_size == int(csv_artifact['artifact_bytes']), 'Supplied CSV byte length differs from the retained manifest')
    raw_rows = read_table(snapshot_csv, RAW_COLUMNS)
    raw_keys = unique_index(raw_rows, 'Submission Number', 'historical CSV')
    require(len(raw_rows) == COHORT_SIZE and set(raw_keys) == set(authorizations), 'Historical CSV membership differs from the current cohort')
    matched_columns = Counter()
    company_trimmed = []
    for row_number, raw in enumerate(raw_rows, start=1):
        key = raw['Submission Number']
        current, member = authorizations[key], mapping[key]
        require(int(member['snapshot_row_number']) == row_number, f'{key}: original record position differs from membership map')
        decision_date = datetime.strptime(raw['Date of Final Decision'], '%m/%d/%Y').date().isoformat()
        comparisons = {
            'Date of Final Decision': (decision_date, current['date_of_final_decision']),
            'Submission Number': (raw['Submission Number'], current['submission_number']),
            'Device': (raw['Device'], current['device_name']),
            'Company': (raw['Company'].strip(), current['company']),
            'Panel (Lead)': (raw['Panel (Lead)'], current['medical_specialty']),
            'Primary Product Code': (raw['Primary Product Code'], member['primary_product_code']),
        }
        for column, (original, retained) in comparisons.items():
            require(original == retained, f'{key}: {column} does not match the public record under the stated normalization')
            matched_columns[column] += 1
        company_changed = raw['Company'] != current['company']
        if company_changed:
            company_trimmed.append(key)
        expected_status = MATCH_COMPANY if company_changed else MATCH_DATE
        require(member['metadata_match_status'] == expected_status, f'{key}: metadata match status disagrees with the original CSV')
    require(set(company_trimmed) == COMPANY_TRIM_SUBJECTS, 'Company whitespace differences do not match the retained two-record finding')
    report.update({
        'check_mode': 'PUBLIC_MAPPING_PLUS_RETAINED_CSV_BYTES_AND_SIX_COLUMNS',
        'raw_artifact_bytes_checked_in_this_run': ['COHORT_20260629_CSV'],
        'observed_original_csv_sha256': observed_hash,
        'observed_original_csv_bytes': snapshot_csv.stat().st_size,
        'original_csv_rows': len(raw_rows),
        'original_csv_metadata_comparison': 'PASS',
        'matched_values_by_original_column': dict(matched_columns),
        'matched_original_metadata_cells': sum(matched_columns.values()),
        'company_whitespace_normalization_subjects': sorted(company_trimmed),
        'normalizations': {'Date of Final Decision': 'MM/DD/YYYY converted to ISO YYYY-MM-DD', 'Company': 'Python str.strip(): leading/trailing whitespace only', 'all_other_columns': 'Exact string comparison'},
        'unexamined_original_artifacts_in_this_run': ['COHORT_20260629_XLSX', 'COHORT_20260629_METADATA'],
    })
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=ROOT, help='Repository root containing data/')
    parser.add_argument('--snapshot-csv', type=Path, help='Retained historical CSV matching the published fingerprint; no download occurs')
    parser.add_argument('--output', type=Path, help='Optional destination for a path-free JSON report; default: stdout only')
    args = parser.parse_args()
    if args.output:
        destination = args.output.expanduser().resolve()
        protected = args.repository.expanduser().resolve() / 'data'
        if destination.suffix.lower() != '.json':
            parser.error('--output must end in .json')
        if destination.is_relative_to(protected):
            parser.error('--output must not overwrite a data table')
        if args.snapshot_csv and destination == args.snapshot_csv.expanduser().resolve():
            parser.error('--output must not overwrite the historical CSV')
    try:
        report = check_snapshot(args.repository.expanduser().resolve(), args.snapshot_csv.expanduser().resolve() if args.snapshot_csv else None)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, 'Cohort snapshot check failed: ' + (str(error) if not isinstance(error, OSError) else 'could not read a required file') + '\n')
    output = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    if args.output:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding='utf-8')
    print(output, end='')


if __name__ == '__main__':
    main()
