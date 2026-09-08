"""Shared schema and deterministic helpers for the resource release."""
import csv, hashlib, json, re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
VALIDATION=ROOT/'validation'
FIELDS=['input','output','user','setting','action','component_status']
CONTENT_FIELDS=FIELDS[:-1]
LIMITED={'NOT_STATED','NOT_ASSESSABLE','UNCERTAIN'}
SCOPES=['DESCRIBED_AI_OR_ALGORITHMIC_FUNCTION','DEVICE_FUNCTION_AI_ATTRIBUTION_UNRESOLVED','SOURCE_INSUFFICIENT']
POSITIVE={
 'input':{'MEDICAL_IMAGE','PHYSIOLOGICAL_SIGNAL','LAB_SPECIMEN_OR_OMICS','CLINICAL_TABULAR_OR_TEXT','AUDIO_OR_VIDEO','DEVICE_TELEMETRY_OR_OPERATIONAL','MULTIMODAL','OTHER'},
 'output':{'DETECTION_OR_ALERT','CLASSIFICATION_OR_DIAGNOSIS','SEGMENTATION_OR_LOCALIZATION','MEASUREMENT_OR_QUANTIFICATION','RISK_SCORE_OR_PREDICTION','RECONSTRUCTION_OR_ENHANCEMENT','RECOMMENDATION_OR_PLANNING','CONTROL_OR_AUTOMATION','DOCUMENTATION_OR_SUMMARY','OTHER'},
 'user':{'RADIOLOGIST','OTHER_PHYSICIAN','OTHER_CLINICIAN','LABORATORY_PROFESSIONAL','TECHNOLOGIST_OR_OPERATOR','PATIENT_OR_CAREGIVER','OTHER'},
 'setting':{'SCREENING','DIAGNOSTIC_INTERPRETATION','ACUTE_TRIAGE_OR_EMERGENCY','PROCEDURAL_OR_OPERATING_ROOM','INPATIENT','OUTPATIENT','LABORATORY','MONITORING','HOME_OR_CONSUMER','OTHER'},
 'action':{'INTERPRETATION_OR_DIAGNOSIS','TRIAGE_OR_PRIORITIZATION','MONITORING_OR_FOLLOW_UP','REFERRAL_OR_ESCALATION','TREATMENT_OR_PROCEDURE_PLANNING','THERAPY_DOSE_OR_DEVICE_CONTROL','WORKFLOW_OR_DOCUMENTATION','PATIENT_SELF_MANAGEMENT','OTHER'},
 'component_status':{'SINGLE','MULTIPLE'},
}
ALLOWED={f:values|({'UNCERTAIN'} if f=='component_status' else {'NOT_STATED','NOT_ASSESSABLE'}) for f,values in POSITIVE.items()}

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))

def csvout(path,rows,fields=None):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields or list(rows[0]));writer.writeheader();writer.writerows(rows)

def jsonout(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def text_sha(value):return hashlib.sha256(value.encode('utf-8')).hexdigest()
def normalize(value):return re.sub(r'\s+',' ',value).strip()
def labelset(value):return set(value.split(';'))
def canonical(url):
    parsed=urlsplit(url)
    return urlunsplit(('https',parsed.netloc.lower(),parsed.path,parsed.query,''))

def url_authorizations(url):
    return sorted(set(re.findall(r'(?:K\d{6}|DEN\d{6}|P\d{6}(?:S\d{3})?)',url.upper())))

def pages_from_text(text):
    markers=list(re.finditer(r'^===== PAGE (\d+) OF \d+ =====\s*$',text,re.M))
    if not markers:return {0:normalize(text)}
    return {int(m.group(1)):normalize(text[m.end():markers[i+1].start() if i+1<len(markers) else len(text)]) for i,m in enumerate(markers)}

def checksum_release():
    # Include data, documentation and code; exclude generated manifest itself.
    entries=[]
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.name=='checksums.sha256':continue
        rel=path.relative_to(ROOT)
        if any(part in {'.git','.source_archives'} for part in rel.parts):continue
        if rel.parts[:2] in {('source_materials','input'),('source_materials','original_documents')}:continue
        if path.suffix=='.pyc':continue
        entries.append(f'{sha(path)}  {path.relative_to(ROOT).as_posix()}')
    (ROOT/'checksums.sha256').write_text('\n'.join(entries)+'\n',encoding='utf-8')
