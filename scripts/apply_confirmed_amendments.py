#!/usr/bin/env python3
"""Apply the eight confirmed 2026-09-08 amendments to the enriched 1.0 release.

Rebuilding accepts the distributed scientific confirmation input or the
retained author-side package. The supplied draft is checked against historical
baseline columns and is not substituted for the current release. The English
review summaries below are a curated projection of the fingerprinted input.
No source retrieval, source-text matching, signing, or independent scoring is
performed. Run the dictionary generator and validator after this script.
"""
import argparse
from collections import Counter
import re
from resource_common import *

VERSION='1.1'
REVIEW_DATE='2026-09-08'
BASIS='HC-20260908-002'
DATE_BASIS='DATE-20260908-003'
INPUTS={
 'confirmation_records':('07_*.csv','a758543cfe8ba1f00b0d3b8b65af34b6c4017f01c143d0b5cf93897487b82131'),
 'confirmation_fields':('08_*.csv','3cb99bf2195ee0b2ad6534c80f0d74add392848255ac672112a4660f3ec336b6'),
 'change_log':('09_*.csv','a254afff777a123722bf3ee4fd8bd7b537258fb2733a9d9f7bf6d881f899ffc3'),
 'review_source_log':('04_*.csv','7b582cb31cac7476e9b6c28e20c4a96c3431067fc45e0f7a9b316ec3a712b387'),
 'confirmation_statement':('10_*.json','d4a3fed9622b08e06153c576b28ba334b17997371efdcbb92b5719a3ed984784'),
 'confirmation_date_statement':('11_*.json','944110c7a89403412fdd6246be0b4a03d52f6cfe42c788c7ccfc9418020efdb7'),
}
REVIEW_TEXT={
 'K182034:input':('The Cardio and Oncology modules process MR and CT clinical images.','S01, physical PDF pages 4-6: device description, module indications, and modality entries.',['S01']),
 'K182034:output':('Semiautomatic region-of-interest segmentation and automatically generated, editable landmarks and contours support segmentation/localization alongside quantitative measurements.','S01, physical PDF pages 5-7; page 7, Table 5.1, proposed-device column: segmentation, landmarks, and contours.',['S01']),
 'K182034:user':('The indications specify trained healthcare professionals without restricting use to a particular medical specialty.','S01, physical PDF page 5: final paragraph of Indications for Use.',['S01']),
 'K182034:setting':('The described clinical contexts are image interpretation and oncology lesion follow-up.','S01, physical PDF page 5: Oncology AI indications and shared intended-use statements.',['S01']),
 'K182034:action':('The modules support clinicians in clinical interpretation and lesion follow-up, with diagnostic responsibility retained by the clinician.','S01, physical PDF page 5: interpretation and follow-up indications, including diagnostic responsibility.',['S01']),
 'K182034:component_status':('Cardio AI and Oncology AI have distinguishable clinical purposes, supporting multiple clinical functions.','S01, physical PDF pages 5-6: separately described Cardio AI and Oncology AI indications.',['S01']),
 'K190013:input':('Device-level inputs include glucose values, carbohydrate information, and prescribed regimens; delayed CGM data are display-only. Attribution of these inputs to the target AI/algorithmic function remains unresolved.','S02, physical PDF pages 4 and 6: prescription-calculation inputs, data entry, and restrictions on CGM display.',['S02']),
 'K190013:output':('The device provides coaching and prescribed-dose recommendations. The described linear decay calculation does not resolve attribution of these outputs to the target AI/algorithmic function.','S02, physical PDF pages 4 and 6: coaching and calculator functions; page 10, Comment 1. S04, physical PDF page 8: related-version functions.',['S02','S04']),
 'K190013:user':('The device is intended for healthcare professionals and adult patients. Attribution of these users to the target AI/algorithmic function remains unresolved.','S02, physical PDF pages 3-4 and 7: indications for healthcare professionals and adult patients.',['S02']),
 'K190013:setting':('The device is intended for home and professional healthcare environments, without specifying inpatient or outpatient use. The target AI/algorithmic use context remains unresolved.','S02, physical PDF pages 3-4: home and professional healthcare environments.',['S02']),
 'K190013:action':('The device supports self-management and insulin dose calculation from prescribed regimens. Attribution of these actions to the target AI/algorithmic function remains unresolved.','S02, physical PDF pages 4 and 6: self-management, prescription-based calculation, and continued professional care.',['S02']),
 'K190013:component_status':('The two described device purposes have not been sufficiently attributed to the target AI/algorithmic function to resolve clinical function grouping.','S02, physical PDF pages 4, 6, and 10; S04, physical PDF pages 8-9; S05, physical PDF page 7; comparison with S03, physical PDF pages 5-6.',['S02','S04','S05','S03']),
}
# id, document identifier, URL, pages, role, retained text SHA, report of access
SOURCE_TEXT=[
 ('S01','K182034','https://www.accessdata.fda.gov/cdrh_docs/pdf18/K182034.pdf','4;5;6;7','TARGET_SUBJECT_SUMMARY','6fe39e71121c36c7ad269620f0ac3808fd7e417883e9c69c73623aa4583f3122','Text and images of pages 5-7 were reported reviewed; no newly downloaded PDF bytes were supplied.'),
 ('S02','K190013','https://www.accessdata.fda.gov/cdrh_docs/pdf19/K190013.pdf','3;4;5;6;7;8;9;10','TARGET_SUBJECT_SUMMARY','31055010769b1a9ffaf77cf145399104d5cc5deb936875823aed318f412d709c','Readable text and images of pages 4 and 6 were reported reviewed. Page 10 image capture failed; that reference is limited to readable text. No newly downloaded PDF bytes were supplied.'),
 ('S03','K150817','https://www.accessdata.fda.gov/cdrh_docs/pdf15/K150817.pdf','5;6','COMPARISON_SUBJECT_SUMMARY','f5c67023c0f210c4a22190eff5db99c7f55c6f4653699833fdf8de85b511a21d','Text and images of pages 5-6 were reported reviewed for comparison; no newly downloaded PDF bytes were supplied.'),
 ('S04','K162532','https://www.accessdata.fda.gov/cdrh_docs/pdf16/K162532.pdf','7;8;9','RELATED_VERSION_CONTEXT','','Readable text was reported reviewed; page 8 image capture failed. Only the URL and review log were supplied. Earlier-version features are not automatically transferred to the target subject.'),
 ('S05','K162225','https://www.accessdata.fda.gov/cdrh_docs/pdf16/K162225.pdf','7','RELATED_VERSION_CONTEXT','','Page 7 imagery was reported reviewed because text order was poor. Only the URL and review log were supplied.'),
 ('S06','K150817','https://www.accessdata.fda.gov/cdrh_docs/reviews/K150817.pdf','1;2;3;4;5','REVIEW_LOG_CONTEXT_NOT_FIELD_CITED','','Relevant text and page 3 imagery were reported reviewed for context. Only the URL and review log were supplied; this source is not linked to any of the 12 targeted field records.'),
]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--confirmation-package',type=Path,help='Retained author-side confirmation package')
    inputs.add_argument('--public-review-input',type=Path,help='Scientific public-review projection JSON with relative CSV/text paths and fingerprints')
    parser.add_argument('--repository',type=Path,default=ROOT,help='Existing enriched release 1.0, or the already integrated 1.1 release for an idempotence check')
    args=parser.parse_args();root=args.repository.resolve();data=root/'data';validation=root/'validation'
    paths={};fingerprints=[];public_review=None
    if args.public_review_input:
        projection_path=args.public_review_input.resolve()
        public_review=json.loads(projection_path.read_text(encoding='utf-8'))
        scientific=public_review['scientific_provenance']
        assert scientific['confirmation_basis_id']==BASIS and scientific['date_basis_id']==DATE_BASIS
        assert scientific['independent_dual_review_established'] is False
        assert scientific['author_reported_confirmation']['reported_confirmation_date']==REVIEW_DATE
        assert scientific['author_reported_confirmation']['supplied_draft_authorizations']==1524
        assert scientific['author_reported_confirmation']['supplied_draft_field_positions']==9144
        roles={'confirmation_records','confirmation_fields','change_log','review_source_log'}
        assert set(public_review['inputs'])==roles
        for role in sorted(roles):
            item=public_review['inputs'][role];path=(projection_path.parent/item['file']).resolve()
            assert path.is_relative_to(projection_path.parent)
            assert item['original_sha256']==INPUTS[role][1]
            assert sha(path)==item['public_sha256'] and path.stat().st_size==item['public_bytes'],role
            paths[role]=path;fingerprints.append({'input_role':role,'bytes':path.stat().st_size,'sha256':sha(path),'original_file_sha256':item['original_sha256'],'original_file_bytes':item['original_bytes'],'public_projection_transformation':item['transformation']})
        supplied_cache_hashes=set()
        for item in public_review['text_artifacts']:
            path=(projection_path.parent/item['file']).resolve()
            assert path.is_relative_to(projection_path.parent)
            assert sha(path)==item['sha256'];supplied_cache_hashes.add(item['sha256'])
    else:
        for role,(pattern,expected) in INPUTS.items():
            found=list(args.confirmation_package.glob(pattern));assert len(found)==1,role
            path=found[0];assert sha(path)==expected,f'Unexpected confirmation input for {role}; review it before changing this version-specific projection'
            paths[role]=path;fingerprints.append({'input_role':role,'bytes':path.stat().st_size,'sha256':expected})
        statement=json.loads(paths['confirmation_statement'].read_text(encoding='utf-8'))
        dates=json.loads(paths['confirmation_date_statement'].read_text(encoding='utf-8'))
        assert statement['id']==BASIS and statement['independent_dual_review_claimed'] is False
        assert dates['id']==DATE_BASIS and dates['reported_review_confirmation_date']==REVIEW_DATE and dates['signatures_supplied'] is False
        supplied_cache_hashes={sha(p) for p in args.confirmation_package.rglob('*.txt')}
    supplied_fields=read_csv(paths['confirmation_fields']);supplied_records=read_csv(paths['confirmation_records']);supplied_changes=read_csv(paths['change_log'])
    auth=read_csv(data/'authorizations.csv');fields=read_csv(data/'field_annotations.csv');changes=read_csv(data/'version_changes.csv');sources=read_csv(data/'source_records.csv')
    aid={r['submission_number']:r for r in auth};fid={r['annotation_id']:r for r in fields}
    sfid={r['submission_number']+':'+r['field']:r for r in supplied_fields}
    said={r['submission_number']:r for r in supplied_records}
    assert len(aid)==len(said)==len(supplied_records)==1524 and set(aid)==set(said)
    assert len(fid)==len(sfid)==len(supplied_fields)==9144 and set(fid)==set(sfid)
    assert all(sfid[k]['baseline_codes']==r['baseline_codes'] for k,r in fid.items())
    assert all(sfid[k+':input']['baseline_scope']==r['baseline_ai_function_scope'] for k,r in aid.items())
    target_keys={r['submission_number']+':'+r['field'] for r in supplied_changes if r['field']!='scope'}
    assert len(supplied_changes)==8 and len(target_keys)==7
    assert target_keys=={'K182034:output'}|{'K190013:'+f for f in FIELDS}
    assert {(r['submission_number'],r['field']) for r in supplied_changes if r['field']=='scope'}=={('K190013','scope')}
    assert len(changes) in {8,16}
    # Existing source corrections are part of this release and are not rolled back.
    assert aid['K182513']['ai_function_scope']==SCOPES[0] and fid['K182513:input']['codes']=='LAB_SPECIMEN_OR_OMICS'
    assert aid['K182513']['clinical_function_group']=='SINGLE' and aid['K233662']['ai_function_scope']==SCOPES[2]
    retained=[r for r in changes if r['change_class'].startswith('RETAINED_')]
    assert len(retained)==8 and {r['submission_number'] for r in retained}=={'K182513','K233662'}
    keep_names=['evidence_links.csv','source_records.csv','source_bridges.csv','associated_source_relationships.csv','regulatory_identifier_aliases.csv','vocabulary.csv']
    kept={name:sha(data/name) for name in keep_names}
    newchanges=[]
    for item in supplied_changes:
        subject=item['submission_number'];field=item['field'];old=item['baseline_value'];new=item['current_value']
        assert item['confirmation_basis_id']==BASIS and item['actual_review_date']==REVIEW_DATE
        if field=='scope':
            assert aid[subject]['ai_function_scope'] in {old,new};aid[subject]['ai_function_scope']=new;field='ai_function_scope'
        else:
            assert fid[subject+':'+field]['codes'] in {old,new}
            fid[subject+':'+field]['codes']=new
            if field=='component_status':aid[subject]['clinical_function_group']=new
        newchanges.append({'submission_number':subject,'field':field,'baseline_value':old,'current_value':new,'change_class':'AUTHOR_REPORTED_EXPERT_CONFIRMED_AMENDMENT_2026_09_08'})
    combined=sorted(retained+newchanges,key=lambda r:(r['submission_number'],r['field']))
    assert len(combined)==16 and len({r['submission_number'] for r in combined})==4
    labels=[]
    for row in fields:
        scope=aid[row['submission_number']]['ai_function_scope'];f=row['field'];codes=labelset(row['codes']);limited=bool(codes&LIMITED)
        row['annotation_state']=row['codes'] if limited else 'CODED';row['source_limited']=str(limited).lower()
        row['limitation_layer']='AI_ATTRIBUTION_BARRIER' if scope==SCOPES[1] else 'SOURCE_INSUFFICIENT' if scope==SCOPES[2] else 'FUNCTION_GROUP_UNRESOLVED' if f=='component_status' and limited else 'FIELD_NOT_STATED' if limited else 'NONE'
        if f in CONTENT_FIELDS and not limited:
            for code in sorted(codes):labels.append({'annotation_id':row['annotation_id'],'submission_number':row['submission_number'],'field':f,'label':code})
    assert len(labels)==11120 and sum(r['source_limited']=='true' for r in fields)==772
    # Verify the supplied cache bytes without publishing source text or paths.
    required_hashes={row[5] for row in SOURCE_TEXT if row[5]}
    assert required_hashes<=supplied_cache_hashes
    review_sources=[]
    for short,subject,url,pages,role,digest,note in SOURCE_TEXT:
        matched=[r['source_record_id'] for r in sources if canonical(r['source_url'])==canonical(url)]
        if digest:assert any(r['text_sha256']==digest for r in sources if r['source_record_id'] in matched)
        review_sources.append({'review_source_id':'R20260908-'+short,'review_date':REVIEW_DATE,'source_document_submission_number':subject,'source_url':url,'physical_pages_reviewed':pages,'review_source_role':role,'existing_source_record_ids':';'.join(matched),'review_document_sha256':'','retained_text_sha256':digest,'review_material_status':'RETAINED_TEXT_AND_REPORTED_SOURCE_INSPECTION' if digest else 'URL_AND_REPORTED_SOURCE_INSPECTION','reported_source_access_date':REVIEW_DATE,'source_access_note':note})
    reviews=[]
    for key in sorted(REVIEW_TEXT):
        reason,locator,refs=REVIEW_TEXT[key];row=sfid[key];subject=key.split(':')[0]
        assert row['current_codes']==fid[key]['codes'] and row['current_scope']==aid[subject]['ai_function_scope']
        reviews.append({'review_record_id':'R20260908-'+key,'annotation_id':key,'review_version':'REVIEW-20260908-v3','review_date':REVIEW_DATE,'confirmation_basis_id':BASIS,'review_date_basis':'AUTHOR_SUPPLIED_CONFIRMATION_DATE','review_status':'AUTHOR_REPORTED_EXPERT_CONFIRMATION','pre_review_codes':row['baseline_codes'],'post_review_codes':row['current_codes'],'pre_review_scope':row['baseline_scope'],'post_review_scope':row['current_scope'],'codes_amended':str(row['baseline_codes']!=row['current_codes']).lower(),'review_source_ids':';'.join('R20260908-'+x for x in refs),'review_locator':re.sub(r'S0[1-6]',lambda m:'R20260908-'+m.group(),locator),'public_reason':reason,'new_locator_check_status':'PAGE_REFERENCES_ONLY_NOT_NEW_MACHINE_SPANS'})
    assert len(reviews)==12 and sum(r['codes_amended']=='true' for r in reviews)==7
    csvout(data/'authorizations.csv',auth);csvout(data/'field_annotations.csv',fields);csvout(data/'positive_labels.csv',labels);csvout(data/'version_changes.csv',combined)
    csvout(data/'semantic_review_records.csv',reviews);csvout(data/'semantic_review_sources.csv',review_sources)
    assert all(sha(data/name)==digest for name,digest in kept.items())
    provenance={
      'release_version':VERSION,'integration_date':REVIEW_DATE,'confirmation_input_version':'REVIEW-20260908-v3','confirmation_basis_id':BASIS,'date_basis_id':DATE_BASIS,'inputs':fingerprints,
      'author_reported_confirmation':{'supplied_draft_authorizations':1524,'supplied_draft_field_positions':9144,'clinical_reviewers':['Xiaonan Yang','Weixin Wang'],'reported_confirmation_date':REVIEW_DATE,'review_date_basis':'Author-supplied confirmation date; not individual reading or signing timestamps','covered_material':'Supplied-draft field labels, assessment states, function attribution, rationales, and source locators','reported_procedure':'Discussion between the two reviewers. Unresolved disagreements were to be referred to Zuoliang Qi.','actual_adjudicated_case_count':None,'paired_independent_initial_ratings_available':False,'interrater_agreement_estimated':False},
      'version_reconciliation':{'supplied_draft_matches_release_historical_baseline':True,'historical_baseline_field_keys_matched':9144,'historical_baseline_authorization_scopes_matched':1524,'existing_source_amendment_cells_preserved':8,'existing_source_amendment_subjects':['K182513','K233662'],'new_confirmed_amendment_cells':8,'new_confirmed_field_cells':7,'new_confirmed_scope_cells':1,'new_confirmed_subjects':['K182034','K190013'],'cumulative_changed_cells':16,'cumulative_changed_authorizations':4,'interpretation':'Confirmation concerns the supplied historical draft and two targeted decisions. Prior source amendments in the current release remain separately versioned; their reversal was not inferred from the older supplied baseline.'},
      'public_review_layer':{'targeted_field_review_records':12,'review_source_references':6,'field_cited_review_sources':5,'context_only_review_sources':1,'new_exact_machine_anchors_claimed':0,'new_pdf_capture_hashes_claimed':0,'retained_text_artifacts_supplied_and_hash_checked':3},
      'preserved_data_file_sha256':kept,'AI_assistance':'Codex (OpenAI) assisted with English projection, increment assembly, scripts, and structural checks. Substantive AI-assistance provenance remains disclosed.',
      'private_materials_redistributed':False,'personal_signature_artifacts_supplied':0,'independent_dual_review_established':False,'semantic_accuracy_estimated':False,
    }
    if public_review is not None:
        provenance.update(reconstruction_input_mode='PUBLIC_SCIENTIFIC_REVIEW_PROJECTION',public_review_input_sha256=sha(projection_path),original_administrative_declarations_required=False)
    jsonout(validation/'semantic_review_provenance.json',provenance)
    print(json.dumps({'release_version':VERSION,'new_amendment_cells':8,'cumulative_amendment_cells':16,'positive_label_memberships':len(labels),'semantic_review_records':len(reviews),'semantic_review_sources':len(review_sources),'original_machine_evidence_unchanged':True,'next_steps':'Run write_dictionary.py and validate_resource.py --refresh-checksums, then validate_resource.py without refresh.'}))

if __name__=='__main__':main()
