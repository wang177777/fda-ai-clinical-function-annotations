#!/usr/bin/env python3
"""Offline structural, vocabulary, lineage, checksum and count validation.

This script does not authenticate human judgments or independently repeat the
source-text matching performed during resource assembly.
"""
import argparse, json, re
from collections import Counter,defaultdict
from urllib.parse import urlsplit
from resource_common import *
from validate_release_extensions import validate_extensions
from validate_public_release import validate_public_release


def counter_rows(counter,names):
    return [dict(zip(names,k if isinstance(k,tuple) else (k,)),n=v) for k,v in sorted(counter.items())]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-checksums',action='store_true',help='Author-side rebuild of checksums after a documented change; ordinary users should omit')
    args=parser.parse_args()
    checksum_count=0
    manifest=ROOT/'checksums.sha256'
    if manifest.exists() and not args.refresh_checksums:
        for line in manifest.read_text().splitlines():
            digest,rel=line.split('  ',1)
            path=ROOT/rel
            assert '..' not in Path(rel).parts and not Path(rel).is_absolute()
            assert path.is_file(),f'Missing release file {rel}'
            assert sha(path)==digest,f'Checksum mismatch {rel}'
            checksum_count+=1
    auth=read_csv(DATA/'authorizations.csv');ann=read_csv(DATA/'field_annotations.csv')
    labels=read_csv(DATA/'positive_labels.csv');ev=read_csv(DATA/'evidence_links.csv')
    sources=read_csv(DATA/'source_records.csv');changes=read_csv(DATA/'version_changes.csv')
    aliases=read_csv(DATA/'regulatory_identifier_aliases.csv')
    bridges=read_csv(DATA/'source_bridges.csv') if (DATA/'source_bridges.csv').exists() else []
    relationships=read_csv(DATA/'associated_source_relationships.csv') if (DATA/'associated_source_relationships.csv').exists() else []
    vocab=read_csv(DATA/'vocabulary.csv');checks=read_csv(VALIDATION/'text_locator_checks.csv')
    reviews=read_csv(DATA/'semantic_review_records.csv');review_sources=read_csv(DATA/'semantic_review_sources.csv')
    review_provenance=json.loads((VALIDATION/'semantic_review_provenance.json').read_text())
    aid={r['submission_number']:r for r in auth};fid={r['annotation_id']:r for r in ann}
    eid={r['annotation_id']:r for r in ev};sid={r['source_record_id']:r for r in sources}
    assert len(auth)==len(aid)==1524
    assert len(ann)==len(fid)==len(ev)==len(eid)==len(checks)==9144
    assert len(sources)==len(sid)
    assert set(fid)==set(eid)=={r['annotation_id'] for r in checks}
    assert len({(r['annotation_id'],r['label']) for r in labels})==len(labels)==11120
    assert {(r['field'],r['code']) for r in vocab}=={(f,c) for f in FIELDS for c in ALLOWED[f]}
    actual=defaultdict(set)
    for row in labels:
        assert row['field'] in CONTENT_FIELDS
        assert row['annotation_id']==row['submission_number']+':'+row['field']
        assert row['annotation_id'] in fid
        assert row['label'] in POSITIVE[row['field']]
        actual[row['annotation_id']].add(row['label'])
    limited=Counter();limits_per_auth=Counter();byfield=Counter();expected_changes=[]
    wide={k:{} for k in aid};baseline={k:{} for k in aid}
    for row in ann:
        subject=aid[row['submission_number']];f=row['field'];codes=labelset(row['codes']);old=labelset(row['baseline_codes'])
        assert f in FIELDS and row['annotation_id']==row['submission_number']+':'+f
        assert codes<=ALLOWED[f] and old<=ALLOWED[f]
        assert len(codes)==len(row['codes'].split(';')) and len(old)==len(row['baseline_codes'].split(';'))
        assert not(codes&LIMITED and len(codes)>1)
        islimited=bool(codes&LIMITED)
        assert row['source_limited']==str(islimited).lower()
        assert row['annotation_state']==(next(iter(codes)) if islimited else 'CODED')
        scope=subject['ai_function_scope']
        expected_layer='AI_ATTRIBUTION_BARRIER' if scope==SCOPES[1] else 'SOURCE_INSUFFICIENT' if scope==SCOPES[2] else 'FUNCTION_GROUP_UNRESOLVED' if f=='component_status' and islimited else 'FIELD_NOT_STATED' if islimited else 'NONE'
        assert row['limitation_layer']==expected_layer
        if f in CONTENT_FIELDS:assert actual[row['annotation_id']]==(set() if islimited else codes)
        wide[row['submission_number']][f]=codes;baseline[row['submission_number']][f]=old
        if islimited:limited[f]+=1;limits_per_auth[row['submission_number']]+=1
        for code in codes:byfield[f,code]+=1
        if row['baseline_codes']!=row['codes']:expected_changes.append((row['submission_number'],f,row['baseline_codes'],row['codes']))
    for subject in auth:
        k=subject['submission_number'];scope=subject['ai_function_scope'];oldscope=subject['baseline_ai_function_scope']
        assert scope in SCOPES and oldscope in SCOPES
        assert set(wide[k])==set(FIELDS)
        assert wide[k]['component_status']=={subject['clinical_function_group']}
        assert baseline[k]['component_status']=={subject['baseline_clinical_function_group']}
        if scope!=SCOPES[0]:
            assert all(wide[k][f]=={'NOT_ASSESSABLE'} for f in CONTENT_FIELDS)
            assert wide[k]['component_status']=={'UNCERTAIN'}
        if oldscope!=SCOPES[0]:
            assert all(baseline[k][f]=={'NOT_ASSESSABLE'} for f in CONTENT_FIELDS)
            assert baseline[k]['component_status']=={'UNCERTAIN'}
        if scope!=oldscope:expected_changes.append((k,'ai_function_scope',oldscope,scope))
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',subject['date_of_final_decision'])
    assert sorted(expected_changes)==sorted((r['submission_number'],r['field'],r['baseline_value'],r['current_value']) for r in changes)
    assert len(changes)==16 and len({r['submission_number'] for r in changes})==4
    retained_changes=[r for r in changes if r['change_class'].startswith('RETAINED_')]
    confirmed_changes=[r for r in changes if r['change_class']=='AUTHOR_REPORTED_EXPERT_CONFIRMED_AMENDMENT_2026_09_08']
    assert len(retained_changes)==len(confirmed_changes)==8
    assert {r['submission_number'] for r in retained_changes}=={'K182513','K233662'}
    assert {r['submission_number'] for r in confirmed_changes}=={'K182034','K190013'}
    assert aid['K182513']['ai_function_scope']==SCOPES[0] and aid['K182513']['clinical_function_group']=='SINGLE'
    assert aid['K233662']['ai_function_scope']==SCOPES[2]
    assert sum(limited.values())==772 and len(limits_per_auth)==241
    assert sum(bool(values&LIMITED) for item in baseline.values() for values in item.values())==772
    for row in ev:
        assert urlsplit(row['recorded_source_url']).hostname.endswith('.fda.gov')
        assert all(k in sid for k in row['source_record_ids'].split(';'))
        assert all(canonical(sid[k]['source_url'])==canonical(row['recorded_source_url']) for k in row['source_record_ids'].split(';'))
        for key in ['quote_sha256','normalized_quote_sha256']:assert re.fullmatch('[0-9a-f]{64}',row[key])
        if row['text_sha256']:assert re.fullmatch('[0-9a-f]{64}',row['text_sha256'])
        if row['verified_char_start']!='':
            assert int(row['verified_char_end'])-int(row['verified_char_start'])==int(row['normalized_quote_characters'])
            assert row['locator_check_status'].startswith('EXACT_')
        assert '/Users/' not in '|'.join(row.values()) and not re.search('[\u4e00-\u9fff]','|'.join(row.values()))
    for row in sources:
        assert row['subject_submission_number'] in aid
        assert urlsplit(row['source_url']).hostname.endswith('.fda.gov')
        for key in ['document_sha256','text_sha256']:
            if row[key]:assert re.fullmatch('[0-9a-f]{64}',row[key])
        assert '/Users/' not in '|'.join(row.values())
    assert len(aliases)==1 and aliases[0]['submission_number']=='DEN130013' and aliases[0]['alternate_regulatory_identifier']=='K124067'
    assert len({r['bridge_id'] for r in bridges})==len(bridges)
    for row in bridges:
        assert row['annotation_id'] in fid
        assert row['subject_submission_number']==fid[row['annotation_id']]['submission_number']
        assert all(x in sid for x in row['source_record_ids'].split(';'))
        assert all(canonical(sid[x]['source_url'])==canonical(row['source_url']) for x in row['source_record_ids'].split(';'))
        assert any(sid[x]['document_sha256']==row['document_sha256'] for x in row['source_record_ids'].split(';'))
        assert int(row['normalized_char_end'])-int(row['normalized_char_start'])==int(row['normalized_quote_characters'])
        assert int(row['physical_page'])>0
        assert not re.search('[\u4e00-\u9fff]','|'.join(row.values())) and '/Users/' not in '|'.join(row.values())
    assert len({r['annotation_id'] for r in relationships})==len(relationships)
    for row in relationships:
        assert row['annotation_id'] in fid
        assert row['recorded_source_url']==eid[row['annotation_id']]['recorded_source_url']
        assert not re.search('[\u4e00-\u9fff]','|'.join(row.values())) and '/Users/' not in '|'.join(row.values())
    review_by_id={r['annotation_id']:r for r in reviews}
    review_source_by_id={r['review_source_id']:r for r in review_sources}
    assert len(reviews)==len(review_by_id)==len({r['review_record_id'] for r in reviews})==12
    assert set(review_by_id)=={k+':'+f for k in ['K182034','K190013'] for f in FIELDS}
    assert len(review_sources)==len(review_source_by_id)==6
    assert set(review_source_by_id)=={'R20260908-S0'+str(i) for i in range(1,7)}
    used_review_sources=set();review_change_keys=set()
    for row in reviews:
        key=row['annotation_id'];subject=fid[key]['submission_number'];field=fid[key]['field']
        assert row['post_review_codes']==fid[key]['codes'] and row['pre_review_codes']==fid[key]['baseline_codes']
        assert row['post_review_scope']==aid[subject]['ai_function_scope'] and row['pre_review_scope']==aid[subject]['baseline_ai_function_scope']
        assert row['review_status']=='AUTHOR_REPORTED_EXPERT_CONFIRMATION'
        assert row['review_date']=='2026-09-08' and row['review_date_basis']=='AUTHOR_SUPPLIED_CONFIRMATION_DATE'
        assert row['review_version']=='REVIEW-20260908-v3' and row['confirmation_basis_id']=='HC-20260908-002'
        amended=row['pre_review_codes']!=row['post_review_codes']
        assert row['codes_amended']==str(amended).lower()
        if amended:review_change_keys.add((subject,field,row['pre_review_codes'],row['post_review_codes']))
        if row['pre_review_scope']!=row['post_review_scope']:review_change_keys.add((subject,'ai_function_scope',row['pre_review_scope'],row['post_review_scope']))
        refs=row['review_source_ids'].split(';')
        assert len(refs)==len(set(refs)) and all(x in review_source_by_id for x in refs)
        assert set(re.findall(r'R20260908-S0[1-6]',row['review_locator']))==set(refs)
        used_review_sources.update(refs)
        assert row['new_locator_check_status']=='PAGE_REFERENCES_ONLY_NOT_NEW_MACHINE_SPANS'
        assert row['public_reason'] and not re.search('[\u4e00-\u9fff]','|'.join(row.values())) and '/Users/' not in '|'.join(row.values())
    assert review_change_keys=={(r['submission_number'],r['field'],r['baseline_value'],r['current_value']) for r in confirmed_changes}
    assert len(used_review_sources)==5 and 'R20260908-S06' not in used_review_sources
    for row in review_sources:
        assert row['review_date']==row['reported_source_access_date']=='2026-09-08'
        assert urlsplit(row['source_url']).hostname.endswith('.fda.gov')
        assert row['review_source_role'] in {'TARGET_SUBJECT_SUMMARY','COMPARISON_SUBJECT_SUMMARY','RELATED_VERSION_CONTEXT','REVIEW_LOG_CONTEXT_NOT_FIELD_CITED'}
        assert row['review_document_sha256']==''
        assert all(int(x)>0 for x in row['physical_pages_reviewed'].split(';'))
        source_ids=row['existing_source_record_ids'].split(';') if row['existing_source_record_ids'] else []
        assert all(x in sid and canonical(sid[x]['source_url'])==canonical(row['source_url']) for x in source_ids)
        if row['retained_text_sha256']:
            assert re.fullmatch('[0-9a-f]{64}',row['retained_text_sha256'])
            assert any(sid[x]['text_sha256']==row['retained_text_sha256'] for x in source_ids)
            assert row['review_material_status']=='RETAINED_TEXT_AND_REPORTED_SOURCE_INSPECTION'
        else:assert row['review_material_status']=='URL_AND_REPORTED_SOURCE_INSPECTION'
        assert not re.search('[\u4e00-\u9fff]','|'.join(row.values())) and '/Users/' not in '|'.join(row.values())
    assert sum(bool(r['retained_text_sha256']) for r in review_sources)==3
    assert sum(bool(r['existing_source_record_ids']) for r in review_sources)==4
    assert review_provenance['release_version']=='1.1'
    assert review_provenance['author_reported_confirmation']['supplied_draft_field_positions']==9144
    assert review_provenance['author_reported_confirmation']['supplied_draft_authorizations']==1524
    assert review_provenance['version_reconciliation']['existing_source_amendment_cells_preserved']==8
    assert review_provenance['version_reconciliation']['new_confirmed_amendment_cells']==8
    for name,digest in review_provenance['preserved_data_file_sha256'].items():
        assert Path(name).name==name and sha(DATA/name)==digest,f'Preserved evidence/reference table changed: {name}'
    extension=validate_extensions(aid,fid)
    public_release=validate_public_release()
    # Check documentation coverage and recorded locator projections independently.
    dictionary=read_csv(ROOT/'docs/data_dictionary.csv')
    actual_columns=set()
    for path in DATA.glob('*.csv'):
        rows=read_csv(path)
        for col in rows[0]:actual_columns.add((path.name,col))
        for item in [r for r in dictionary if r['table']==path.name]:
            assert int(item['blank_cells'])==sum(r[item['column']]=='' for r in rows)
    assert {(r['table'],r['column']) for r in dictionary}==actual_columns
    checks_by_id={r['annotation_id']:r for r in checks}
    for row in ev:
        assert all(row[k]==checks_by_id[row['annotation_id']][k] for k in set(row)&set(checks_by_id[row['annotation_id']]))
    scopes=Counter(r['ai_function_scope'] for r in auth)
    groups=Counter(r['clinical_function_group'] for r in auth)
    assert scopes=={SCOPES[0]:1421,SCOPES[1]:101,SCOPES[2]:2}
    assert groups=={'SINGLE':1155,'MULTIPLE':247,'UNCERTAIN':122}
    layers=Counter(r['limitation_layer'] for r in ann)
    status=Counter(r['locator_check_status'] for r in ev)
    text_kinds=Counter((r['text_source_kind'],r['locator_check_status']) for r in ev)
    cross=[r for r in ev if r['source_authorization_relationship']=='OTHER_AUTHORIZATION_NOT_SUBJECT_LINKED_IN_LEGACY_MANIFEST']
    assert {r['annotation_id'] for r in cross}=={r['annotation_id'] for r in relationships}=={r['annotation_id'] for r in bridges}
    granularity=Counter()
    for r in auth:
        output=wide[r['submission_number']]['output']
        nout=0 if output&LIMITED else len(output)
        granularity[r['clinical_function_group'],nout]+=1
    summary={
      'release_status':'GITHUB_VERSIONED_RELEASE',
      'release_version':'1.3.0','semantic_amendment_date':'2026-09-08',
      'cohort_snapshot_access_date':'2026-06-29',
      'unit':'FDA submission-level authorization; not a unique product, internal model, or individual AI function',
      'table_counts':{'authorizations':len(auth),'field_annotations':len(ann),'positive_labels_first_five_fields':len(labels),'evidence_links':len(ev),'source_records':len(sources),'legacy_source_records':sum(r['record_origin']=='LEGACY_SOURCE_MANIFEST' for r in sources),'additional_source_records':sum(r['record_origin']!='LEGACY_SOURCE_MANIFEST' for r in sources),'retained_version_change_cells':len(retained_changes),'confirmed_semantic_amendment_cells':len(confirmed_changes),'total_version_change_cells':len(changes),'regulatory_identifier_alias_rows':len(aliases),'subject_source_bridge_rows':len(bridges),'associated_source_relationship_rows':len(relationships),'semantic_review_records':len(reviews),'semantic_review_sources':len(review_sources)},
      'author_reported_confirmation_scope':review_provenance['author_reported_confirmation'],
      'semantic_review_field_codes_amended':sum(r['codes_amended']=='true' for r in reviews),
      'semantic_review_scope_amendments':sum(r['field']=='ai_function_scope' for r in confirmed_changes),
      'semantic_review_source_references_field_cited':len(used_review_sources),
      'semantic_review_source_references_context_only':len(review_sources)-len(used_review_sources),
      'semantic_review_new_machine_spans':0,
      'source_capture_records_not_unique_documents':True,
      'unique_source_URL_strings':len({r['source_url'] for r in sources}),
      'source_retrieval_status_in_legacy_manifest':dict(Counter(r['retrieval_status'] for r in sources if r['record_origin']=='LEGACY_SOURCE_MANIFEST')),
      'ai_function_scope':dict(scopes),'clinical_function_group':dict(groups),
      'scope_by_function_group':counter_rows(Counter((r['ai_function_scope'],r['clinical_function_group']) for r in auth),['ai_function_scope','clinical_function_group']),
      'source_limited_fields':sum(limited.values()),'source_limited_authorizations':len(limits_per_auth),
      'source_limited_fields_by_domain':dict(limited),'source_limited_fields_by_layer':dict(layers),
      'source_limited_field_count_per_authorization':dict(Counter(limits_per_auth.get(k,0) for k in aid)),
      'baseline_source_limited_fields':772,
      'propagated_source_or_AI_attribution_limited_fields':sum(layers[x] for x in ['AI_ATTRIBUTION_BARRIER','SOURCE_INSUFFICIENT']),
      'within_AI_attributed_limited_fields':sum(layers[x] for x in ['FIELD_NOT_STATED','FUNCTION_GROUP_UNRESOLVED']),
      'within_AI_attributed_authorizations_with_any_limited_field':sum(r['ai_function_scope']==SCOPES[0] and limits_per_auth.get(r['submission_number'],0)>0 for r in auth),
      'label_frequencies':counter_rows(byfield,['field','code']),
      'output_label_breadth_by_function_group':counter_rows(granularity,['clinical_function_group','output_label_count']),
      'single_function_with_multiple_output_labels':sum(v for (g,n),v in granularity.items() if g=='SINGLE' and n>=2),
      'multiple_function_with_single_output_label':granularity['MULTIPLE',1],
      'assembly_text_locator_check_status':dict(status),
      'assembly_text_locator_check_by_source_kind':counter_rows(text_kinds,['text_source_kind','locator_check_status']),
      'assembly_verified_exact_anchors':sum(n for k,n in status.items() if k.startswith('EXACT_')),
      'mechanically_added_alternative_anchor_fields':sum(n for k,n in status.items() if k.startswith('EXACT_QUOTE_MATCH_')),
      'cross_authorization_URL_fields':len(cross),'cross_authorization_URL_subjects':len({r['annotation_id'].split(':')[0] for r in cross}),'cross_authorization_subject_URL_pairs':len({(r['annotation_id'].split(':')[0],r['recorded_source_url']) for r in cross}),
      'source_authorization_relationship':dict(Counter(r['source_authorization_relationship'] for r in ev)),
      'subject_source_bridge_purposes':dict(Counter(r['anchor_purpose'] for r in bridges)),
      'associated_source_relation_categories':dict(Counter(r['source_relationship'] for r in relationships)),
      'associated_source_caution_codes':dict(Counter(code for r in relationships for code in r['source_caution_codes'].split(';') if code)),
      'all_quoted_texts_relocated_claimed':False,'semantic_accuracy_or_human_reliability_estimated':False,
      'validation_scope':'Offline validator checks schema, keys, vocabulary, propagation, baseline changes, counts and file hashes. Assembly text matching is separately classified by extract/transcription/web-excerpt provenance; no semantic accuracy or human agreement is estimated.'
    }
    summary['table_counts'].update({k:extension[k] for k in ['cohort_snapshot_membership','cohort_snapshot_manifest','other_label_notes']})
    summary['release_1_2_documentation']=extension
    summary['release_1_3_public_sources']=public_release
    jsonout(VALIDATION/'summary.json',summary)
    report={'status':'PASS_STRUCTURAL_AND_MECHANICAL_ACCOUNTING','release_version':'1.3.0','checks':['1524 unique authorization keys','9144 unique authorization-field keys and exact six-field coverage','11120 unique positive-content-label keys','9144 annotation-evidence links with resolvable source records','Allowed vocabularies and no positive/limited mixing','Explicit propagation of source/AI-attribution barriers','Eight retained amendments plus eight confirmed semantic amendments across four authorizations','12 semantic-review records and six review references with resolvable keys','New review page references kept separate from preserved exact machine anchors','Data-dictionary coverage and blank-cell counts','Source URL, hash and locator syntax','Complete missing-state and source-check accounting'], 'technical_limits_not_validation_failures':{'image_transcription_anchors_not_rechecked':status['RECORDED_IMAGE_TRANSCRIPTION_NOT_RECHECKED'],'page_only_references_without_machine_anchor':status['NO_MACHINE_TEXT_ANCHOR'],'quotes_on_multiple_pages_without_auto_anchor_choice':status['QUOTE_PRESENT_MULTIPLE_PAGES_NO_AUTOMATIC_CORRECTION'],'cross_authorization_URL_fields_requiring_cautious_use':len(cross),'new_semantic_review_records_with_page_references_only':len(reviews)},'author_reported_expert_confirmation_recorded':True,'offline_independent_semantic_validation':False,'independent_human_accuracy_or_reliability':None}
    report['checks'].extend(['1524 historical cohort row mappings and three original-artifact fingerprints','789 OTHER memberships with 206 retained notes and 583 explicitly unseparated contexts'])
    jsonout(VALIDATION/'validation_report.json',report)
    if args.refresh_checksums or not manifest.exists():checksum_release()
    print(json.dumps({'status':report['status'],'table_counts':summary['table_counts'],'checked_release_checksums':checksum_count,'technical_limits':report['technical_limits_not_validation_failures']},ensure_ascii=False))

if __name__=='__main__':main()
