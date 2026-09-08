# Clinical-function annotations for 1524 US artificial intelligence medical-device authorizations

Version **1.3.0**, September 8, 2026. [Repository](https://github.com/wang177777/fda-ai-clinical-function-annotations) · [Versioned release](https://github.com/wang177777/fda-ai-clinical-function-annotations/releases/tag/v1.3.0). Cite the resource using [CITATION.cff](CITATION.cff). Author-created data and documentation use CC BY 4.0; code uses MIT. See [LICENSE.md](LICENSE.md) for the scope of these grants and attribution of source materials.

## Scope and files

The cohort comprises 1,524 submission-level authorizations in the FDA AI-enabled-device list snapshot accessed June 29, 2026; the retained source-capture log is dated June 30. The six annotation fields describe input, output, intended user, setting or use context, downstream action, and clinical-function grouping. Version 1.3.0 publishes the source materials and reconstruction inputs alongside the 15 linked data tables. Annotation labels and evidence values are unchanged from version 1.2; the cohort manifest now records public distribution of its three originals. Earlier assembly stages are documented in [release notes](docs/release_notes.md).

| File | Rows and purpose |
| --- | --- |
| `data/authorizations.csv` | 1,524 authorization records with metadata, baseline/current scope and clinical-function grouping |
| `data/field_annotations.csv` | 9,144 authorization-field records with historical baseline/current labels and limitation layers |
| `data/positive_labels.csv` | 11,120 nonexclusive positive-label memberships from the first five fields |
| `data/evidence_links.csv` | 9,144 preserved source/locator records with quotation hashes |
| `data/source_records.csv` | 3,173 retained source-capture records, not necessarily unique documents |
| `data/version_changes.csv` | 16 amended cells across four authorizations: eight retained source amendments and eight confirmed amendments |
| `data/semantic_review_records.csv` | 12 targeted field reviews with pre/post values, English reasons and page references |
| `data/semantic_review_sources.csv` | Six review references: five field-cited and one context-only |
| `data/regulatory_identifier_aliases.csv` | One FDA-confirmed DEN130013/K124067 identity link |
| `data/source_bridges.csv` | 145 preserved field-linked bridge anchors representing 43 distinct text locations |
| `data/associated_source_relationships.csv` | 65 field-level source relationships and scope restrictions |
| `data/vocabulary.csv` | Allowed field/code combinations and their types |
| `data/cohort_snapshot_membership.csv` | 1,524 original FDA-list record positions with primary product codes |
| `data/cohort_snapshot_manifest.csv` | Three original-artifact fingerprints, historical access metadata and distribution status |
| `data/other_label_notes.csv` | 789 OTHER memberships: 206 specific notes and 583 unseparated multilabel contexts |
| `docs/data_dictionary.csv` | All 139 columns across the 15 data tables, types, joining rules and blank-cell counts |
| `docs/retained_taxonomy_rules_en.md` | Operational definitions and category boundaries |
| `validation/summary.json` | Recomputed resource, review and technical-validation counts |
| `validation/text_locator_checks.csv` | Every recorded/verified locator and original mechanical-check outcome |
| `validation/locator_and_source_exceptions.csv` | Non-original-span or non-direct-subject anchors |
| `validation/input_provenance.json` | Fingerprints of inputs to the initial normalization stage |
| `validation/semantic_review_provenance.json` | Confirmation-input fingerprints, reported review scope and version reconciliation |
| `validation/validation_report.json` | Scope and outcome of standalone checks |

Join authorizations and fields on `submission_number`; join fields, label memberships, evidence and semantic reviews on `annotation_id`. Split `source_record_ids`, `review_source_ids` and `existing_source_record_ids` on semicolons before joining referenced keys. Source-capture records may be shared across fields or authorizations. The six review references form a separate register and do not replace or increase the 3,173-row capture manifest.

## Cohort mapping and retained OTHER notes

The original June 29 CSV and XLSX both contain the same 1,524 submissions and six-column metadata in the same order. The public mapping records the original CSV record position and primary product code; the three-row manifest records original file fingerprints and source URLs. The full original-CSV check matched all six columns, after date normalization and trimming two company names. The three originals are distributed under `source_materials/input/cohort` in the input archive. See [cohort documentation](docs/cohort_snapshot.md) and `validation/cohort_snapshot_check.json`; the default checker validates mapping structure, while the original-file command repeats the six-column comparison.

The exact OTHER code occurs in 789 field records. Existing reasons support 206 specific notes (198 single-OTHER reasons and eight explicit multilabel fragments). The other 583 receive a blank note and an explicit unseparated-attribution status. Of the populated notes, 128 retain English/Latin text and 78 are AI-assisted English translations of Chinese originals. No categories or field codes change. `docs/other_label_notes.md` defines the note statuses and retained provenance.

## Confirmation and version history

For the confirmation recorded as September 8, 2026, the authors reported that Xiaonan Yang and Weixin Wang confirmed the supplied draft record by record across 1,524 authorizations and 9,144 field positions. Review covered labels, assessment states, function attribution, rationales and source locators. The reported procedure specified discussion between the two reviewers; unresolved disagreements were to be referred to Zuoliang Qi. The record describes draft confirmation and discussion; it does not contain paired independent ratings for estimating inter-rater agreement or a count of disagreements adjudicated by Qi.

The supplied draft matches the historical baseline. The current release already contained eight source-amended cells involving K182513 and K233662; those amendments remain separately versioned. New confirmed decisions add `SEGMENTATION_OR_LOCALIZATION` to K182034 output and assign unresolved function attribution to K190013, propagating `NOT_ASSESSABLE` to its first five fields and `UNCERTAIN` to grouping. These comprise seven field amendments and one scope amendment. The older supplied draft does not overwrite the source-updated release.

All 12 targeted fields have public review notes, including five confirmed without code changes. New review notes use physical pages and table references, with no new exact character-span claim. The additional K182034 segmentation/localization label cites page 7; the old page-5 output anchor remains in the original mechanical layer.

The September 8 confirmation supplied three retained text caches matching existing SHA-256 values, with page-level references for the review. The six-row review register retains the historical capture fields; any later release-stage downloads are identified separately in the source-material manifest. K162532 and K162225 are related-version references absent from the original capture manifest. Access notes retain the reported page-10 image-capture failure for K190013 and page-8 failure for K162532; those references use readable text. S06 is context-only and is not assigned to any of the 12 fields.

## Validate and retrieve source materials

Python 3.10 or later, standard library only, is sufficient. From the repository directory:

```sh
python3 scripts/validate_resource.py
python3 scripts/example_usage.py
python3 scripts/check_cohort_snapshot.py
python3 scripts/export_reuse_subset.py --input-code MEDICAL_IMAGE --output ../reuse_exports/medical_image.csv
```

The validator checks checksums, keys, vocabulary, label expansion, scope propagation, version amendments, dictionary coverage, source/review joins, cohort mapping, OTHER-note provenance fields and preserved evidence bytes. It regenerates `summary.json` and `validation_report.json`; a normal successful rerun produces the same bytes. These checks establish structural consistency and mechanical evidence accounting; they do not estimate clinical accuracy.

The tables and routine validator are usable directly from the repository. Download the versioned source archives when rebuilding the data or inspecting source evidence:

```sh
python3 scripts/download_sources.py --group inputs
python3 scripts/download_sources.py --group documents
```

`--group inputs` retrieves the cohort originals, annotation ledgers, scientific confirmation inputs, source manifest, bridge review, OTHER-note inputs and retained text cache. `--group documents` retrieves the retained source-document archives. Use `--group all` to retrieve both groups. The downloader verifies the release assets and extracts their portable paths; [source-material documentation](docs/source_materials.md) describes the manifests, original attribution and later captures.

After downloading `inputs`, reconstruct all 15 tables in the following order from the repository directory:

```sh
python3 scripts/build_resource.py --source-package source_materials
python3 scripts/append_source_bridges.py --review-file source_materials/input/cross_authorization_review.csv
python3 scripts/apply_confirmed_amendments.py --public-review-input source_materials/input/public_review_input.json
python3 scripts/build_other_notes.py --audit-file source_materials/input/other_notes/other_explanations.json --retained-fields source_materials/input/annotations/field_taxonomy_9144.csv --translations-file source_materials/input/other_notes/translations.json
python3 scripts/build_cohort_mapping.py --snapshot-csv source_materials/input/cohort/fda_ai_enabled_devices_2026-06-29.csv --snapshot-xlsx source_materials/input/cohort/fda_ai_enabled_devices_2026-06-29.xlsx --metadata-txt source_materials/input/cohort/source_metadata_2026-06-29.txt
python3 scripts/check_cohort_snapshot.py --snapshot-csv source_materials/input/cohort/fda_ai_enabled_devices_2026-06-29.csv --output validation/cohort_snapshot_check.json
python3 scripts/write_dictionary.py
python3 scripts/validate_resource.py --refresh-checksums
python3 scripts/validate_resource.py
```

The first stages normalize the retained ledgers, join source bridges and apply the eight confirmed amendments while preserving the eight earlier amendments. Public scientific confirmation inputs contain the review records and source references needed for reconstruction. The cohort builder verifies all three original fingerprints and every original CSV metadata cell before writing. The OTHER-note builder projects existing reasons and the retained translation ledger. Two isolated rebuilds reproduced all 15 data tables byte for byte.

`source_materials/input/projection_manifest.json` distinguishes hashes of original files from hashes of public scientific projections. Portable paths replace local source paths, while annotation values and evidence coordinates retain their original content. The initial builder also accepts the historical source-package layout. The published `docs/retained_taxonomy_rules_en.md` adapts the codebook to this six-field resource and is preserved during rebuild; the original codebook remains fingerprinted in `source_materials/input/annotations/taxonomy_rules_en.md`.

Run reconstruction on a working copy when preserving a frozen release. Checksum refresh is the final step of an intentional rebuild, after confirming the outputs; it should not be used to suppress an unexplained mismatch.

## Original evidence-location audit

The preserved audit includes 8,967 exact recorded spans, 26 same-page span corrections and 22 corrected page/span matches. The resulting 9,015 anchors comprise 8,939 PDF-text extracts, 42 FDA HTML extracts, 16 stored image transcriptions and 18 stored web excerpts. Two quotations occurred on multiple pages without automatic correction; 121 image-excerpt references were not visually rechecked during assembly; six fields have page references without machine-text anchors.

The retained cache contains 3,121 text artifacts. The cache recheck found all 1,518 required text hashes and reproduced 9,015 field spans plus 145 bridge spans. Its 129 fields without verified spans remained outside the check. A transcription match locates a string within a transcription; it does not authenticate the original image or support every attached semantic label.

```sh
python3 scripts/recheck_text_locators.py
```

The default cache is `source_materials/input/archive`, installed with `download_sources.py --group inputs`; `--source-cache DIRECTORY` selects another cache. Artifacts are indexed by SHA-256. Normalization uses `re.sub(r"\s+", " ", text).strip()` without case folding or fuzzy matching. Character intervals count Unicode code points and are zero-based and half-open. PDF pages are physical and one-based; HTML logical marker 0 is not a PDF page. Different future extraction methods may produce different offsets for visibly similar documents.

## Source relationships and reuse

`docs/reuse_examples.md` provides executable authorization-level queries and explicit denominators. The exporter carries original evidence and later semantic-review references together, including the page-7 K182034 amendment. The MEDICAL_IMAGE query returns 1,154 authorizations, or 1,149 with its defined input/output current-scope filter; adding SEGMENTATION_OR_LOCALIZATION returns 653. Query exports are written outside the repository so the frozen payload remains unchanged. Join `other_label_notes.csv` separately by annotation identifier when interpreting OTHER categories.

The 65 associated-source field records cover 21 subject/source pairs in 20 authorizations. Their 145 bridge rows preserve subject or intermediate-source passages alongside associated-source detail. Bridges may describe carryover, configuration changes or integrated features outside the current submission scope. Users can filter these restrictions through `associated_source_relationships.csv`. The semantic amendments do not remove those warnings or change the FDA-linked DEN130013/K124067 alias.

`NOT_STATED` records field-specific information not stated in reviewed material; `NOT_ASSESSABLE` records an attribution/source barrier; `UNCERTAIN` applies to grouping. `OTHER` is a positive content code. Of 772 limited field cells, 618 arise from the same 103 authorizations with an upstream barrier. The remaining 154 occur in 138 authorizations within the described-function scope.

SINGLE and MULTIPLE describe clinical-function grouping. The first five fields allow nonexclusive labels: 670 SINGLE records have at least two output labels, while 14 MULTIPLE records have one. Label-set breadth does not enumerate internal models or establish component-level input-output-action pairs. Authorization records may also share products and documents and are not automatically statistically independent observations.

## Assistance and redistribution

Codex (OpenAI) assisted with source organization, draft taxonomy work, code, normalization, technical checks, the English public review projection, translation of 78 retained Chinese OTHER notes and manuscript preparation. Author-reported draft confirmation and targeted amendments are documented above; independent semantic accuracy, AI coding accuracy and inter-rater reliability are not estimated.

The source archives distribute retained FDA captures, source extracts, annotation evidence and reconstruction inputs with original attribution. Third-party submissions and source quotations retain their underlying rights. CC BY 4.0 applies to the authors' data and documentation, and MIT to their code; see [LICENSE.md](LICENSE.md) and [source-material documentation](docs/source_materials.md).

## Manuscript and figures

The versioned Data Descriptor, three editable tables, and both figures are in [manuscript/](manuscript/). [Figure-generation code](figure_generation/README.md) reproduces the diagrams from the released tables. Use `python3 scripts/rebuild_data.py` to reconstruct all 15 CSV tables in a temporary directory and compare their bytes with this version.
