#!/usr/bin/env python3
"""Append factual subject/associated-source anchors without replacing old evidence.

Author-held relationship-review CSV is converted without copying its long
quotations, private paths, reviewer metadata or internal action/status fields.
"""
import argparse,json
from collections import Counter
from resource_common import *

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review-file',type=Path,required=True)
    args=parser.parse_args()
    review=read_csv(args.review_file)
    fields={r['annotation_id']:r for r in read_csv(DATA/'field_annotations.csv')}
    evidence={r['annotation_id']:r for r in read_csv(DATA/'evidence_links.csv')}
    sources=read_csv(DATA/'source_records.csv')
    sourceindex={}
    for row in sources:sourceindex.setdefault(canonical(row['source_url']),[]).append(row)
    bridges=[];relationships=[];additions=[]
    categories={'subject_bridge_anchors_json':'SUBJECT_TO_ASSOCIATED_SOURCE_BRIDGE','additional_chain_anchors_json':'INTERMEDIATE_SOURCE_CHAIN_BRIDGE','own_source_alternative_anchors_json':'SUBJECT_SOURCE_ADDITIONAL_DETAIL'}
    for r in sorted(review,key=lambda x:x['annotation_id']):
        aid=r['annotation_id'];assert aid in fields
        assert r['semantic_label_change']=='NONE'
        assert r['retained_revised_codes']==fields[aid]['codes']
        assert r['original_quote_sha256']==evidence[aid]['quote_sha256']
        assert r['recorded_source_url']==evidence[aid]['recorded_source_url']
        relationships.append({'annotation_id':aid,'recorded_source_url':r['recorded_source_url'],'subject_source_url':r['subject_source_url'],'source_relationship':r['source_relation_review'],'support_scope_note':r['support_boundary'],'source_caution_codes':r['warning_codes']})
        for field,purpose in categories.items():
            for anchor in json.loads(r[field]):
                url=anchor['source_url'];q=normalize(anchor['exact_excerpt']);start=int(anchor['normalized_char_start']);end=int(anchor['normalized_char_end'])
                assert len(q)==end-start
                matches=[s for s in sourceindex.get(canonical(url),[]) if s['document_sha256']==anchor['pdf_sha256']]
                if not matches:
                    item={'source_record_id':'BRG'+text_sha(url+'|'+anchor['pdf_sha256'])[:12],'subject_submission_number':anchor['subject_submission_number'],'source_url':url,'source_document_type':'FDA_PDF_BRIDGE_REFERENCE','document_sha256':anchor['pdf_sha256'],'text_sha256':'','retrieval_date':'','retrieval_status':'HASH_VERIFIED_DURING_BRIDGE_REVIEW','record_origin':'ADDITIONAL_BRIDGE_REFERENCE'}
                    if item['source_record_id'] not in {s['source_record_id'] for s in sources}:sources.append(item);additions.append(item)
                    matches=[item]
                known_texts={s['text_sha256'] for s in matches if s['text_sha256']}
                text_hash=next(iter(known_texts)) if len(known_texts)==1 else ''
                identifier='BRIDGE'+text_sha('|'.join([aid,purpose,url,str(anchor['physical_page']),str(start),str(end),text_sha(q)]))[:16]
                bridges.append({'bridge_id':identifier,'annotation_id':aid,'subject_submission_number':aid.split(':')[0],'anchor_document_submission_number':anchor['subject_submission_number'],'anchor_purpose':purpose,'source_url':url,'source_record_ids':';'.join(sorted(s['source_record_id'] for s in matches)),'document_sha256':anchor['pdf_sha256'],'text_sha256':text_hash,'physical_page':int(anchor['physical_page']),'normalized_char_start':start,'normalized_char_end':end,'quote_sha256':text_sha(anchor['exact_excerpt']),'normalized_quote_sha256':text_sha(q),'normalized_quote_characters':len(q)})
    assert len({r['bridge_id'] for r in bridges})==len(bridges)
    csvout(DATA/'source_bridges.csv',sorted(bridges,key=lambda r:(r['annotation_id'],r['anchor_purpose'],r['source_url'],r['physical_page'],r['normalized_char_start'])))
    csvout(DATA/'associated_source_relationships.csv',relationships)
    csvout(DATA/'source_records.csv',sources)
    jsonout(VALIDATION/'bridge_input_provenance.json',{'file_name':args.review_file.name,'sha256':sha(args.review_file),'reviewed_annotation_records':len(review),'annotation_labels_changed':0,'old_URLs_or_quotations_replaced':0,'public_long_quotations_copied':0,'method':'AI-assisted source-relationship review and exact-text location; not independent human semantic validation','source_relationships':dict(Counter(r['source_relationship'] for r in relationships)),'anchor_purposes':dict(Counter(r['anchor_purpose'] for r in bridges)),'additional_source_capture_records':len(additions)})
    print({'relationship_records':len(relationships),'bridge_anchor_rows':len(bridges),'additional_source_capture_records':len(additions)})

if __name__=='__main__':main()
