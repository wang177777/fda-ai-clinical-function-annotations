# Reusing current labels with both evidence layers

`scripts/export_reuse_subset.py` exports one row per selected authorization, with the complete current input and output label sets. It uses Python 3.10 or later and the standard library. Run the resource validator before using an export. The script checks input/output membership consistency and joining keys but does not replace the full validator.

From the repository directory:

```sh
python3 scripts/validate_resource.py
python3 scripts/export_reuse_subset.py --output ../reuse_exports/medical_image.csv
python3 scripts/export_reuse_subset.py --output-code SEGMENTATION_OR_LOCALIZATION --output ../reuse_exports/image_segmentation.csv
python3 scripts/export_reuse_subset.py --input-code CLINICAL_TABULAR_OR_TEXT --output-code RECOMMENDATION_OR_PLANNING --output ../reuse_exports/tabular_planning.csv
python3 scripts/export_reuse_subset.py --strict-current-scope --output ../reuse_exports/medical_image_strict.csv
```

The destination must be outside this repository. Each command writes a CSV, a `.summary.json` with counts and source-table fingerprints, and an `.excluded.csv` with recorded exclusion reasons. The exclusion file has only its header when no records are excluded. Repeating the same command on unchanged tables produces the same output bytes.

## Selection and row unit

`--input-code` selects a positive input code and defaults to `MEDICAL_IMAGE`; `--input-code ANY` selects any input in the `CODED` state. `--output-code` optionally requires one positive output code. Code arguments are case-insensitive and checked against the vocabulary. Supplying a limitation code such as `NOT_ASSESSABLE` is an error. The selection uses current codes and positive memberships, so historical device-level labels do not re-enter through `baseline_codes` or review notes.

An omitted output filter preserves the current output field, including its state. The script never expands a multi-label set into multiple authorization rows. Input/output coexistence at the authorization level does not establish a particular input-output pair for an internal component. For example, a selected segmentation output can coexist with another output produced by a different clinical function.

## Evidence in each row

`input_evidence_json` and `output_evidence_json` each contain:

- `original_evidence`: the preserved source/locator record, including its original mechanical-check outcome.
- `original_and_bridge_source_records`: source-capture records referenced by that original record or its bridges.
- `source_bridges` and `focused_source_relationship`: the corresponding field-specific source relationship and scope notes. `NO_FOCUSED_RECORD` identifies the absence of such a record.
- `semantic_reviews`: later field reviews, retaining pre/post codes, reasons, review status and the separate `new_locator_check_status`. Each review contains its `review_sources`, including URLs, physical pages, material/access notes and any linked original capture records.

The semantic join is `annotation_id` → `semantic_review_records.review_source_ids` → `semantic_review_sources.review_source_id`. Semicolon-separated source keys are split before joining. Only field-cited references are attached: the context-only S06 reference is not attached to unrelated rows. The full tables remain available for reviews of grouping or other fields beyond this input/output export.

For **K182034**, the output set includes `MEASUREMENT_OR_QUANTIFICATION;SEGMENTATION_OR_LOCALIZATION`. Its old machine locator remains on physical page 5. Its later review supplies physical page 7, Table 5.1, and the FDA PDF URL for the added segmentation/localization code. The export retains both layers; it does not turn the page-7 reference into a verified character span or treat the page-5 match as validation of the added label.

## Recorded current-scope restrictions

`--strict-current-scope` requires scope `DESCRIBED_AI_OR_ALGORITHMIC_FUNCTION` and `CODED` states for both input and output. It additionally excludes a candidate when **either its input field or its output field** has a focused relationship with one of these exact values:

| Column | Excluded value |
| --- | --- |
| `source_relationship` | `GENERAL_SOFTWARE_CONTINUITY_FEATURE_NOT_RESTATED` |
| `source_relationship` | `GENERAL_FIRMWARE_CONTINUITY_FEATURE_NOT_RESTATED` |
| `source_relationship` | `GENERAL_PERFORMANCE_CONTINUITY_FEATURE_NOT_RESTATED` |
| `source_relationship` | `EXPLICIT_INTEGRATION_OUTSIDE_CURRENT_SUBMISSION_SCOPE` |
| `source_caution_codes` | `FEATURE_NOT_NAMED_IN_CURRENT_SUMMARY` |
| `source_caution_codes` | `AI_FEATURE_EXPLICITLY_OUTSIDE_CURRENT_SUBMISSION_SCOPE` |

Caution matching uses complete semicolon-separated codes. The broad export retains these records and exposes the same flags. Grouping, user, setting and action flags are not substituted for input/output flags. Other cautions are preserved in the JSON without becoming additional exclusion rules. A cross-authorization source, by itself, is not excluded; an explicitly documented continuity relationship and its bridge remain available for review. For example, K210645 is retained, and a grouping-only caution on K250877 does not exclude its input/output row.

“Current” refers to the scope encoded in this release, not to a new source search or new expert assessment. Passing the filter, or having no focused relationship record, does not establish semantic accuracy, an exhaustive inventory or independently verified attribution. The filter does not create a code-level gold standard.

## Results for version 1.3.0

These counts were reproduced on September 8, 2026 and remain unchanged in version 1.3.0. The input label and evidence tables are byte-identical to version 1.1. These are retrieval examples, not new clinical validation results. Join `data/other_label_notes.csv` by `annotation_id` for the additional retained OTHER descriptions and their processing states.

| Input selection | Output selection | Recorded scope filter | Exported authorizations | Output positive-code memberships |
| --- | --- | --- | ---: | ---: |
| `MEDICAL_IMAGE` | Any current output | Off | 1,154 | 2,474 |
| `MEDICAL_IMAGE` | Any current output | On | 1,149 | 2,468 |
| `MEDICAL_IMAGE` | `SEGMENTATION_OR_LOCALIZATION` | Off | 653 | 1,738 |
| `CLINICAL_TABULAR_OR_TEXT` | `RECOMMENDATION_OR_PLANNING` | Off | 12 | 31 |

Output-membership counts include the full output label sets, not only the selected output code, and must not be summed or interpreted as independent devices. The strict image export excludes K213603, K251901, K252371, K253625 and K260746, with ten triggering input/output field records. Both image exports and the segmentation export retain the two input/output semantic reviews for K182034 and their single cited review reference.

K190013 has `NOT_ASSESSABLE` in its current input and output fields. Its earlier tabular-input and planning-output labels remain visible in the full historical records; it is absent from the positive tabular/planning selection. No clinical recoding or new agreement estimate is produced by these examples.
