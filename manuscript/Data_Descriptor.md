# Clinical-function annotations for 1524 US artificial intelligence medical-device authorizations

Article type: Data Descriptor

Guoyong Wang, MD[1]; Kaijun Zhang, MD[2]; Jiyue Jiang, PhD[3]; Weixin Wang, MD[1]; Hui Bi, MD[4]; Haojun Liang, MD[5]; Zuoliang Qi, MD[5]; Ying Huang, MD[2]; Yu Li, PhD[3,6]; Xiaonan Yang, MD[1]

Guoyong Wang, Kaijun Zhang, and Jiyue Jiang contributed equally.

1. Department of Hemangioma and Vascular Malformation, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing, China.

2. Department of Gastroenterology, Children's Hospital of Fudan University, National Children's Medical Center, Shanghai, China.

3. Department of Computer Science and Engineering, The Chinese University of Hong Kong, Hong Kong SAR, China.

4. Department of Internal Medicine, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing, China.

5. Department of Comprehensive Plastic Surgery, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing, China.

6. The CUHK Shenzhen Research Institute, Shenzhen, China.

Corresponding author: Xiaonan Yang, MD, Department of Hemangioma and Vascular Malformation, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China. Email: yxnan@aliyun.com.

## Abstract

Public regulatory documents describe the clinical functions of artificial intelligence (AI)–enabled medical devices in heterogeneous formats. We assembled a source-linked annotation dataset covering 1524 US Food and Drug Administration submission-level authorizations from the list accessed June 29, 2026. Six fields describe input, output, intended user, setting or use context, downstream action, and clinical-function grouping. The dataset contains 9144 field records and 11120 nonexclusive positive-label memberships across the first five fields. Assessment states distinguish unresolved AI attribution, insufficient source material, and information not stated. Evidence tables connect annotations to source documents, text coordinates, and cross-authorization relationships. Expert confirmation of the supplied draft and two targeted coding decisions complements executable checks of cohort membership, structural consistency, and evidence location. The release includes the historical cohort snapshot, retained source materials, annotation inputs, dictionaries, and reconstruction code. These materials support targeted source retrieval, documented subset construction, and development of annotation methods.

## Background & Summary

Public documentation of AI-enabled medical devices provides information about the data a function consumes, the result it produces, and its intended clinical use. The US Food and Drug Administration (FDA) list provides submission identifiers through which these descriptions can be linked across regulatory documents.[1] Reuse requires a consistent representation of clinical functions alongside the passages and source versions used to assign each annotation. It also requires distinguishing language about a whole device from language attributable to an AI-related function.

Previous studies have classified clinical and AI functions across FDA authorizations and characterized intended use and clinician-facing interfaces.[2,3] Work on automated regulatory-document extraction and structured clinical AI documentation further shows the value of organizing these descriptions for analysis.[4,5] Our resource extends this work through an authorization-level release that combines six annotation fields with explicit assessment states, field-linked provenance, source-association records, and executable integrity checks. These features allow users to inspect both a label and the scope of its supporting source.

We organize a defined cohort into linked tables for authorizations, annotations, label memberships, and evidence (Fig. 1). A researcher can use the resource to retrieve source documents for a chosen input or output category, distinguish field-specific missing information from unresolved AI attribution, or assemble a documented sample for subsequent annotation validation. Stable identifiers, dictionaries, and version records support these uses and the traceability and reuse objectives of the FAIR principles.[6]

The authorization cohort and part of the downstream-action taxonomy are shared with a broader public-disclosure study. This Data Descriptor documents the six-field annotation resource and its supporting evidence.

## Methods

### Cohort and source collection

The cohort comprises the 1524 submission-level records in the FDA list accessed June 29, 2026.[1] The retained authorization decision dates range from September 29, 1995, to March 30, 2026. Source retrieval records are dated June 30, 2026. The historical CSV and XLSX snapshots, access metadata, SHA-256 fingerprints, and original record positions are included in the release. Submission number is the linkage key, and device name and company are descriptive attributes. Multiple authorizations for a product family remain separate records. The observation unit is therefore an authorization, with products, internal models, and clinical deployments represented only insofar as they are described in the source material.

Eligible sources were FDA-hosted or FDA-linked database entries, summaries, decision documents, labeling, and Indications for Use statements. The retained manifest contains 3173 retrieval records, including repeat captures. Retrieval dates and available document and text hashes identify the source versions. Inclusion on the FDA list identifies the cohort, while attribution of a particular description to an AI or algorithmic function is recorded separately. The resource contains public regulatory information and no individual participant data or identifiable private health information.

### Annotation provenance and definitions

The dataset was assembled from study annotations, a field-level evidence ledger, a source manifest, and amendment records. In the review documented on September 8, 2026, Xiaonan Yang and Weixin Wang confirmed the supplied draft record by record across 1524 authorizations and 9144 authorization–field positions. The confirmation covered labels, assessment states, function attribution, rationales, and FDA source locators. The review procedure specified discussion between the two reviewers, with unresolved disagreements to be referred to Zuoliang Qi. The release records the supplied draft separately from the source-based amendments integrated during assembly.

Two authorizations received targeted review of coding boundaries. The confirmed decisions added segmentation/localization to the output labels for K182034 and assigned unresolved AI attribution to K190013, with the corresponding assessment states propagated to its six fields. These decisions comprise seven field amendments and one scope amendment. The version ledger combines them with eight earlier source-based amendments and preserves the baseline values.

The first five fields contain nonexclusive sets of labels. Input describes data directly consumed by the AI or algorithmic function. Output describes the reported result connected to that function, including downstream results explicitly linked to it. Intended user identifies the described user of the function. Setting or use context includes both clinical purposes, such as screening and monitoring, and locations. Downstream action records a stated connection between the output or described use and a subsequent clinical activity. The operational codebook supplies allowed values and boundary rules, including the distinction between intended users and validation-study participants and between a prediction and an ensuing treatment decision.

The sixth field records clinical-function grouping as SINGLE, MULTIPLE, or UNCERTAIN. Its original column name, `component_status`, is retained for compatibility. Grouping concerns distinguishable clinical functions: one function may have several outputs or use several internal models, and separate functions may share a broad output category. This is a study-specific coding definition, distinct from the FDA's regulatory framework for multiple-function device products.[7]

For authorizations with multiple functions, the first five fields contain the union of the supported labels. Indications for Use statements and other eligible passages contribute to the same six fields. Input–output–action membership is represented at the authorization level.

### Assessment states

Three authorization-level scope states distinguish a described AI or algorithmic function, a device function with unresolved AI attribution, and insufficient source material. The latter two states propagate to all six fields through `limitation_layer`. This hierarchy separates a source-wide assessment barrier from information not stated in an otherwise assessable field.

For the first five fields, NOT_STATED means the reviewed eligible content did not specify the field, and NOT_ASSESSABLE means source scope or insufficiency prevented classification. UNCERTAIN records unresolved clinical-function grouping. OTHER is a positive category for explicitly described content outside the named categories. NOT_STATED describes the reviewed material rather than the presence or absence of a function in practice.

The repository table `other_label_notes.csv` covers all 789 fields carrying the exact code OTHER. Existing reasons yield 206 retained explanations: 198 from fields coded only as OTHER and eight from multilabel reasons explicitly assigning content to OTHER. The other 583 multilabel reasons do not isolate an OTHER-specific description and retain an explicit unseparated-note status. We preserved 128 English or Latin-character notes and translated 78 existing Chinese notes into English with AI assistance. The table records source-row positions, fragment hashes, and language-processing status. Field labels remain unchanged.

### Versioned assembly and evidence coordinates

Each annotation identifier combines submission number and field name. Baseline and current values are retained, and positive labels are expanded into annotation–code membership rows. The cumulative amendment ledger contains 16 changed cells across four authorizations: eight prior amendments and eight amendments from the September 8 confirmation. Thirteen changes concern annotation fields and three concern scope. Input-file hashes and review provenance identify the successive annotation versions.

Evidence records link annotation identifiers to source-record identifiers and preserve the recorded public URL. URL-token checks identify references to the subject authorization, alternate identifiers, or another authorization. Cross-authorization references receive a separate source-association review because an earlier authorization can describe an inherited or integrated function. The resulting relationship and caution codes are retained with the original labels.

PDF page numbers refer to physical pages counted from one. Character intervals are zero-based, half-open offsets after whitespace normalization within an extracted page. Evidence records retain the source-text and quotation hashes, quote length, recorded coordinates, checked coordinates where established, and locator-check status. The release includes the normalization and locator routines. The September 8 semantic review adds page-level source references in separate tables; it preserves the earlier coordinate audit and its check statuses. The source-material archives include the retained document captures, annotation evidence, and text cache. Document and text hashes identify the versions used for the recorded coordinates.

### AI assistance

Codex (OpenAI) assisted with source organization, draft taxonomy development, data normalization, development and testing of the assembly and validation scripts, source-association and locator checks, and manuscript drafting and revision. Available records identify the models gpt-5.6-sol and gpt-6-astra. Codex also assisted with translating 78 retained Chinese OTHER notes into English; the processing status is recorded in `other_label_notes.csv`. Figures were rendered programmatically from the data structure and verification counts. Confirmation of the supplied draft and the two targeted coding decisions is described above. The authors take responsibility for the final data, code, and manuscript.

## Data Records

Version 1.3.0 is available at https://github.com/wang177777/fda-ai-clinical-function-annotations/releases/tag/v1.3.0. The release contains 15 UTF-8 comma-separated data tables, documentation, code, and source-material archives. Table 1 lists the principal files and their units. `authorizations.csv` supplies the submission key, `field_annotations.csv` holds six records per authorization, and `positive_labels.csv` records memberships for the first five fields. Clinical-function grouping remains in the authorization and field tables. Evidence references are assigned to fields and accompany their positive-label sets.

`evidence_links.csv` provides a retained evidence record for every annotation, including contextual evidence for unresolved states. It links to retrieval records in `source_records.csv` and to the focused cross-authorization review in `associated_source_relationships.csv`. `source_bridges.csv` adds field-linked anchors for subject-to-associated-source relationships and relevant details. Source-record identifiers use semicolon-delimited lists, which are parsed before joining to the source table. The September 8 targeted review is represented by 12 rows in `semantic_review_records.csv`, linked by annotation identifier to the field table and to the cited entries in the six-reference `semantic_review_sources.csv` register. Five references are field-cited; one is retained for context. These records supply the rationale and page references for the confirmed amendments, including the added K182034 output category.

`cohort_snapshot_membership.csv` links each authorization to its original FDA-list record position and primary product code. `cohort_snapshot_manifest.csv` identifies the three distributed snapshot artifacts by filename, source URL, date, size, and hash. `other_label_notes.csv` joins to field annotations by `annotation_id` and distinguishes 206 populated notes from 583 unseparated multilabel contexts. Its processing fields identify retained wording and English translations.

The data dictionary defines all 139 columns across the 15 data tables, including types, keys, missing-value conventions, and joining rules. The operational codebook defines category boundaries, while `version_changes.csv` and the locator audit record label amendments and technical coordinate changes separately. The vocabulary, summary, validation reports, and checksums accompany the release. The source-material manifest maps retained files to the capture records. It distinguishes FDA document captures, text extracts, image transcriptions, web excerpts, and later reference downloads. Source archives also provide the cohort originals and scientific inputs needed to reconstruct the derived tables.

## Data Overview

The release contains 1524 authorizations, 9144 field records, and 11120 positive-label memberships. Of the authorizations, 1421 have the described-function scope, 101 have unresolved AI attribution, and 2 have insufficient source material. Table 2 summarizes the stored field states. The 103 authorization-level barriers account for 618 limited field records; a further 154 field-specific limitations occur among the 1421 authorizations within the described-function scope.

## Technical Validation

### Structural consistency

The standalone validator checks cohort size, unique keys, six-field coverage, permitted states and codes, agreement between authorization and field tables, positive-label expansion, and source-record links. It also checks scope propagation, the retained amendment history, and release-file hashes. These checks and the accompanying usage examples run on the distributed tables without network access or proprietary software.

### Historical cohort and note provenance

The historical CSV and XLSX contained the same 1524 unique submissions in the same order, with identical values across six original columns. Comparison with the release matched submission identifiers, device names, FDA panels, primary product codes, and normalized decision dates; two company names additionally required trimming leading whitespace. All 1524 original record positions are represented in the public mapping. Using the distributed original CSV, the snapshot checker verifies its fingerprint and repeats the six-column comparison.

All 206 retained OTHER explanations occurred verbatim in the fingerprinted annotation reasons before translation. The validator checks exact-code membership, note coverage, source-row references, and language-processing states.

### Evidence-location audit

The retained coordinate audit assigns a locator-check status to all 9144 evidence records (Fig. 2). The separately recorded September 8 semantic-review references are page-level locators and are outside these exact-span counts. Exact text matched at the recorded normalized span for 8967 records. A further 26 matched after correction of the span on the same page, and 22 after correction of the page or span. These 48 corrections add checked coordinates while preserving the original coordinates and labels. Two quotations occurred on multiple pages without a unique automatically selected replacement. Another 121 records retained image-transcription references that were not rechecked against the source image, and 6 had page-only references.

The 9015 exact anchors comprise 8939 matches to PDF text extracts, 42 to FDA HTML extracts, 18 to stored web excerpts, and 16 to stored image transcriptions. Matching a stored transcription establishes a location within that transcription; its fidelity to the source image was not independently checked. The distributed text cache contains all 1518 text hashes required for the 9015 exact field anchors and 145 bridge anchors. Repeating the locator check against these archived text versions reproduced every corresponding substring hash.

### Cross-authorization source review

Following normalization of PMA supplement-identifier formatting and recognition of DEN130013 and K124067 as alternate identifiers for the same subject, the focused review covered 65 field records, 20 subject authorizations, and 21 subject–source pairs. The 20 subject-document hashes matched the retained manifest. Associated-source quotations were retained at their original locations because the same wording was not reproduced in the subject's extracted text. We added 145 field-linked anchors: 115 subject-relationship anchors, 24 intermediate-chain anchors, and 6 supplementary detail anchors. These represent 43 distinct text locations, defined by text hash, physical page, and character interval. At all 145 anchors, the normalized source substring matched the recorded quotation hash.

The recorded relationships distinguish named feature adoption, multistep continuity, general software or performance continuity, and separately cleared integrated functions. Five subjects, covering 16 field records, had general continuity evidence without the AI feature being named in the current summary. Two subjects, covering 10 field records, described integrated AI as outside the current submission's scope. Caution codes also identify configuration restrictions and excluded predecessor functions. These flags qualify the retained labels for analyses of the AI function described in the current submission.

### Validation scope

The checks assess cohort identity, table consistency, evidence location, and the recorded relationships between source authorizations. All 3109 retained capture files matched their recorded hashes: 1584 PDF files, 1524 HTML files, and one non-PDF failure response. The capture manifest also identifies 16 failed retrievals with no retained document file. Three review-reference PDFs downloaded during release preparation accompany this retained capture set. Expert confirmation covered the supplied annotation draft and the two targeted coding decisions for K182034 and K190013.

Semantic accuracy and label completeness were not independently estimated. Paired pre-discussion ratings were unavailable, so inter-rater agreement was not calculated. Reuse should account for annotation scope, field-specific limitations, and shared products or source documents.

## Usage Notes

Start with `authorizations.csv`, join the six field records by submission number, and select the relevant assessment states before expanding positive labels. The `export_reuse_subset.py` script joins current input and output labels to original evidence, source relationships, bridge anchors, and later semantic-review references. Selecting MEDICAL_IMAGE returns 1154 authorizations; additionally selecting SEGMENTATION_OR_LOCALIZATION output returns 653. The documented current-scope filter retains 1149 imaging authorizations by requiring described-function scope and coded input/output fields and excluding specified source-relationship restrictions. Commands, denominators, and exported fields are described in `docs/reuse_examples.md`.

Report denominators at the authorization level because one record can contribute several labels. Authorization-level co-occurrence does not identify input–output–action pairs for individual components. Before interpreting evidence from another authorization, inspect its relationship and bridge records, including whether the named function belongs to the current submission. Source-document and text hashes support retrieval of the versions used for annotation.

The codebook and OTHER-note table provide category definitions and retained explanations. For example, THERAPY_DOSE_OR_DEVICE_CONTROL includes clinician-mediated changes and automatic control, while HOME_OR_CONSUMER includes some nonclinical consumer contexts. In the OTHER-note table, the unseparated status identifies a retained positive label whose whole-field reason does not isolate a specific explanation. Processing flags distinguish original wording from AI-assisted English translations.

The data support descriptive reuse, source retrieval, and annotation-method development. Regulatory descriptions alone do not establish clinical safety or effectiveness. Related authorizations and shared documents create dependencies; model-development studies should assess leakage across authorizations, product families, manufacturers, and source documents. Record the dataset version, selection rules, and any subsequent source-based corrections.

## Data Availability

The annotation tables, dictionaries, historical cohort files, retained source materials, and scientific reconstruction inputs are openly available in release v1.3.0 at https://github.com/wang177777/fda-ai-clinical-function-annotations/releases/tag/v1.3.0. The repository provides individual derived files and downloadable source archives with SHA-256 manifests. Author-created data and documentation are licensed under CC BY 4.0. FDA-hosted source materials retain their original attribution and rights.

## Code Availability

The assembly, validation, source-download, and retrieval scripts are available at https://github.com/wang177777/fda-ai-clinical-function-annotations/tree/v1.3.0/scripts under the MIT license. Data reconstruction and validation use Python 3.10 or later and the standard library. The repository documents how to download the source archives, reproduce the derived tables, and repeat the evidence-location checks. Figure-generation code and its rendering dependencies are provided in `figure_generation/`.

## References

1. US Food and Drug Administration. Artificial Intelligence-Enabled Medical Devices. https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices (accessed 29 June 2026).

2. Singh, R., Bapna, M., Diab, A. R., Ruiz, E. S. & Lotter, W. How AI is used in FDA-authorized medical devices: a taxonomy across 1,016 authorizations. npj Digit. Med. 8, 388 (2025). https://doi.org/10.1038/s41746-025-01800-1

3. McNamara, S. L., Yi, P. H. & Lotter, W. The clinician-AI interface: intended use and explainability in FDA-cleared AI devices for medical image interpretation. npj Digit. Med. 7, 80 (2024). https://doi.org/10.1038/s41746-024-01080-1

4. Li, H. et al. Scaling medical device regulatory science using large language models. npj Digit. Med. 9, 221 (2026). https://doi.org/10.1038/s41746-026-02353-7

5. Lohachab, A. et al. SMART: structured, meaningful, auditable, responsible, and transparent documentation for clinical AI. J. Am. Med. Inform. Assoc. ocag117 (2026) doi:10.1093/jamia/ocag117.

6. Wilkinson, M. D. et al. The FAIR Guiding Principles for scientific data management and stewardship. Sci. Data 3, 160018 (2016). https://doi.org/10.1038/sdata.2016.18

7. US Food and Drug Administration. Multiple Function Device Products: Policy and Considerations. https://www.fda.gov/regulatory-information/search-fda-guidance-documents/multiple-function-device-products-policy-and-considerations (2020).

## Funding

This work was supported by the Special Program for Clinical and Translational Medical Research of the Chinese Academy of Medical Sciences (2025-12M-C&T-B-067); the National Clinical Key Specialty Construction Project (23003); the Plastic Medicine Research Fund of Chinese Academy of Medical Sciences (2024-ZX-1-01); and the Special Research Fund for Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College (YSZ2024CG007). The funders had no role in study design, data collection and analysis, decision to publish, or manuscript preparation.

## Tables

### Table 1. Principal files and observation units

| File | Rows | Unit and contents |
| --- | ---: | --- |
| authorizations.csv | 1524 | One authorization; submission metadata, retained scope, and clinical-function grouping |
| field_annotations.csv | 9144 | One authorization–field pair; baseline/current codes and assessment state |
| positive_labels.csv | 11120 | One annotation–code membership for the first five fields |
| cohort_snapshot_membership.csv | 1524 | One authorization; original FDA-list row position and primary product code |
| cohort_snapshot_manifest.csv | 3 | One historical snapshot artifact; source, date, size, and fingerprint |
| other_label_notes.csv | 789 | One field carrying OTHER; 206 retained explanations and 583 unseparated contexts |
| evidence_links.csv | 9144 | One annotation-level evidence record; source references, coordinates, and check states |
| source_records.csv | 3173 | One retained retrieval record; source URL, capture metadata, and available hashes |
| version_changes.csv | 16 | One changed cell; eight prior and eight September 8 amendments across four authorizations, including scope |
| associated_source_relationships.csv | 65 | One reviewed annotation–associated-source relationship with caution codes |
| source_bridges.csv | 145 | One field-linked relationship or detail anchor; 43 distinct text locations |
| semantic_review_records.csv | 12 | One targeted authorization–field review; decisions, rationale, and page-level references |
| semantic_review_sources.csv | 6 | One source reference for the targeted review; separate from retained retrieval records |

Each authorization has six field records. Positive memberships are nonexclusive and exclude clinical-function grouping. Source retrieval records can repeat a document, and bridge rows can repeat a text location across fields. One additional alias row links DEN130013 and K124067. Vocabulary, dictionary, validation, code, and source-material archive manifests accompany these tables.

### Table 2. Stored assessment states and positive-label memberships by field

| Field | Coded | Not stated | Not assessable | Uncertain | Positive memberships |
| --- | ---: | ---: | ---: | ---: | ---: |
| Input | 1414 | 7 | 103 | — | 1583 |
| Output | 1421 | 0 | 103 | — | 3009 |
| Intended user | 1319 | 102 | 103 | — | 2027 |
| Setting or use context | 1410 | 11 | 103 | — | 2370 |
| Downstream action | 1406 | 15 | 103 | — | 2131 |
| Clinical-function grouping | 1402 | — | — | 122 | N/A |

Each row covers 1524 authorizations. A dash indicates a state that is inapplicable under the schema. The four state columns are mutually exclusive and sum to 1524 within each field; headers correspond to CODED, NOT_STATED, NOT_ASSESSABLE, and UNCERTAIN. Positive memberships may exceed the coded count because the first five fields allow multiple labels. N/A means grouping is not expanded in positive_labels.csv. Its 1402 coded records comprise 1155 SINGLE and 247 MULTIPLE values. The 122 UNCERTAIN records comprise 103 authorization-level barriers and 19 unresolved groupings within the described-function scope. Field states do not incorporate the separate cross-authorization caution flags, which must also be considered when selecting a reuse subset.

### Table 3. Selected applications of the coding rules

| Authorization | FDA source; physical pages | Retained coding | Interpretation |
| --- | --- | --- | --- |
| K150817, Dario Blood Glucose Monitoring System | K150817.pdf; 5–6 | First five fields: NOT_ASSESSABLE; grouping: UNCERTAIN | The reviewed whole-device description leaves AI attribution unresolved. |
| K182034, Arterys MICA | K182034.pdf; 5–7 | Output: MEASUREMENT_OR_QUANTIFICATION; SEGMENTATION_OR_LOCALIZATION. Grouping: MULTIPLE. | Segmentation and user-editable landmarks and contours support the additional output category. Cardiac and oncology modules retain distinct clinical-function grouping. |
| K190013, WellDoc BlueStar | K190013.pdf; 4, 6, 10 | Scope: AI attribution unresolved. First five fields: NOT_ASSESSABLE. Grouping: UNCERTAIN. | Coaching and prescription-based dose calculation are described at device level. Confirmed coding retains unresolved function-specific AI attribution; earlier device-level labels remain in the version records. |
| K182513, FluChip-8G Influenza A+B Assay | reviews/K182513.pdf; 8–9 | Input: LAB_SPECIMEN_OR_OMICS; output: CLASSIFICATION_OR_DIAGNOSIS; grouping: SINGLE | Internal neural networks contribute to one integrated influenza-classification function. |

The examples illustrate attribution, output-category, and function-grouping decisions in the versioned release. Source URLs, in row order: https://www.accessdata.fda.gov/cdrh_docs/pdf15/K150817.pdf; https://www.accessdata.fda.gov/cdrh_docs/pdf18/K182034.pdf; https://www.accessdata.fda.gov/cdrh_docs/pdf19/K190013.pdf; https://www.accessdata.fda.gov/cdrh_docs/reviews/K182513.pdf. Page numbers count physical PDF pages from one.

## Figure legends

### Figure 1. Data structure and linkage keys

The main annotation tables link by submission_number and annotation_id. Each authorization has six field records; each field has one evidence record and zero or more positive-label memberships, with the latter limited to the first five fields. Evidence and bridge rows contain semicolon-delimited source_record_ids, which are expanded before joining to source_records.csv. The focused cross-authorization review comprises 65 field-level relationships and 145 field-linked bridge anchors. The additional tables in Table 1 link cohort membership by submission number and retained OTHER notes and targeted semantic reviews by annotation identifier. Lines indicate table joins. Counts identify stored rows; source captures and bridge anchors may be shared across fields or authorizations.

### Figure 2. Evidence-location checks and source types

(a) Locator-check outcomes for 9144 field evidence records. Exact anchors comprise 8967 recorded-span matches and 48 matches with added corrected coordinates. The remaining 129 records retain explicit unresolved or unchecked statuses. (b) Source types of the 9015 exact anchors. PDF text accounts for 8939 anchors, FDA HTML for 42, stored web excerpts for 18, and stored image transcriptions for 16. (c) Distributed-file checks and the focused source-association review provide complementary technical checks. Counts refer to field-linked records; a text match evaluates location in the retained text representation. The semantic-review page references are recorded separately from these locator counts.
