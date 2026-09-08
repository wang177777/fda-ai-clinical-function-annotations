#!/usr/bin/env python3
"""Build sanitized normalized tables from the retained source package.

Supports both the retained author-side layout and the public source_materials
input layout. The public projection records original and distributed input
fingerprints separately. This step does not change semantic labels.
"""
import argparse, csv, re, shutil
from collections import Counter, defaultdict
from pathlib import Path
from resource_common import *


def locator_parts(locator):
    path=locator.split('|')[0].strip() if '|' in locator else ''
    page_match=re.search(r'(?:PDF physical page|physical page)\s+([0-9, ]+)',locator,re.I)
    pages=[int(x) for x in re.findall(r'\d+',page_match.group(1))] if page_match else []
    html='HTML extracted text' in locator
    span=re.search(r'normalized characters\s+(\d+):(\d+)',locator)
    image='图像' in locator
    return path,pages,html,(int(span[1]),int(span[2])) if span else None,image


def public_locator(pages,html,span,image=False):
    head='HTML extracted text (logical marker 0, not a PDF page)' if html else 'PDF physical page(s): '+', '.join(map(str,pages)) if pages else 'No physical page recorded'
    if span:head+=f'; whitespace-normalized characters [{span[0]}, {span[1]}) (zero-based)'
    if image:head+='; recorded image-excerpt transcription, not verified as extracted text'
    return head


def mechanical_check(row,archive,cache):
    raw_path,pages,html,span,image=locator_parts(row['evidence_locator_en'])
    q=normalize(row['evidence_quote'])
    result={'annotation_id':row['submission_number']+':'+row['field'],'recorded_locator_en':public_locator(pages,html,span,image),'recorded_pages':';'.join(map(str,pages)),'recorded_char_start':span[0] if span else '', 'recorded_char_end':span[1] if span else '', 'text_sha256':'','normalized_quote_sha256':text_sha(q),'normalized_quote_characters':len(q),'verified_page':'','verified_char_start':'','verified_char_end':'','verified_locator_en':'','text_source_kind':'PAGE_ONLY_REFERENCE','locator_check_status':'NO_MACHINE_TEXT_ANCHOR'}
    if not raw_path:return result
    path=archive/raw_path
    if not path.exists():result['locator_check_status']='SOURCE_TEXT_CACHE_UNAVAILABLE';return result
    if raw_path not in cache:
        tx=path.read_text(encoding='utf-8-sig')
        cache[raw_path]={'sha':sha(path),'pages':pages_from_text(tx)}
    cached=cache[raw_path]
    result['text_sha256']=cached['sha']
    kind='STORED_IMAGE_TRANSCRIPTION' if raw_path.startswith('derived_sources/') else 'STORED_WEB_EXCERPT' if raw_path.startswith('supplemental_sources/') else 'FDA_HTML_EXTRACT' if html else 'FDA_PDF_TEXT_EXTRACT'
    result['text_source_kind']=kind
    if image:
        result['locator_check_status']='RECORDED_IMAGE_TRANSCRIPTION_NOT_RECHECKED'
        return result
    if not span:
        result['locator_check_status']='NO_RECORDED_CHARACTER_SPAN'
        return result
    pageno=0 if html else pages[0] if pages else None
    ptext=cached['pages'].get(pageno,'')
    if q==ptext[span[0]:span[1]]:
        vp,vs,ve=pageno,span[0],span[1]
        result['locator_check_status']='EXACT_RECORDED_SPAN_MATCH'
    elif q and q in ptext:
        vp,vs=pageno,ptext.index(q);ve=vs+len(q)
        result['locator_check_status']='EXACT_QUOTE_MATCH_CORRECTED_SPAN_SAME_PAGE'
    else:
        hits=[(p,txt.index(q)) for p,txt in cached['pages'].items() if q and q in txt]
        if len(hits)==1:
            vp,vs=hits[0];ve=vs+len(q)
            result['locator_check_status']='EXACT_QUOTE_MATCH_CORRECTED_PAGE_OR_SPAN'
        elif len(hits)>1:
            result['locator_check_status']='QUOTE_PRESENT_MULTIPLE_PAGES_NO_AUTOMATIC_CORRECTION';return result
        else:
            result['locator_check_status']='QUOTE_NOT_EXACTLY_FOUND_IN_STORED_TEXT';return result
    result.update(verified_page=vp,verified_char_start=vs,verified_char_end=ve,verified_locator_en=public_locator([] if vp==0 else [vp],vp==0,(vs,ve)))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-package',type=Path,required=True)
    args=parser.parse_args()
    package=args.source_package
    public_input=None
    for candidate in [package/'input',package/'source_materials/input',package]:
        if (candidate/'annotations/authorization_taxonomy_1524.csv').is_file():
            public_input=candidate;break
    if public_input is None:
        taxroot=package/'01_Article投稿文件/Supplementary_Data_2'
        archive=package/'03_原返回包_只读'
    else:
        taxroot=public_input/'annotations';archive=public_input/'archive'
    source_paths={'authorization_taxonomy_1524.csv':taxroot/'authorization_taxonomy_1524.csv','field_taxonomy_9144.csv':taxroot/'field_taxonomy_9144.csv','source_manifest.csv':archive/'evidence/source_manifest.csv','taxonomy_rules_en.md':taxroot/'taxonomy_rules_en.md'}
    projection=None
    if public_input is not None:
        projection_path=public_input/'projection_manifest.json'
        projection=json.loads(projection_path.read_text(encoding='utf-8'))
        for name,path in source_paths.items():
            entry=projection['normalization_inputs'][name]
            assert path.resolve().is_relative_to(public_input.resolve())
            assert sha(path)==entry['public_sha256'] and path.stat().st_size==entry['public_bytes'],name
            assert re.fullmatch('[0-9a-f]{64}',entry['original_sha256'])
    authors=read_csv(source_paths['authorization_taxonomy_1524.csv'])
    fields=read_csv(source_paths['field_taxonomy_9144.csv'])
    sources=read_csv(source_paths['source_manifest.csv'])
    assert len(authors)==1524 and len(fields)==9144 and len(sources)==3173
    index={r['submission_number']:r for r in authors}
    assert len(index)==1524
    authout=[]
    for row in sorted(authors,key=lambda r:r['submission_number']):
        authout.append({k:row[k] for k in ['submission_number','device_name','company','regulatory_pathway','date_of_final_decision','medical_specialty']}|{'baseline_ai_function_scope':row['baseline_coding_scope'],'ai_function_scope':row['revised_coding_scope'],'baseline_clinical_function_group':row['baseline_component_status'],'clinical_function_group':row['component_status']})
    csvout(DATA/'authorizations.csv',authout)
    annotation=[];positive=[];changes=[]
    for row in sorted(fields,key=lambda r:(r['submission_number'],FIELDS.index(r['field']))):
        sid,field=row['submission_number'],row['field'];auth=index[sid]
        assert row['revised_codes']==auth[field] and row['baseline_codes']==auth['baseline_'+field]
        codes=labelset(row['revised_codes']);assert codes<=ALLOWED[field]
        assert not (codes&LIMITED and len(codes)>1)
        limited=bool(codes&LIMITED)
        assert limited==(row['source_limited']=='True')
        scope=auth['revised_coding_scope']
        layer='AI_ATTRIBUTION_BARRIER' if scope==SCOPES[1] else 'SOURCE_INSUFFICIENT' if scope==SCOPES[2] else 'FUNCTION_GROUP_UNRESOLVED' if field=='component_status' and limited else 'FIELD_NOT_STATED' if limited else 'NONE'
        aid=sid+':'+field
        state=next(iter(codes)) if limited else 'CODED'
        annotation.append({'annotation_id':aid,'submission_number':sid,'field':field,'baseline_codes':row['baseline_codes'],'codes':row['revised_codes'],'annotation_state':state,'source_limited':str(limited).lower(),'limitation_layer':layer})
        if field in CONTENT_FIELDS and not limited:
            for code in sorted(codes):positive.append({'annotation_id':aid,'submission_number':sid,'field':field,'label':code})
        if row['baseline_codes']!=row['revised_codes']:changes.append({'submission_number':sid,'field':field,'baseline_value':row['baseline_codes'],'current_value':row['revised_codes'],'change_class':'RETAINED_SOURCE_UPDATE_NOT_NEW_RECODING'})
    for row in authors:
        if row['baseline_coding_scope']!=row['revised_coding_scope']:changes.append({'submission_number':row['submission_number'],'field':'ai_function_scope','baseline_value':row['baseline_coding_scope'],'current_value':row['revised_coding_scope'],'change_class':'RETAINED_SCOPE_AMENDMENT_NOT_NEW_RECODING'})
    csvout(DATA/'field_annotations.csv',annotation)
    csvout(DATA/'positive_labels.csv',positive)
    csvout(DATA/'version_changes.csv',sorted(changes,key=lambda r:(r['submission_number'],r['field'])))
    aliases=[{'submission_number':'DEN130013','alternate_regulatory_identifier':'K124067','identity_source_url':'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?id=DEN130013','identity_source_access_date':'2026-09-07','identity_basis':'FDA De Novo database lists both identifiers for VITEK MS'}]
    csvout(DATA/'regulatory_identifier_aliases.csv',aliases)
    sourceout=[];source_lookup=defaultdict(list);source_subject_lookup=defaultdict(list)
    for row in sorted(sources,key=lambda r:int(r['source_index_row'])):
        sid=f"SRC{int(row['source_index_row']):05d}"
        item={'source_record_id':sid,'subject_submission_number':row['submission_number'],'source_url':row['source_document_url'],'source_document_type':row['source_document_type'],'document_sha256':row['document_original_sha256'],'text_sha256':row['text_actual_sha256'],'retrieval_date':row['retrieval_date'],'retrieval_status':row['retrieval_status'],'record_origin':'LEGACY_SOURCE_MANIFEST'}
        sourceout.append(item);source_lookup[canonical(item['source_url'])].append(item);source_subject_lookup[row['submission_number'],canonical(item['source_url'])].append(item)
    evidence=[];checks=[];cache={};additional={}
    for row in sorted(fields,key=lambda r:(r['submission_number'],FIELDS.index(r['field']))):
        check=mechanical_check(row,archive,cache);checks.append(check)
        sid,url=row['submission_number'],row['source_url'];key=canonical(url)
        same=source_subject_lookup.get((sid,key),[])
        global_matches=source_lookup.get(key,[])
        matches=same or global_matches
        if check['text_sha256']:
            exact=[x for x in matches if x['text_sha256']==check['text_sha256']]
            if exact:matches=exact
        if not matches:
            pair=sid,key
            if pair not in additional:
                item={'source_record_id':'ADD'+text_sha(sid+'|'+key)[:12],'subject_submission_number':sid,'source_url':url,'source_document_type':'FDA_LINKED_ADDITIONAL_REFERENCE','document_sha256':'','text_sha256':check['text_sha256'],'retrieval_date':'','retrieval_status':'NOT_RETRIEVED_IN_RESOURCE_BUILD','record_origin':'ADDITIONAL_ANNOTATION_REFERENCE'}
                additional[pair]=item;sourceout.append(item)
            matches=[additional[pair]]
        url_ids=url_authorizations(url)
        normalized_sid=sid.replace('/','').upper()
        alternate_match=any(x['submission_number']==sid and x['alternate_regulatory_identifier'] in url_ids for x in aliases)
        relation='DIRECT_SUBJECT_AUTHORIZATION_TOKEN' if normalized_sid in url_ids else 'SAME_SUBJECT_ALTERNATE_REGULATORY_IDENTIFIER' if alternate_match else 'ASSOCIATED_OTHER_AUTHORIZATION_LEGACY_LINK' if url_ids and same else 'OTHER_AUTHORIZATION_NOT_SUBJECT_LINKED_IN_LEGACY_MANIFEST' if url_ids else 'NO_AUTHORIZATION_TOKEN_IN_URL'
        item={'annotation_id':check['annotation_id'],'source_record_ids':';'.join(sorted(x['source_record_id'] for x in matches)),'recorded_source_url':url,'source_url_authorization_tokens':';'.join(url_ids),'source_authorization_relationship':relation,'subject_source_pair_in_legacy_manifest':str(bool(same)).lower(),'quote_sha256':text_sha(row['evidence_quote']),**{k:v for k,v in check.items() if k!='annotation_id'}}
        evidence.append(item)
    csvout(DATA/'source_records.csv',sourceout)
    csvout(DATA/'evidence_links.csv',evidence)
    csvout(VALIDATION/'text_locator_checks.csv',checks)
    exceptions=[r for r in evidence if r['locator_check_status']!='EXACT_RECORDED_SPAN_MATCH' or r['source_authorization_relationship'] not in ['DIRECT_SUBJECT_AUTHORIZATION_TOKEN','SAME_SUBJECT_ALTERNATE_REGULATORY_IDENTIFIER']]
    csvout(VALIDATION/'locator_and_source_exceptions.csv',exceptions)
    input_records=[{'file_name':n,'sha256':sha(p),'bytes':p.stat().st_size} for n,p in source_paths.items()]
    provenance={'source_release':'CAP_Article_three_figure_reviewed_release_2026-09-07','inputs':input_records,'semantic_labels_modified':False,'long_quotations_redistributed':False,'source_caches_redistributed':False,'license_status':'AUTHOR_PERMISSION_AND_REPOSITORY_DEPOSIT_PENDING'}
    if projection is not None:
        for entry in input_records:
            origin=projection['normalization_inputs'][entry['file_name']]
            entry.update(original_file_sha256=origin['original_sha256'],original_file_bytes=origin['original_bytes'],public_projection_transformation=origin['transformation'])
        provenance.update(reconstruction_input_mode='PUBLIC_SCIENTIFIC_SOURCE_MATERIALS',public_projection_manifest_sha256=sha(projection_path),source_caches_redistributed=True,long_quotations_redistributed=True,license_status='AUTHOR_CREATED_DATA_CC_BY_4_0_CODE_MIT_THIRD_PARTY_SOURCE_RIGHTS_RETAINED')
    jsonout(VALIDATION/'input_provenance.json',provenance)
    (ROOT/'docs').mkdir(exist_ok=True)
    # Keep the release's adapted six-field codebook; retain the original input separately.
    if not (ROOT/'docs/retained_taxonomy_rules_en.md').exists():
        shutil.copy2(source_paths['taxonomy_rules_en.md'],ROOT/'docs/retained_taxonomy_rules_en.md')
    vocab=[]
    for field in FIELDS:
        for code in sorted(ALLOWED[field]):vocab.append({'field':field,'code':code,'class':'LIMITATION_STATE' if code in LIMITED else 'FUNCTION_GROUP_STATE' if field=='component_status' else 'POSITIVE_CONTENT_LABEL','multiple_values_allowed':str(field!='component_status').lower()})
    csvout(DATA/'vocabulary.csv',vocab)
    print({'authorizations':len(authout),'field_annotations':len(annotation),'positive_labels':len(positive),'evidence_links':len(evidence),'legacy_source_records':len(sources),'additional_source_records':len(additional),'locator_status':dict(Counter(r['locator_check_status'] for r in checks))})

if __name__=='__main__':main()
