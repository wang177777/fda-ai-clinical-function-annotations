# Release notes

## Version 1.3.0 — September 8, 2026

The public release is identified by [v1.3.0](https://github.com/wang177777/fda-ai-clinical-function-annotations/releases/tag/v1.3.0). Author-created data and documentation are licensed under CC BY 4.0 and code under MIT. Source materials retain their original attribution and underlying rights, as described in `LICENSE.md`.

The release adds source-material archives containing historical cohort originals, retained FDA captures, 3,121 text artifacts and scientific reconstruction inputs. Portable source manifests link original files to the preserved capture records and distinguish historical hashes from hashes of public projections. Later release-stage downloads are recorded separately from the original source and semantic-review registers.

All annotation labels and evidence tables are unchanged from version 1.2. The only data-table value changes are the three cohort-manifest `distribution_status` cells, now `DISTRIBUTED_IN_RELEASE_SOURCE_ARCHIVES`. The dataset still contains 15 tables and 139 dictionary columns. Public reconstruction inputs reproduce the derived tables without administrative confirmation records or local source paths.

`download_sources.py` provides `inputs`, `documents` and `all` groups. Reconstruction commands use the portable English input layout, and the locator checker defaults to `source_materials/input/archive`. `CITATION.cff` records the resource title, authors, version and release date.

## Historical version 1.2 — September 8, 2026

This documentation and reuse update retains every version 1.1 data CSV byte for byte. The cohort, six-field labels, 16 amended cells, 11,120 positive memberships and all evidence/source layers remain unchanged.

Three new data tables provide 1,524 historical FDA-list row mappings, three original-artifact fingerprints, and 789 OTHER-membership note records. There are 206 recovered specific notes: 198 single-OTHER reasons and eight explicit multilabel fragments. Of these, 128 retain English/Latin wording and 78 are AI-assisted English translations. The other 583 multilabel contexts have an explicit unseparated-attribution status and no specific note. The dictionary covers 139 columns across 15 data tables.

The original CSV and XLSX contain identical six-column metadata. Original-CSV comparison matched the current cohort and public product-code mapping after normalizing dates and trimming two company names. At that assembly stage, original artifacts were held by the authors and the candidate package contained fingerprints and row mappings. Version 1.3.0 distributes those originals. The optional standard-library checker can repeat the comparison when given the original CSV.

A new standard-library retrieval exporter joins current input/output labels to original and later semantic evidence and offers a documented current-scope filter. The imaging query returns 1,154 authorizations, or 1,149 under that filter; the imaging-plus-segmentation query returns 653. These counts describe retrieval subsets, not new clinical-effect or accuracy results. Note projection, cohort checks and reuse examples have their own provenance and validation records.

## Historical version 1.1 — September 8, 2026

The cohort remains the June 29, 2026 FDA-list snapshot: 1,524 authorizations and 9,144 fields. This version integrates eight explicit amendments from the author-reported expert confirmation: K182034 gains a segmentation/localization output label; K190013 changes to unresolved function attribution with five NOT_ASSESSABLE fields and UNCERTAIN grouping. There are 11,120 positive-label memberships, 772 limited fields and 241 authorizations with at least one limited field.

The supplied confirmation draft matches the historical baseline, rather than source-updated version 1.0. Existing source amendments for K182513 and K233662 remain. The eight retained changes plus eight new changes total 16 cells across four authorizations in `version_changes.csv`. Its `change_class` distinguishes the two stages; historical baseline values remain intact.

The authors reported confirmation of the supplied 1,524-record/9,144-field draft. This is documented separately from prior source amendments. Twelve targeted fields are projected into `semantic_review_records.csv` with English reasons, pre/post values and page references. `semantic_review_sources.csv` retains six references, including one context-only source. The layer records author-supplied confirmation and source-access information. It does not contain paired independent ratings for estimating inter-rater agreement.

Original evidence, source-capture, bridge, associated-relationship, alias and vocabulary CSVs are byte-preserved. The 9,015 exact field anchors and 145 bridge anchors retain their original technical scope. New review page references are not promoted to exact machine spans. Three supplied retained text caches matched SHA-256; no new PDF bytes accompanied that confirmation stage.

`apply_confirmed_amendments.py` applies the fingerprinted increment reproducibly and can be rerun without changing integrated output. The dictionary now describes 114 columns in 12 public tables. Validation includes both amendment stages, semantic-review joins, dictionary coverage and preserved evidence bytes. Codex assistance remains disclosed in provenance and the README.

## Historical version 1.0 — September 7, 2026

The initial normalized candidate contained 1,524 authorizations, 9,144 fields and 11,127 positive-label memberships. Eight prior amended cells across K182513 and K233662 were retained. Technical layers comprised 48 coordinate corrections, 65 associated-source relationships, 145 field-linked bridges and the DEN130013/K124067 alias.

The operational field rules were retained; an analysis-specific historical paragraph was replaced by a scope note. That documentation adaptation and initial normalization did not recode labels. The September 8 confirmed amendments are a subsequent stage.
