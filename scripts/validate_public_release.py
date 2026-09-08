"""Check public source manifests, release inputs and preserved data versions."""
import json
from resource_common import ROOT, DATA, VALIDATION, read_csv, sha

def validate_public_release():
    release=json.loads((VALIDATION/'release_1_3_provenance.json').read_text())
    assert release['release_version']=='1.3.0' and release['annotation_changes']==0
    preserved=release['preserved_v1_2_data_file_sha256']
    assert len(preserved)==14
    for name,digest in preserved.items(): assert sha(DATA/name)==digest,name
    reconstruction=json.loads((VALIDATION/'public_reconstruction_check.json').read_text())
    assert reconstruction['status']=='PASS' and reconstruction['data_tables_rebuilt']==15
    for name,values in reconstruction['tables'].items():
        assert sha(DATA/name)==values['released_sha256']==values['rebuilt_sha256'],name
    source=ROOT/'source_materials'
    documents=json.loads((source/'original_document_manifest.json').read_text())
    inputs=json.loads((source/'input_manifest.json').read_text())
    archives=json.loads((source/'archives.json').read_text())['archives']
    assert len(archives)==6 and sum(a['group']=='inputs' for a in archives)==1
    assert len(documents['files'])==3109 and len(inputs['files'])==3166
    assert len({r['path'] for r in documents['files']})==3109
    recorded=read_csv(DATA/'source_records.csv')
    assert {r['document_sha256'] for r in recorded if r['document_sha256']}=={r['sha256'] for r in documents['files']}
    assert documents['format_counts']=={'PDF':1584,'HTML':1524,'retained_error_response':1}
    assert sum(a['files'] for a in archives if a['group']=='documents')==3109
    assert sum(a['files'] for a in archives if a['group']=='inputs')==3166
    assert (ROOT/'licenses/CC-BY-4.0.txt').is_file() and (ROOT/'licenses/MIT.txt').is_file()
    return {'source_document_files':3109,'scientific_input_files':3166,'source_archives':6,'all_recorded_document_hashes_accounted_for':True,'all_15_tables_reconstructed_byte_identically':True,'preserved_v1_2_data_tables':14}
