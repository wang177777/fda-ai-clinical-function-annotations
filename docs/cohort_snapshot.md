# Historical cohort snapshot and record mapping

The cohort is linked to the retained FDA AI-Enabled Medical Devices List CSV accessed on June 29, 2026. Its 1,524 submission identifiers match the current authorization table exactly. This addition records historical membership and metadata provenance; it does not update the cohort or recode clinical-function labels.

## Public tables

`data/cohort_snapshot_membership.csv` has one row per authorization:

| Column | Meaning |
| --- | --- |
| `submission_number` | Authorization key; joins to `authorizations.csv`. |
| `snapshot_id` | `FDA_AI_LIST_2026-06-29`; links to the three artifact records in the snapshot manifest. |
| `snapshot_row_number` | One-based CSV data-record position, excluding the header. This is a parsed CSV record number, not a physical line number: a quoted cell can contain a newline. |
| `primary_product_code` | The original FDA three-letter primary product code. It is retained as regulatory metadata, separate from the clinical-function taxonomy. |
| `metadata_match_status` | `MATCH_AFTER_DATE_NORMALIZATION` for 1,522 records; `MATCH_AFTER_DATE_AND_COMPANY_TRIM` for two records. |

`data/cohort_snapshot_manifest.csv` has three rows for the original CSV, original XLSX and contemporaneous TXT source-metadata record. `snapshot_artifact_id` uniquely identifies an artifact; `snapshot_id` is shared by all three. The remaining columns record the basename, SHA-256, byte length, recorded access date, recorded source URL, format and distribution status. The CSV and XLSX URLs are the recorded official download URLs. The TXT URL identifies the FDA page described by the locally retained metadata record; it is not a URL for downloading that TXT file.

All three raw artifacts have status `DISTRIBUTED_IN_RELEASE_SOURCE_ARCHIVES`. They are distributed under `source_materials/input/cohort`, alongside the derived membership map and artifact fingerprints. Run `python3 scripts/download_sources.py --group inputs` to install the exact retained CSV, XLSX and source-metadata TXT. The artifacts form a separate cohort register and do not change the 3,173-row source-capture manifest used for field evidence.

## Reproduce the checks

Python 3.10 or later and the standard library are sufficient. From the repository directory:

```sh
python3 scripts/check_cohort_snapshot.py
```

The default command checks that all 1,524 authorization keys occur exactly once, original record positions cover 1–1,524 exactly once, product codes and status values are valid, and all three artifact records have the expected identifiers, date, URL structure and fingerprint syntax. It prints JSON and does not alter the repository. Raw-byte comparison is enabled by the explicit original-file command below.

After downloading the input archive, compare the original CSV:

```sh
python3 scripts/check_cohort_snapshot.py --snapshot-csv source_materials/input/cohort/fda_ai_enabled_devices_2026-06-29.csv
```

The optional `--output /path/to/check.json` saves the report; it contains no supplied private path. The function `check_snapshot(repository, snapshot_csv=None)` provides the same checks for a Python caller. A failed comparison exits unsuccessfully rather than silently accepting a newer download. The script makes no network requests.

With the original CSV, checks first require its exact SHA-256 and byte length, then compare every original data record, its position and all six source columns:

| Original column | Comparison |
| --- | --- |
| `Date of Final Decision` | Parse `MM/DD/YYYY`; compare ISO `YYYY-MM-DD` with `authorizations.date_of_final_decision`. |
| `Submission Number` | Exact comparison with `authorizations.submission_number`. |
| `Device` | Exact comparison with `authorizations.device_name`. |
| `Company` | Remove only leading/trailing whitespace with `str.strip()`; compare with `authorizations.company`. |
| `Panel (Lead)` | Exact comparison with `authorizations.medical_specialty`. |
| `Primary Product Code` | Exact comparison with `cohort_snapshot_membership.primary_product_code`. |

Only DEN220024 and DEN230027 require company-whitespace normalization; their original cells contain leading tab/newline characters. Case, punctuation and internal whitespace are not normalized. No fuzzy name matching is used.

## Rebuild the two public tables

Rebuild from the three originals installed by the input archive:

```sh
python3 scripts/build_cohort_mapping.py \
  --snapshot-csv source_materials/input/cohort/fda_ai_enabled_devices_2026-06-29.csv \
  --snapshot-xlsx source_materials/input/cohort/fda_ai_enabled_devices_2026-06-29.xlsx \
  --metadata-txt source_materials/input/cohort/source_metadata_2026-06-29.txt
```

The default writes only `data/cohort_snapshot_membership.csv` and `data/cohort_snapshot_manifest.csv`. Add `--output-dir /path/to/staging` to reconstruct the files in a separate directory. The script requires the current `authorizations.csv` but does not read existing cohort tables. It first verifies all three originals against the fixed retained fingerprints, projects original CSV record positions and product codes, and checks all six metadata columns through `check_snapshot` in a temporary directory. Destination files are written only after those checks pass. The CSV row order, column order, UTF-8 encoding and CRLF record terminators reproduce the retained public tables byte for byte; repeated runs preserve identical files. The original twelve data tables and the source originals are unchanged. Refresh the release checksums only after completing and verifying an intended rebuild.

## Retained verification result

`validation/cohort_snapshot_check.json` records the successful original-CSV comparison performed for this addition: 1,524 keys, 1,524 original record positions and 9,144 source-metadata cells matched. These six source columns are distinct from the six clinical annotation fields, which coincidentally also yield 9,144 field positions.

The retained CSV contains 132,922 bytes, with SHA-256 `4da0d15a1dcc7b6a7d45364f243e85aa4407ba3b63b6922a16fdbf96fea0d41d`. The other two raw-artifact fingerprints are recorded in the manifest; this script's optional byte comparison covers the CSV only. Neither a checksum match nor the preserved access log independently authenticates the historical HTTP retrieval time. A current FDA download can differ from the retained June 29 snapshot and should not be substituted without a separately documented cohort update.
