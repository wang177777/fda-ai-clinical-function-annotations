#!/usr/bin/env python3
"""Small offline queries illustrating safe joins and nonexclusive label counts.

For source-linked CSV exports including later semantic reviews, use
export_reuse_subset.py; worked examples are in docs/reuse_examples.md.
"""
import json
from collections import Counter
from resource_common import *

def main():
    authors=read_csv(DATA/'authorizations.csv')
    labels=read_csv(DATA/'positive_labels.csv')
    fields=read_csv(DATA/'field_annotations.csv')
    subject='K182513'
    result={
      'authorization_count':len(authors),
      'function_groups':dict(Counter(r['clinical_function_group'] for r in authors)),
      'medical_image_authorizations':len({r['submission_number'] for r in labels if r['field']=='input' and r['label']=='MEDICAL_IMAGE'}),
      'field_limitations_not_blank_cells':dict(Counter(r['limitation_layer'] for r in fields if r['source_limited']=='true')),
      'example_subject':subject,
      'example_subject_fields':{r['field']:r['codes'] for r in fields if r['submission_number']==subject},
      'safe_usage_note':'Do not sum nonexclusive label frequencies as device counts; do not equate output-label count with clinical function or internal model count.'
    }
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
