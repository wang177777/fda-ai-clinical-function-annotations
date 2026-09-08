#!/usr/bin/env python3
"""Export subject/source-URL provenance flags without changing annotations."""
import argparse, csv, hashlib, json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

def canonical(url):
    p=urlsplit(url)
    return urlunsplit(('https',p.netloc.lower(),p.path,p.query,''))

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    fields=read(args.source_package/'01_Article投稿文件/Supplementary_Data_2/field_taxonomy_9144.csv')
    sources=read(args.source_package/'03_原返回包_只读/evidence/source_manifest.csv')
    pairs={(r['submission_number'],canonical(r['source_document_url'])) for r in sources}
    subject_urls=defaultdict(set)
    for r in sources:subject_urls[r['submission_number']].add(r['source_document_url'])
    grouped=defaultdict(list)
    for r in fields:
        if (r['submission_number'],canonical(r['source_url'])) not in pairs:grouped[r['submission_number'],r['source_url']].append(r)
    rows=[]
    for (sid,url),group in sorted(grouped.items()):
        rows.append({'subject_submission_number':sid,'recorded_source_url':url,'field_count':len(group),'annotation_ids_json':json.dumps([f"{sid}:{r['field']}" for r in group]),'quote_sha256_by_field_json':json.dumps({r['field']:hashlib.sha256(r['evidence_quote'].encode()).hexdigest() for r in group},sort_keys=True),'recorded_locator_by_field_json':json.dumps({r['field']:r['evidence_locator_en'] for r in group},ensure_ascii=False,sort_keys=True),'subject_manifest_urls_json':json.dumps(sorted(subject_urls[sid])),'interpretation':'PROVENANCE_FLAG_NOT_ADJUDICATED_ERROR; original URLs and semantic labels unchanged'})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({'groups':len(rows),'subjects':len({x['subject_submission_number'] for x in rows}),'field_annotations':sum(x['field_count'] for x in rows),'output':str(args.output)},ensure_ascii=False))

if __name__=='__main__':main()
