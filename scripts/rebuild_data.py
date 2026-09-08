#!/usr/bin/env python3
"""Reconstruct all 15 data tables in an isolated destination and compare them."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from download_sources import file_sha

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-materials', type=Path, default=ROOT / 'source_materials')
    p.add_argument('--output', type=Path, help='Write the comparison report here')
    args = p.parse_args()
    source = args.source_materials.resolve(); inputs = source / 'input'
    if not (inputs / 'public_review_input.json').is_file():
        raise SystemExit('First run: python3 scripts/download_sources.py --group inputs')
    with tempfile.TemporaryDirectory(prefix='clinical-function-rebuild-') as temporary:
        target = Path(temporary)
        for name in ['scripts', 'data', 'docs', 'validation']:
            shutil.copytree(ROOT / name, target / name, ignore=shutil.ignore_patterns('__pycache__'))
        for path in (target / 'data').glob('*.csv'): path.unlink()
        commands = [
            ['build_resource.py', '--source-package', str(source)],
            ['append_source_bridges.py', '--review-file', str(inputs / 'cross_authorization_review.csv')],
            ['apply_confirmed_amendments.py', '--public-review-input', str(inputs / 'public_review_input.json')],
            ['build_other_notes.py', '--audit-file', str(inputs / 'other_notes/other_explanations.json'), '--retained-fields', str(inputs / 'annotations/field_taxonomy_9144.csv'), '--translations-file', str(inputs / 'other_notes/translations.json')],
            ['build_cohort_mapping.py', '--snapshot-csv', str(inputs / 'cohort/fda_ai_enabled_devices_2026-06-29.csv'), '--snapshot-xlsx', str(inputs / 'cohort/fda_ai_enabled_devices_2026-06-29.xlsx'), '--metadata-txt', str(inputs / 'cohort/source_metadata_2026-06-29.txt')],
            ['check_cohort_snapshot.py', '--snapshot-csv', str(inputs / 'cohort/fda_ai_enabled_devices_2026-06-29.csv'), '--output', str(target / 'validation/cohort_snapshot_check.json')],
            ['write_dictionary.py'],
        ]
        for command in commands:
            result = subprocess.run([sys.executable, str(target / 'scripts' / command[0]), *command[1:]], cwd=target, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(command[0] + '\n' + result.stdout + result.stderr)
        comparison = {p.name: {'released_sha256':file_sha(p), 'rebuilt_sha256':file_sha(target / 'data' / p.name)} for p in sorted((ROOT / 'data').glob('*.csv'))}
        assert len(comparison) == 15
        matches = all(x['released_sha256'] == x['rebuilt_sha256'] for x in comparison.values())
        report = {'status':'PASS' if matches else 'FAIL', 'data_tables_rebuilt':len(comparison), 'byte_identical':matches, 'tables':comparison}
        text = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(text)
        print(text)
        if not matches: raise SystemExit(1)

if __name__ == '__main__': main()
