#!/usr/bin/env python3
"""Download, verify and extract the versioned scientific source archives."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import shlex
import stat
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def extract_archive(path, destination):
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        for item in members:
            rel = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            if (rel.is_absolute() or '..' in rel.parts or '\\' in item.filename
                    or not rel.parts or rel.parts[0] != 'source_materials'
                    or stat.S_ISLNK(mode)):
                raise ValueError(f'Unsafe archive member: {item.filename}')
            target = (destination / item.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError(f'Archive path leaves destination: {item.filename}')
        for item in members:
            target = destination / item.filename
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.extracting')
            with archive.open(item) as source, temporary.open('wb') as out:
                shutil.copyfileobj(source, out, 1024 * 1024)
            temporary.replace(target)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['all', 'inputs', 'documents'], default='all')
    parser.add_argument('--archive-dir', type=Path, default=ROOT / '.source_archives', help='Use already downloaded archives here, or download missing files into it')
    parser.add_argument('--destination', type=Path, default=ROOT, help='Repository root for extraction')
    args = parser.parse_args()
    archives = json.loads((ROOT / 'source_materials/archives.json').read_text())['archives']
    selected = [x for x in archives if args.group == 'all' or x['group'] == args.group]
    args.archive_dir.mkdir(parents=True, exist_ok=True)
    args.destination.mkdir(parents=True, exist_ok=True)
    for item in selected:
        assert Path(item['name']).name == item['name']
        local = args.archive_dir / item['name']
        if not local.exists():
            print('Downloading ' + item['name'], flush=True)
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'clinical-function-annotations/1.3.0'})
            temporary = local.with_suffix(local.suffix + '.part')
            with urllib.request.urlopen(request, timeout=120) as response, temporary.open('wb') as out:
                shutil.copyfileobj(response, out, 1024 * 1024)
            temporary.replace(local)
        if local.stat().st_size != item['bytes'] or file_sha(local) != item['sha256']:
            raise ValueError(f'Archive checksum mismatch: {local}. Remove this file and download it again.')
        extract_archive(local, args.destination)
        print(f"Verified and extracted {item['name']} ({item['files']} files)", flush=True)
    next_command=['python3','scripts/validate_sources.py','--group',args.group]
    if args.destination.resolve()!=ROOT.resolve():
        next_command.extend(['--destination',str(args.destination.resolve())])
    print('Source archives ready. Run ' + shlex.join(next_command), flush=True)

if __name__ == '__main__':
    main()
