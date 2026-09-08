#!/usr/bin/env python3
"""Project existing OTHER notes and separately documented English translations.

Author-side inputs are needed to rebuild notes, not to use or validate them.
This step preserves current codes and does not assign meanings to ambiguous
multi-label contexts.
"""
import argparse, csv, hashlib, json, re
from collections import Counter
from pathlib import Path
from resource_common import ROOT, DATA, VALIDATION, read_csv, csvout, jsonout, sha

SOURCE_SHA='89154f7f437bca8cdeffc5782db7209afb2d8fa7cc79b98cb29c9137e8840ac8'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-file',type=Path,required=True)
    parser.add_argument('--retained-fields',type=Path,required=True)
    parser.add_argument('--translations-file',type=Path,required=True)
    args=parser.parse_args()
    assert sha(args.retained_fields)==SOURCE_SHA
    audit=json.loads(args.audit_file.read_text())['other_explanations']
    assert audit['retained_source_sha256']==SOURCE_SHA
    original=read_csv(args.retained_fields)
    current={r['annotation_id']:r for r in read_csv(DATA/'field_annotations.csv')}
    translated=json.loads(args.translations_file.read_text())
    translations=translated['translations'] if isinstance(translated,dict) else translated
    tmap={r['annotation_id']:r for r in translations}
    assert len(tmap)==len(translations)==78
    rows=[]
    for item in sorted(audit['records'],key=lambda r:r['annotation_id']):
        key=item['annotation_id'];record_no=item['retained_record_number_1_based_excluding_header']
        old=original[record_no-1];now=current[key]
        assert old['submission_number']+':'+old['field']==key
        assert item['current_codes']==now['codes']==item['retained_codes']
        assert 'OTHER' in now['codes'].split(';')
        note=item['other_explanation_original'];status=item['other_attribution_status']
        if note:
            assert note in old['decision_reason'],key
            if re.search('[\u4e00-\u9fff]',note):
                tr=tmap[key];assert tr['original']==note
                english=tr['translation_en'];language='zh';processing='AI_ASSISTED_ENGLISH_TRANSLATION'
            else:english=note;language='en_or_latin';processing='RETAINED_ENGLISH_OR_LATIN_TEXT'
            assert english and not re.search('[\u4e00-\u9fff]','|'.join([english]))
            digest=hashlib.sha256(note.encode()).hexdigest()
        else:
            assert status=='MULTILABEL_OTHER_ATTRIBUTION_NOT_ISOLATED'
            english=language=digest='';processing='NO_OTHER_SPECIFIC_NOTE_ADDED'
        assert '/Users/' not in english and 'evidence/texts/' not in english
        rows.append({'annotation_id':key,'field':now['field'],'codes':now['codes'],'other_note_en':english,'other_note_status':status,'note_original_language':language,'note_processing':processing,'note_original_sha256':digest,'retained_field_record_number':record_no,'retained_input_sha256':SOURCE_SHA,'retained_source_column':'decision_reason'})
    assert len(rows)==789 and sum(bool(r['other_note_en']) for r in rows)==206
    assert set(tmap)=={r['annotation_id'] for r in rows if r['note_original_language']=='zh'}
    csvout(DATA/'other_label_notes.csv',rows)
    jsonout(VALIDATION/'other_notes_provenance.json',{'release_version':'1.2','prepared_date':'2026-09-08','retained_input_sha256':SOURCE_SHA,'retained_input_rows':9144,'input_hash_verified':True,'explicit_fragments_verified_in_original_reasons':206,'current_OTHER_memberships':789,'nonempty_specific_notes':206,'ambiguous_multilabel_specific_notes_left_blank':583,'status_counts':dict(Counter(r['other_note_status'] for r in rows)),'language_processing':dict(Counter(r['note_processing'] for r in rows)),'label_changes':0,'description':'Retained single-OTHER field reasons and explicit OTHER fragments only. Codex assisted with English translation of 78 existing Chinese notes; no separate expert validation of the new English wording is claimed. No meanings are inferred for the 583 unseparated multilabel contexts.','translation_input_sha256':sha(args.translations_file)})
    print(json.dumps({'rows':len(rows),'nonempty_notes':206,'unchanged_codes':True}))

if __name__=='__main__':main()
