# Source materials and complete reconstruction

The [v1.3.0 release](https://github.com/wang177777/fda-ai-clinical-function-annotations/releases/tag/v1.3.0) provides six source archives. `source_materials/archives.json` records each download URL, byte size, SHA-256 fingerprint and file count.

| Archive | Contents |
| --- | --- |
| `scientific_inputs.zip` | 3,166 files: normalization and scientific review inputs; original cohort CSV, XLSX and access metadata; the complete portable text cache; source notes, page images and supplementary PDFs; three review-reference PDFs captured for this release |
| `original_documents_01.zip`–`original_documents_05.zip` | All 3,109 distinct archived source captures indexed in `data/source_records.csv`: 1,584 PDFs, 1,524 HTML files and one retained non-PDF error response |

The source captures occupy 2,159,574,625 uncompressed bytes. Original bytes are preserved; content hashes name the distributed files and `original_document_manifest.json` retains original filenames, source URLs, source-record identifiers and subject identifiers. Multiple capture records can point to one file. The 16 capture records originally marked failed or unavailable are retained as records; they have no archived document bytes. The error response is explicitly identified as text rather than a PDF.

## Download and verify

From the repository root, using Python 3.10 or later:

```sh
python3 scripts/download_sources.py --group all
python3 scripts/validate_sources.py --group all
python3 scripts/validate_resource.py
```

The downloader verifies archive size and SHA-256 before extraction. To rebuild data tables and repeat text matching with a smaller download, use `--group inputs` with both source commands. Add originals later with `--group documents`. Existing archives in `--archive-dir PATH` are verified and reused. Downloaded archives and extracted source payloads are excluded from Git; their versioned manifests remain in the repository.

## Reproduce the data and locator checks

```sh
python3 scripts/rebuild_data.py
python3 scripts/recheck_text_locators.py --output text_locator_recheck.json
```

`rebuild_data.py` uses an isolated temporary directory, starts with no derived CSV tables, runs normalization, source-bridge, confirmed-amendment, OTHER-note and cohort-mapping steps, and compares all 15 tables with the released bytes. It leaves the released tables unchanged. Individual reconstruction commands are in the README.

The portable cache contains 3,121 files. Its 1,518 distinct hashes required for the retained exact-location checks reproduce 9,015 field anchors and 145 subject–source bridge anchors. Stored image transcriptions and web excerpts retain their source types. These checks locate retained quotations in the specified stored texts.

## Input provenance

`input_manifest.json` fingerprints every input archive member. After extraction, `source_materials/input/projection_manifest.json` distinguishes original fingerprints from public projection fingerprints. The authorization and field ledgers, cohort originals, and cross-authorization review input preserve their original bytes. Public scientific confirmation tables retain annotation values, source references and review outcomes while excluding signature administration. The normalized source manifest uses portable paths and omits two machine-specific absolute-path columns. The retained taxonomy input is available alongside the adapted six-field codebook in `docs/retained_taxonomy_rules_en.md`.

`source_addenda_manifest.json` inventories retained source notes, supplementary PDFs and page images. The mixed historical source index is represented by its FDA-source entries. A duplicate rendering and unrelated editorial administration are outside the scientific payload. Historical case-card HTML duplicates the retained ledgers and also contains parent-project fields; it is not needed to reconstruct this resource.

`review_reference_captures.json` records three PDFs retrieved on September 8, 2026 for release access. These new fingerprints supplement the historical review-source records without replacing historical provenance or creating new exact-span claims. No annotation values changed during this step.

## Reuse rights

Author-created data, annotations, documentation and manuscript figures are licensed under CC BY 4.0; code is licensed under MIT. Archived FDA documents and other third-party content retain their original rights, source attribution and notices. See [LICENSE.md](../LICENSE.md).
