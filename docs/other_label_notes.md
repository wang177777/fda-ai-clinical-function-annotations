# Retained descriptions for OTHER labels

`data/other_label_notes.csv` contains one row for each of the 789 current field annotations with the exact positive code `OTHER`. Join it to `field_annotations.csv` and the evidence tables by `annotation_id`. Tokens such as `OTHER_PHYSICIAN` and `OTHER_CLINICIAN` do not count as `OTHER`.

The table restores descriptions already present in the fingerprinted annotation ledger. It supplies 198 existing field reasons where OTHER is the sole code, plus eight fragments that explicitly identify OTHER within a multi-label reason. For the other 583 multi-label fields, an OTHER-specific description could not be isolated from the existing whole-field reason. Their note remains blank with status `MULTILABEL_OTHER_ATTRIBUTION_NOT_ISOLATED`. A blank here is a documentation gap within an existing positive OTHER annotation, not a new NOT_STATED or NOT_ASSESSABLE state.

The 206 populated notes comprise 128 retained English or Latin-character strings and 78 English translations of existing Chinese notes. `note_processing` distinguishes these operations. Codex assisted with the translations, preserving limitations and negation in the original notes. No new category assignments or independent expert validation of the English wording are reported. Some retained strings are compact identifiers rather than prose.

`retained_input_sha256` identifies the original field ledger; `retained_field_record_number` counts CSV records from one after the header, including any embedded newlines within a single CSV record. `note_original_sha256` fingerprints the exact original fragment before translation. The original field ledger is distributed as `source_materials/input/annotations/field_taxonomy_9144.csv`. The scientific extraction audit and translation inputs are in `source_materials/input/other_notes`; obtain them with `python3 scripts/download_sources.py --group inputs`. The source URLs and locator status remain accessible through the existing evidence links for the same annotation.

Use these notes to inspect the meaning and boundaries of a retained OTHER label, together with its whole field, source scope and evidence. The table does not introduce mutually exclusive OTHER subcategories or establish that all meanings have been exhaustively recovered. A future refinement should preserve the current category and source version while recording any subsequent decision separately.

## Rebuild the notes

After constructing the current annotation tables, run:

```sh
python3 scripts/build_other_notes.py --audit-file source_materials/input/other_notes/other_explanations.json --retained-fields source_materials/input/annotations/field_taxonomy_9144.csv --translations-file source_materials/input/other_notes/translations.json
```

The builder checks the fingerprinted field ledger and note-fragment hashes before writing the 789-row table. The public audit and translation files preserve the scientific content needed for this projection and record their relationship to the retained originals.
