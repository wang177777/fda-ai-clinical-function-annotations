#!/usr/bin/env python3
"""Generate a complete column dictionary for the normalized CSV tables."""
from resource_common import *

DESCRIPTIONS={
 'submission_number':('string','Stable FDA submission-level authorization identifier; PMA supplement slashes are retained.'),
 'device_name':('string','Public device name in the retained FDA list snapshot; not an independently deduplicated product identity.'),
 'company':('string','Retained public applicant/manufacturer string; spelling variants are not merged.'),
 'regulatory_pathway':('categorical','Retained authorization route: 510k, de_novo or pma.'),
 'date_of_final_decision':('date','Retained authorization decision date in YYYY-MM-DD form.'),
 'medical_specialty':('categorical','Retained FDA specialty/panel label, not a reclassified clinical specialty.'),
 'alternate_regulatory_identifier':('string','Different FDA identifier officially linked to the same subject authorization; not a new device or semantic recoding.'),
 'identity_source_url':('URL','FDA database page explicitly identifying the regulatory alias.'),
 'identity_source_access_date':('date','Date the public identity linkage was checked.'),
 'identity_basis':('string','Concise factual identity-linkage statement; no source quotation is republished.'),
 'baseline_ai_function_scope':('categorical','Source-attribution category before the retained targeted source amendments.'),
 'ai_function_scope':('categorical','Current source-attribution layer; see retained codebook and README. It does not imply that every ordinary algorithm is AI.'),
 'baseline_clinical_function_group':('categorical','Baseline SINGLE, MULTIPLE or UNCERTAIN clinical-function grouping.'),
 'clinical_function_group':('categorical','Current SINGLE, MULTIPLE or UNCERTAIN grouping of described clinical functions; not a number of internal models.'),
 'annotation_id':('string','Primary field key: submission_number followed by a colon and one of the six field names.'),
 'field':('categorical','One of input, output, user, setting, action, component_status.'),
 'baseline_codes':('semicolon-delimited code set','Unmodified baseline field labels in their retained order.'),
 'codes':('semicolon-delimited code set','Current versioned field labels; first five fields are nonexclusive, component_status is single-valued.'),
 'annotation_state':('categorical','CODED for positive content/function grouping; otherwise NOT_STATED, NOT_ASSESSABLE or UNCERTAIN.'),
 'source_limited':('boolean','true for NOT_STATED, NOT_ASSESSABLE or UNCERTAIN; false for CODED.'),
 'limitation_layer':('categorical','NONE, AI_ATTRIBUTION_BARRIER, SOURCE_INSUFFICIENT, FIELD_NOT_STATED or FUNCTION_GROUP_UNRESOLVED. Upstream barriers propagate across the six fields.'),
 'label':('categorical','One positive content label; limitation codes and component_status are excluded from this long table.'),
 'baseline_value':('string','Retained value before a documented existing amendment.'),
 'current_value':('string','Current value after the versioned source or confirmed semantic amendment.'),
 'change_class':('categorical','Retained source-update/scope-amendment class, or AUTHOR_REPORTED_EXPERT_CONFIRMED_AMENDMENT_2026_09_08 for the new confirmed changes.'),
 'source_record_id':('string','Stable source-capture record key; SRC refers to the legacy manifest and ADD to an additional reference if present.'),
 'subject_submission_number':('string','Authorization under which this source was indexed; not necessarily an identifier written in the source URL.'),
 'source_url':('URL','Retained FDA-hosted source URL; URL existence is not contemporaneous retrieval or subject-specific relevance validation.'),
 'source_document_type':('categorical','Retained document-type designation, such as FDA database HTML or a decision summary.'),
 'document_sha256':('SHA-256 or blank','SHA-256 of the archived source document recorded in the legacy manifest; blank means unavailable, not an empty-document hash.'),
 'text_sha256':('SHA-256 or blank','Source-record table: actual text hash recorded in legacy manifest. Evidence table: SHA-256 computed from the stored text artifact used in this assembly locator check. Artifacts may be extraction, web excerpt, or transcription.'),
 'retrieval_date':('timestamp or blank','Retained retrieval date/time; no new web retrieval is implied by assembling the resource.'),
 'retrieval_status':('categorical','Legacy success/unavailable/failed or an explicit not-retrieved status for an added reference.'),
 'record_origin':('categorical','LEGACY_SOURCE_MANIFEST or ADDITIONAL_ANNOTATION_REFERENCE; capture records are not unique documents.'),
 'source_record_ids':('semicolon-delimited identifiers','One or more matching source-capture record IDs; candidate linkage retains URL/source ambiguity rather than inventing a unique document.'),
 'recorded_source_url':('URL','Original annotation source URL, unchanged even when it identifies an associated authorization.'),
 'source_url_authorization_tokens':('semicolon-delimited identifiers','Authorization-like tokens parsed from URL, including PMA supplement suffix. Tokens are not a semantic verification of provenance.'),
 'source_authorization_relationship':('categorical','Direct subject URL token, officially linked alternate identifier, associated other-authorization legacy link, other-authorization source not indexed for subject, or no URL token. Associated-source detail must not be described as direct subject evidence.'),
 'subject_source_pair_in_legacy_manifest':('boolean','Whether the exact subject/canonical-URL pair was indexed in the original manifest. Canonical matching normalizes http/https and hostname case only.'),
 'quote_sha256':('SHA-256','SHA-256 of the original UTF-8 annotation quotation, without publishing that quotation.'),
 'recorded_locator_en':('string','English reconstruction of the retained page/span locator; internal cache paths and working notes are removed.'),
 'recorded_pages':('semicolon-delimited integers or blank','Reported physical PDF page numbers; HTML logical marker 0 is not a PDF page.'),
 'recorded_char_start':('integer or blank','Original zero-based start in whitespace-normalized page text; inclusive. A recorded value may be superseded only by an explicitly separate verified locator.'),
 'recorded_char_end':('integer or blank','Original zero-based exclusive end in whitespace-normalized page text.'),
 'normalized_quote_sha256':('SHA-256','SHA-256 after Python re.sub(r"\\s+", " ", quote).strip(); no case folding or Unicode transliteration.'),
 'normalized_quote_characters':('integer','Length in Unicode code points of the whitespace-normalized quote, not UTF-8 bytes.'),
 'verified_page':('integer or blank','Page with a unique exact quote match; 0 denotes HTML logical text. Blank for non-machine, unchecked image or multiple-page references.'),
 'verified_char_start':('integer or blank','Exact-match start added by mechanical checking; not a new semantic annotation.'),
 'verified_char_end':('integer or blank','Exact-match exclusive end added by mechanical checking.'),
 'verified_locator_en':('string or blank','Separate mechanically supported locator; the recorded locator remains available.'),
 'text_source_kind':('categorical','FDA_PDF_TEXT_EXTRACT, FDA_HTML_EXTRACT, STORED_WEB_EXCERPT, STORED_IMAGE_TRANSCRIPTION, or PAGE_ONLY_REFERENCE. Text matches to a transcription are not independent checks of FDA OCR or page imagery.'),
 'locator_check_status':('categorical','Exact original-span match, exact relocated quote, multiple-page occurrences without chosen correction, unchecked recorded image transcription, or no machine anchor. Full states are enumerated in validation/summary.json.'),
 'code':('categorical','One allowed value for its field in the retained codebook.'),
 'class':('categorical','POSITIVE_CONTENT_LABEL, FUNCTION_GROUP_STATE or LIMITATION_STATE.'),
 'multiple_values_allowed':('boolean','Whether the field permits more than one positive label; limitation states remain mutually exclusive.'),
 'bridge_id':('string','Unique subject/field/purpose/source/page/span anchor key, derived deterministically from these values and the normalized quotation hash.'),
 'anchor_document_submission_number':('string','FDA identifier of the document containing the bridge passage; may be an intermediate authorization.'),
 'anchor_purpose':('categorical','SUBJECT_TO_ASSOCIATED_SOURCE_BRIDGE, INTERMEDIATE_SOURCE_CHAIN_BRIDGE, or SUBJECT_SOURCE_ADDITIONAL_DETAIL. A bridge is not an equivalent replacement for the original detail quotation.'),
 'physical_page':('integer','One-based physical PDF page containing the bridge passage.'),
 'normalized_char_start':('integer','Zero-based inclusive start of a whitespace-normalized bridge excerpt within its physical page text.'),
 'normalized_char_end':('integer','Zero-based exclusive end of the whitespace-normalized bridge excerpt.'),
 'subject_source_url':('URL','Subject authorization document used to establish an associated-source relationship or its boundary.'),
 'source_relationship':('categorical','Descriptive source-continuity relation identified in the targeted AI-assisted provenance review; not a semantic accuracy or independent human-review grade.'),
 'support_scope_note':('string','English source-support boundary explaining why linked-source detail is not necessarily direct, exhaustive current-subject evidence; no long quotation or private workflow note.'),
 'source_caution_codes':('semicolon-delimited categories or blank','Scientific source-use cautions such as scope exclusions, configuration limits and feature details not restated; not reviewer identity, confidence or approval status.'),
 'review_record_id':('string','Unique versioned semantic-review record identifier; one row for each of the 12 targeted authorization-field positions.'),
 'review_version':('string','Identifier of the supplied confirmation package; distinct from the public release version.'),
 'review_date':('date','Author-supplied confirmation date in YYYY-MM-DD form; not an individual reading or signing timestamp.'),
 'confirmation_basis_id':('string','Identifier of the author-provided statement reporting expert confirmation of the supplied draft.'),
 'review_date_basis':('categorical','AUTHOR_SUPPLIED_CONFIRMATION_DATE; no individual reading or signing timestamp is inferred.'),
 'review_status':('categorical','AUTHOR_REPORTED_EXPERT_CONFIRMATION; records a confirmed coding decision without claiming an independent dual-review design.'),
 'pre_review_codes':('semicolon-delimited code set','Targeted field labels before this confirmed amendment; prior source corrections elsewhere remain independently versioned.'),
 'post_review_codes':('semicolon-delimited code set','Targeted field labels after the confirmed decision, equal to the current field-annotation values.'),
 'pre_review_scope':('categorical','Target authorization scope before the confirmed decision.'),
 'post_review_scope':('categorical','Target authorization scope after the confirmed decision, equal to the current authorization-table value.'),
 'codes_amended':('boolean','true if the field label set changed in this targeted review; false if confirmed without a code amendment. A source-review record can exist in either case.'),
 'review_source_ids':('semicolon-delimited identifiers','One or more keys in semantic_review_sources.review_source_id; split before joining.'),
 'review_locator':('string','English page/table references from the confirmed review; these are not newly verified normalized character spans.'),
 'public_reason':('string','English summary of the confirmed semantic coding basis, projected from the fingerprinted scientific review records distributed in the source archives.'),
 'new_locator_check_status':('categorical','PAGE_REFERENCES_ONLY_NOT_NEW_MACHINE_SPANS. Existing evidence_links machine-anchor states remain a separate historical check.'),
 'review_source_id':('string','Unique versioned key for one of six source references retained in the targeted-review log; one is context-only and has no field link.'),
 'source_document_submission_number':('string','FDA identifier of the referenced document, which may be a comparison subject or an earlier product version.'),
 'physical_pages_reviewed':('semicolon-delimited positive integers','One-based physical PDF page range identified in the supplied review log; the recorded access note distinguishes readable text from image inspection.'),
 'review_source_role':('categorical','TARGET_SUBJECT_SUMMARY, COMPARISON_SUBJECT_SUMMARY, RELATED_VERSION_CONTEXT, or REVIEW_LOG_CONTEXT_NOT_FIELD_CITED.'),
 'existing_source_record_ids':('semicolon-delimited identifiers or blank','Matching entries in the retained source-capture manifest. Blank for review references not present there; it does not create a new source-capture claim.'),
 'review_document_sha256':('SHA-256 or blank','SHA-256 of PDF bytes supplied with the September 8 confirmation inputs; blank for all six historical review references. Subsequent release-stage captures are recorded separately in the source-material manifest.'),
 'retained_text_sha256':('SHA-256 or blank','Hash of an actually supplied retained text cache, verified to match the existing source text artifact. Blank where no review text cache was supplied.'),
 'review_material_status':('categorical','RETAINED_TEXT_AND_REPORTED_SOURCE_INSPECTION or URL_AND_REPORTED_SOURCE_INSPECTION; both retain the source-access boundary in source_access_note.'),
 'reported_source_access_date':('date','Source access date reported in the supplied review log; integration does not itself perform new retrieval.'),
 'source_access_note':('string','English description of reported text/image access and archival limitations, including failed image captures where relevant.'),
}


DESCRIPTIONS.update({
 'snapshot_id':('string','Fixed cohort snapshot identifier, shared by three artifact-manifest rows and all membership rows.'),
 'snapshot_row_number':('integer','One-based CSV record position after the header in the retained original FDA list; unique within the snapshot.'),
 'primary_product_code':('string','Primary FDA product code copied from the retained original cohort list; not a new clinical-function label.'),
 'metadata_match_status':('categorical','MATCH_AFTER_DATE_NORMALIZATION or MATCH_AFTER_DATE_AND_COMPANY_TRIM; refers to historical list metadata matching.'),
 'snapshot_artifact_id':('string','Unique identifier for a retained cohort CSV, XLSX or source-metadata artifact.'),
 'artifact_name':('string','Basename of the retained original cohort artifact; no private filesystem path.'),
 'artifact_sha256':('SHA-256','SHA-256 of retained original bytes, matched against the historical metadata and archive.'),
 'artifact_bytes':('integer','Byte length of the retained original artifact.'),
 'recorded_access_date':('date','Historical source access date recorded in retained metadata; not a new download date.'),
 'artifact_format':('categorical','CSV, XLSX or TXT for the historical cohort artifact.'),
 'distribution_status':('categorical','DISTRIBUTED_IN_RELEASE_SOURCE_ARCHIVES; the three retained originals are distributed under source_materials/input/cohort.'),
 'other_note_en':('string or blank','Retained English/Latin note or English translation for the OTHER membership. Blank where the multi-label field reason did not isolate an OTHER meaning.'),
 'other_note_status':('categorical','SINGLE_OTHER_EXISTING_FIELD_REASON, EXPLICIT_OTHER_ASSIGNMENT_IN_RETAINED_REASON, or MULTILABEL_OTHER_ATTRIBUTION_NOT_ISOLATED; a documentation status, not an annotation-state change.'),
 'note_original_language':('categorical or blank','en_or_latin or zh for the extracted original fragment; blank when no OTHER-specific fragment was isolated.'),
 'note_processing':('categorical','RETAINED_ENGLISH_OR_LATIN_TEXT, AI_ASSISTED_ENGLISH_TRANSLATION, or NO_OTHER_SPECIFIC_NOTE_ADDED.'),
 'note_original_sha256':('SHA-256 or blank','Hash of the exact retained UTF-8 note fragment before translation; blank for unseparated multi-label contexts.'),
 'retained_field_record_number':('integer','One-based CSV record position after the header in the fingerprinted original field ledger; embedded newlines do not start new records.'),
 'retained_input_sha256':('SHA-256','Fingerprint of the historical field ledger containing the note; shared with the initial input-provenance record.'),
 'retained_source_column':('string','decision_reason, the original field-ledger column from which the existing note was extracted.'),
})

def main():
    rows=[]
    for path in sorted(DATA.glob('*.csv')):
        values=read_csv(path)
        if not values:continue
        for field in values[0]:
            assert field in DESCRIPTIONS,field
            kind,description=DESCRIPTIONS[field]
            if path.name=='version_changes.csv' and field=='field':
                description='One of input, output, user, setting, action, component_status, or ai_function_scope. Scope amendments are recorded separately from the six annotation fields.'
            if path.name=='cohort_snapshot_manifest.csv' and field=='recorded_source_url':
                description='Original FDA list-page or download URL. Cohort downloads may change over time; artifact hashes identify the retained version.'
            rows.append({'table':path.name,'column':field,'type':kind,'description':description,'blank_cells':sum(r[field]=='' for r in values)})
    csvout(ROOT/'docs/data_dictionary.csv',rows)
    print({'documented_columns':len(rows),'tables':len({r['table'] for r in rows})})

if __name__=='__main__':main()
