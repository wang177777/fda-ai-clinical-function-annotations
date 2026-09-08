#!/usr/bin/env python3
"""Export current positive input/output selections with both evidence layers.

One CSV row represents an authorization. Input and output label sets co-occur at
that level; the export does not encode component-level input-output pairs.
See docs/reuse_examples.md for filter definitions and worked examples.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESCRIBED_SCOPE = 'DESCRIBED_AI_OR_ALGORITHMIC_FUNCTION'
STRICT_RELATIONSHIPS = frozenset({
    'GENERAL_SOFTWARE_CONTINUITY_FEATURE_NOT_RESTATED',
    'GENERAL_FIRMWARE_CONTINUITY_FEATURE_NOT_RESTATED',
    'GENERAL_PERFORMANCE_CONTINUITY_FEATURE_NOT_RESTATED',
    'EXPLICIT_INTEGRATION_OUTSIDE_CURRENT_SUBMISSION_SCOPE',
})
STRICT_CAUTION_CODES = frozenset({
    'FEATURE_NOT_NAMED_IN_CURRENT_SUMMARY',
    'AI_FEATURE_EXPLICITLY_OUTSIDE_CURRENT_SUBMISSION_SCOPE',
})
TABLE_NAMES = (
    'authorizations', 'field_annotations', 'positive_labels', 'vocabulary',
    'evidence_links', 'source_records', 'associated_source_relationships',
    'source_bridges', 'semantic_review_records', 'semantic_review_sources',
)
COLUMNS = (
    'submission_number', 'device_name', 'ai_function_scope',
    'clinical_function_group', 'selection_input_code', 'selection_output_code',
    'input_annotation_id', 'input_codes', 'input_annotation_state',
    'output_annotation_id', 'output_codes', 'output_annotation_state',
    'input_evidence_json', 'output_evidence_json',
    'recorded_scope_flags_json', 'strict_current_scope_applied',
)
INTERPRETATION = (
    'Selection uses current positive labels. Input and output coexist at the '
    'authorization level, without encoded component-level pairs. Original '
    'machine locators and subsequent page-based semantic review are separate '
    'layers; a located string is not code-level validation. The strict filter '
    'applies specified recorded restrictions to input and output only. Passing '
    'it, or having no focused relationship record, does not establish semantic '
    'accuracy, exhaustive coding, or independently verified current attribution.'
)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def unique_index(rows, key, name):
    result = {}
    for row in rows:
        if row[key] in result:
            raise ValueError(f'{name}: duplicate {key} {row[key]!r}')
        result[row[key]] = row
    return result


def split_ids(value):
    return [part for part in value.split(';') if part]


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def scope_flags(authorization, fields, relations):
    flags = []
    if authorization['ai_function_scope'] != DESCRIBED_SCOPE:
        flags.append({'annotation_id': '', 'reason': 'ai_function_scope=' + authorization['ai_function_scope']})
    for field in fields:
        annotation_id = field['annotation_id']
        if field['annotation_state'] != 'CODED':
            flags.append({'annotation_id': annotation_id, 'reason': 'annotation_state=' + field['annotation_state']})
        relation = relations.get(annotation_id)
        if relation is None:
            continue
        if relation['source_relationship'] in STRICT_RELATIONSHIPS:
            flags.append({'annotation_id': annotation_id, 'reason': 'source_relationship=' + relation['source_relationship']})
        for code in sorted(set(split_ids(relation['source_caution_codes'])) & STRICT_CAUTION_CODES):
            flags.append({'annotation_id': annotation_id, 'reason': 'source_caution_code=' + code})
    return flags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=ROOT, help='Root containing data/ (default: this script\'s repository)')
    parser.add_argument('--input-code', default='MEDICAL_IMAGE', type=str.upper,
                        help='One positive input code, or ANY for any positive coded input (default: MEDICAL_IMAGE)')
    parser.add_argument('--output-code', type=str.upper, help='Optional positive output code; omitted means retain the current output field')
    parser.add_argument('--strict-current-scope', action='store_true', help='Exclude recorded scope/state restrictions and specified input/output source cautions')
    parser.add_argument('--output', type=Path, required=True, help='CSV outside the source repository; also writes .summary.json and .excluded.csv')
    args = parser.parse_args()
    repository, destination = args.repository.expanduser().resolve(), args.output.expanduser().resolve()
    if destination.suffix.lower() != '.csv':
        parser.error('--output must end in .csv')
    if destination.is_relative_to(repository):
        parser.error('--output must be outside the source repository to preserve the release')

    paths = {name: repository / 'data' / (name + '.csv') for name in TABLE_NAMES}
    tables = {name: read_csv(path) for name, path in paths.items()}
    vocabulary = {(row['field'], row['code']) for row in tables['vocabulary'] if row['class'] == 'POSITIVE_CONTENT_LABEL'}
    if args.input_code != 'ANY' and ('input', args.input_code) not in vocabulary:
        parser.error('--input-code must be a positive input vocabulary code or ANY')
    if args.output_code and ('output', args.output_code) not in vocabulary:
        parser.error('--output-code must be a positive output vocabulary code')

    authorizations = unique_index(tables['authorizations'], 'submission_number', 'authorizations')
    fields = unique_index(tables['field_annotations'], 'annotation_id', 'field_annotations')
    evidence = unique_index(tables['evidence_links'], 'annotation_id', 'evidence_links')
    sources = unique_index(tables['source_records'], 'source_record_id', 'source_records')
    relations = unique_index(tables['associated_source_relationships'], 'annotation_id', 'associated_source_relationships')
    review_sources = unique_index(tables['semantic_review_sources'], 'review_source_id', 'semantic_review_sources')
    unique_index(tables['semantic_review_records'], 'review_record_id', 'semantic_review_records')
    unique_index(tables['source_bridges'], 'bridge_id', 'source_bridges')
    bridges, reviews = defaultdict(list), defaultdict(list)
    for bridge in tables['source_bridges']:
        bridges[bridge['annotation_id']].append(bridge)
    for review in tables['semantic_review_records']:
        reviews[review['annotation_id']].append(review)

    memberships = set()
    for label in tables['positive_labels']:
        field = fields[label['annotation_id']]
        key = (label['annotation_id'], label['label'])
        if key in memberships:
            raise ValueError(f'Duplicate positive-label membership: {key}')
        if field['annotation_state'] != 'CODED' or label['label'] not in split_ids(field['codes']):
            raise ValueError(f'Positive-label membership disagrees with current field: {key}')
        if label['submission_number'] != field['submission_number'] or label['field'] != field['field']:
            raise ValueError(f'Positive-label membership has inconsistent identity: {key}')
        memberships.add(key)
    # Check both directions: an omitted new label must not silently disappear.
    for field in fields.values():
        if field['field'] in ('input', 'output') and field['annotation_state'] == 'CODED':
            for code in split_ids(field['codes']):
                if (field['field'], code) not in vocabulary or (field['annotation_id'], code) not in memberships:
                    raise ValueError(f'Current input/output code missing from positive membership: {field["annotation_id"]} {code}')

    def source_details(annotation_id):
        original = evidence[annotation_id]
        field_bridges = sorted(bridges[annotation_id], key=lambda row: row['bridge_id'])
        original_ids = set(split_ids(original['source_record_ids']))
        original_ids.update(source_id for row in field_bridges for source_id in split_ids(row['source_record_ids']))
        field_reviews = []
        for review in sorted(reviews[annotation_id], key=lambda row: row['review_record_id']):
            linked = []
            for source_id in split_ids(review['review_source_ids']):
                source = review_sources[source_id]
                linked.append({**source, 'existing_source_records': [sources[key] for key in split_ids(source['existing_source_record_ids'])]})
            field_reviews.append({**review, 'review_sources': linked})
        relation = relations.get(annotation_id)
        return {
            'original_evidence': original,
            'original_and_bridge_source_records': [sources[key] for key in sorted(original_ids)],
            'source_bridges': field_bridges,
            'focused_relationship_record_status': 'AVAILABLE' if relation else 'NO_FOCUSED_RECORD',
            'focused_source_relationship': relation,
            'semantic_reviews': field_reviews,
        }

    matched, exported, excluded, flagged = [], [], [], {}
    for submission, authorization in sorted(authorizations.items()):
        input_field, output_field = fields[submission + ':input'], fields[submission + ':output']
        if input_field['annotation_state'] != 'CODED':
            continue
        if args.input_code != 'ANY' and (input_field['annotation_id'], args.input_code) not in memberships:
            continue
        if args.output_code and (output_field['annotation_id'], args.output_code) not in memberships:
            continue
        matched.append(submission)
        flags = scope_flags(authorization, (input_field, output_field), relations)
        if flags:
            flagged[submission] = flags
        if args.strict_current_scope and flags:
            excluded.append({'submission_number': submission, 'exclusion_reasons_json': encode(flags)})
            continue
        row = {key: authorization[key] for key in COLUMNS[:4]}
        row.update(selection_input_code=args.input_code, selection_output_code=args.output_code or '')
        for prefix, field in (('input', input_field), ('output', output_field)):
            for key in ('annotation_id', 'codes', 'annotation_state'):
                row[prefix + '_' + key] = field[key]
            row[prefix + '_evidence_json'] = encode(source_details(field['annotation_id']))
        row.update(recorded_scope_flags_json=encode(flags), strict_current_scope_applied=str(args.strict_current_scope).lower())
        exported.append(row)

    if len({row['submission_number'] for row in exported}) != len(exported):
        raise ValueError('Join multiplication: more than one exported row per authorization')
    review_ids, source_ids = set(), set()
    for row in exported:
        for prefix in ('input', 'output'):
            for review in json.loads(row[prefix + '_evidence_json'])['semantic_reviews']:
                review_ids.add(review['review_record_id'])
                source_ids.update(source['review_source_id'] for source in review['review_sources'])
    summary = {
        'row_unit': 'one authorization with current input/output sets and separate evidence layers',
        'input_code': args.input_code, 'output_code': args.output_code,
        'strict_current_scope': args.strict_current_scope,
        'repository_authorizations': len(authorizations),
        'matched_authorizations_before_scope_filter': len(matched),
        'authorizations_with_recorded_filter_flags': len(flagged),
        'flagged_authorizations': flagged,
        'flagged_input_output_annotation_ids': sorted({flag['annotation_id'] for flags in flagged.values() for flag in flags if flag['annotation_id']}),
        'exported_authorizations': len(exported),
        'exported_output_positive_code_memberships': sum(len(split_ids(row['output_codes'])) for row in exported if row['output_annotation_state'] == 'CODED'),
        'exported_output_annotation_states': dict(sorted(Counter(row['output_annotation_state'] for row in exported).items())),
        'exported_semantic_review_records': len(review_ids),
        'exported_semantic_review_source_references': len(source_ids),
        'excluded_authorizations': len(excluded),
        'excluded_submission_numbers': [row['submission_number'] for row in excluded],
        'strict_filter_fields': ['input', 'output'],
        'strict_filter_required_scope': DESCRIBED_SCOPE,
        'strict_filter_required_field_state': 'CODED',
        'strict_filter_relationship_values': sorted(STRICT_RELATIONSHIPS),
        'strict_filter_caution_values': sorted(STRICT_CAUTION_CODES),
        'source_table_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths.values()},
        'interpretation_note': INTERPRETATION,
    }
    write_csv(destination, COLUMNS, exported)
    write_csv(destination.with_name(destination.stem + '.excluded.csv'), ('submission_number', 'exclusion_reasons_json'), excluded)
    destination.with_suffix('.summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
