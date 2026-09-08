#!/usr/bin/env python3
"""Recheck verified spans using the published retained text cache.

Run download_sources.py --group inputs to obtain the default cache. This checks
archived text bytes and substring hashes; it does not estimate semantic accuracy
or perform independent visual verification.
"""
import argparse,json
from collections import Counter
from resource_common import *

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache',type=Path,default=ROOT/'source_materials/input/archive',help='Directory of .txt extraction/excerpt artifacts indexed by SHA-256; default: source_materials/input/archive')
    parser.add_argument('--output',type=Path,help='Optional output JSON; omitted prints summary only')
    args=parser.parse_args()
    if not args.source_cache.is_dir():
        parser.error('Text cache is unavailable; run scripts/download_sources.py --group inputs or supply --source-cache DIRECTORY')
    rows=read_csv(DATA/'evidence_links.csv')
    bridges=read_csv(DATA/'source_bridges.csv') if (DATA/'source_bridges.csv').exists() else []
    required={r['text_sha256'] for r in rows if r['verified_page']!=''}
    required.update(r['text_sha256'] for r in bridges if r['text_sha256'])
    found={}
    for path in sorted(args.source_cache.rglob('*.txt')):
        digest=sha(path)
        if digest in required and digest not in found:found[digest]=path
    pagecache={};counts=Counter();bykind=Counter();failed=[]
    for r in rows:
        if r['verified_page']=='':counts['NO_VERIFIED_SPAN_NOT_RECHECKED']+=1;continue
        digest=r['text_sha256'];path=found.get(digest)
        if path is None:counts['EXTERNAL_CACHE_FILE_NOT_FOUND']+=1;failed.append({'annotation_id':r['annotation_id'],'status':'EXTERNAL_CACHE_FILE_NOT_FOUND','text_sha256':digest});continue
        if digest not in pagecache:pagecache[digest]=pages_from_text(path.read_text(encoding='utf-8-sig'))
        text=pagecache[digest].get(int(r['verified_page']),'')
        part=text[int(r['verified_char_start']):int(r['verified_char_end'])]
        ok=text_sha(part)==r['normalized_quote_sha256'] and len(part)==int(r['normalized_quote_characters'])
        status='VERIFIED_SPAN_HASH_MATCH' if ok else 'VERIFIED_SPAN_HASH_MISMATCH'
        counts[status]+=1;bykind[r['text_source_kind'],status]+=1
        if not ok:failed.append({'annotation_id':r['annotation_id'],'status':status,'text_sha256':digest})
    bridgecounts=Counter();bridgefailed=[]
    for r in bridges:
        digest=r['text_sha256'];path=found.get(digest)
        if path is None:bridgecounts['EXTERNAL_CACHE_FILE_NOT_FOUND']+=1;bridgefailed.append({'bridge_id':r['bridge_id'],'status':'EXTERNAL_CACHE_FILE_NOT_FOUND'});continue
        if digest not in pagecache:pagecache[digest]=pages_from_text(path.read_text(encoding='utf-8-sig'))
        text=pagecache[digest].get(int(r['physical_page']),'')
        part=text[int(r['normalized_char_start']):int(r['normalized_char_end'])]
        ok=text_sha(part)==r['normalized_quote_sha256'] and len(part)==int(r['normalized_quote_characters'])
        status='BRIDGE_SPAN_HASH_MATCH' if ok else 'BRIDGE_SPAN_HASH_MISMATCH'
        bridgecounts[status]+=1
        if not ok:bridgefailed.append({'bridge_id':r['bridge_id'],'annotation_id':r['annotation_id'],'status':status})
    report={'status':'PASS_FOR_AVAILABLE_VERIFIED_SPANS' if not failed and not bridgefailed else 'PARTIAL_OR_FAILED_CACHE_RECHECK','counts':dict(counts),'bridge_anchor_counts':dict(bridgecounts),'required_distinct_text_hashes':len(required),'found_distinct_text_hashes':len(found),'by_artifact_kind':[{'text_source_kind':k,'status':s,'n':n} for (k,s),n in sorted(bykind.items())],'failures':failed,'bridge_failures':bridgefailed,'semantic_accuracy_estimated':False,'independent_image_or_human_review_performed':False,'interpretation':'A text hash match proves only the recorded string location within the supplied archived artifact. A transcription/excerpt remains a transcription/excerpt, not independent OCR/source validation.'}
    if args.output:jsonout(args.output,report)
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
