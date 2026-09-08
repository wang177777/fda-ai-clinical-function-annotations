"""Validate the version 1.2 cohort and retained-OTHER documentation layers."""
from collections import Counter
import re
from resource_common import ROOT, DATA, VALIDATION, read_csv, sha
from check_cohort_snapshot import check_snapshot
import json

def validate_extensions(authorizations, annotations):
    release=json.loads((VALIDATION/'release_1_2_provenance.json').read_text())
    assert release['release_version']=='1.2' and release['label_changes']==release['cohort_changes']==0
    preserved=release['preserved_v1_1_data_file_sha256']
    assert len(preserved)==12
    for name,digest in preserved.items():
        assert name in {p.name for p in DATA.glob('*.csv')}
        assert sha(DATA/name)==digest,f'Version 1.1 data table changed: {name}'
    snapshot=check_snapshot(repository=ROOT)
    recorded=json.loads((VALIDATION/'cohort_snapshot_check.json').read_text())
    assert recorded['status']=='PASS' and recorded['matching_current_authorization_keys']==1524
    for name,digest in recorded['public_input_sha256'].items():assert sha(DATA/name)==digest
    notes=read_csv(DATA/'other_label_notes.csv');by_id={r['annotation_id']:r for r in notes}
    expected={k for k,r in annotations.items() if 'OTHER' in r['codes'].split(';')}
    assert len(notes)==len(by_id)==len(expected)==789 and set(by_id)==expected
    counts=Counter();processing=Counter()
    input_sha='89154f7f437bca8cdeffc5782db7209afb2d8fa7cc79b98cb29c9137e8840ac8'
    for key,r in by_id.items():
        field=annotations[key]
        assert r['field']==field['field'] and r['codes']==field['codes']
        assert r['retained_input_sha256']==input_sha and r['retained_source_column']=='decision_reason'
        assert 1<=int(r['retained_field_record_number'])<=9144
        status=r['other_note_status'];counts[status]+=1;processing[r['note_processing']]+=1
        if status=='MULTILABEL_OTHER_ATTRIBUTION_NOT_ISOLATED':
            assert len(field['codes'].split(';'))>1
            assert not r['other_note_en'] and not r['note_original_language'] and not r['note_original_sha256']
            assert r['note_processing']=='NO_OTHER_SPECIFIC_NOTE_ADDED'
        else:
            assert r['other_note_en'] and not re.search('[\u4e00-\u9fff]',r['other_note_en'])
            assert re.fullmatch('[a-f0-9]{64}',r['note_original_sha256'])
            if status=='SINGLE_OTHER_EXISTING_FIELD_REASON':assert field['codes']=='OTHER'
            else:assert status=='EXPLICIT_OTHER_ASSIGNMENT_IN_RETAINED_REASON' and len(field['codes'].split(';'))>1
            assert (r['note_original_language'],r['note_processing']) in {('en_or_latin','RETAINED_ENGLISH_OR_LATIN_TEXT'),('zh','AI_ASSISTED_ENGLISH_TRANSLATION')}
        assert '/Users/' not in '|'.join(r.values()) and 'evidence/texts/' not in r['other_note_en']
    assert counts=={'SINGLE_OTHER_EXISTING_FIELD_REASON':198,'EXPLICIT_OTHER_ASSIGNMENT_IN_RETAINED_REASON':8,'MULTILABEL_OTHER_ATTRIBUTION_NOT_ISOLATED':583}
    assert processing=={'RETAINED_ENGLISH_OR_LATIN_TEXT':128,'AI_ASSISTED_ENGLISH_TRANSLATION':78,'NO_OTHER_SPECIFIC_NOTE_ADDED':583}
    provenance=json.loads((VALIDATION/'other_notes_provenance.json').read_text())
    assert provenance['label_changes']==0 and provenance['explicit_fragments_verified_in_original_reasons']==206
    assert provenance['retained_input_sha256']==input_sha
    return {'cohort_snapshot_membership':snapshot['public_membership_rows'],'cohort_snapshot_manifest':snapshot['artifact_manifest_rows'],'other_label_notes':len(notes),'other_notes_populated':206,'other_notes_unseparated_multilabel':583,'other_note_status_counts':dict(counts),'other_note_processing_counts':dict(processing),'cohort_mapping_check':'PASS'}
