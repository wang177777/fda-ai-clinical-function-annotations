# Operational coding rules — English explanation of retained definitions

These rules define the six annotation fields and their coding boundaries. Clinical-function interpretation, source attribution, and evidence locators are recorded for each authorization. Amendments are versioned separately from the initial baseline. Counts refer to authorizations.

## Unit and evidence boundaries

One record corresponds to one FDA submission-level authorization. Eligible evidence is FDA-hosted or FDA-linked public material. Manufacturer-only contextual supplementation does not alter FDA-only primary codes.

The first five fields are nonexclusive label sets. Each positive code requires supporting source content. Direct AI/algorithm input is distinguished from the whole system's initial specimen or acquisition hardware. Descriptions that cannot be attributed to the AI-related function retain device-level scope and do not become positive AI-specific labels. Internal features or probabilities are not automatically promoted to user-facing clinical outputs.

## Input

- `MEDICAL_IMAGE`: patient or clinical-specimen images, including CT, MR, microscopy, fundus images, intraoral scans, and clinical test-strip images.
- `PHYSIOLOGICAL_SIGNAL`: measured physiological sequences, such as ECG, EEG, PPG, respiratory signals, or continuous glucose measurements.
- `LAB_SPECIMEN_OR_OMICS`: molecular/laboratory analytical data such as genotype, sequencing-derived variants, expression profiles, or protein spectra. The direct molecular microarray signal is the relevant input for the FluChip-8G amendment; the whole-system swab is not substituted for that input.
- `CLINICAL_TABULAR_OR_TEXT`: EHR variables, questionnaires, manually annotated timing or cell parameters, clinical logs, or derived state tables.
- `AUDIO_OR_VIDEO`: audio or video directly read by the algorithm; clinical video is separated from static images in this codebook.
- `DEVICE_TELEMETRY_OR_OPERATIONAL`: device or therapy logs and operating parameters.
- `MULTIMODAL`: explicitly documented fusion of different modalities in the same analysis; separate functions using separate modalities do not automatically establish fusion.
- `OTHER`: a specifically described input not suitably covered above; the original detail states the input (for example, an optical spectrum).

## Output

The retained output codes distinguish detection/alert, classification/diagnosis, segmentation/localization, measurement/quantification, risk score/prediction, reconstruction/enhancement, recommendation/planning, control/automation, documentation/summary, and other explicitly described output. Code strings use uppercase words joined by underscores, as shown in the data.

An output can legitimately receive multiple supported labels, for example detection and localization. `CLASSIFICATION_OR_DIAGNOSIS` includes classification; it does not by itself establish authorization for autonomous diagnosis. A similarity or measurement score is not relabeled as a clinical risk merely because it is numeric. User-facing output includes downstream results explicitly connected to the AI/algorithmic function, not every internal quantity.

## Intended user

The retained labels are `RADIOLOGIST`, `OTHER_PHYSICIAN`, `OTHER_CLINICIAN`, `LABORATORY_PROFESSIONAL`, `TECHNOLOGIST_OR_OPERATOR`, `PATIENT_OR_CAREGIVER`, and `OTHER`. Generic healthcare-professional language is not assigned an unsupported specialty. Distinct explicitly supported user labels may co-occur. Validation-study readers are not automatically intended users; patient participation in acquisition does not establish responsibility for a clinical decision.

## Setting or use context

The retained labels are `SCREENING`, `DIAGNOSTIC_INTERPRETATION`, `ACUTE_TRIAGE_OR_EMERGENCY`, `PROCEDURAL_OR_OPERATING_ROOM`, `INPATIENT`, `OUTPATIENT`, `LABORATORY`, `MONITORING`, `HOME_OR_CONSUMER`, and `OTHER`.

Screening, monitoring, and interpretation are clinical contexts, not physical locations. `HOME_OR_CONSUMER` can include over-the-counter nonclinical use and must not be summarized exclusively as home use. `PROCEDURAL_OR_OPERATING_ROOM` can include procedural planning and does not establish that every such device operates inside an operating room. A hospital location alone is not sufficient for `INPATIENT`.

## Downstream action

The retained labels are `INTERPRETATION_OR_DIAGNOSIS`, `TRIAGE_OR_PRIORITIZATION`, `MONITORING_OR_FOLLOW_UP`, `REFERRAL_OR_ESCALATION`, `TREATMENT_OR_PROCEDURE_PLANNING`, `THERAPY_DOSE_OR_DEVICE_CONTROL`, `WORKFLOW_OR_DOCUMENTATION`, `PATIENT_SELF_MANAGEMENT`, and `OTHER`.

The action must be explicitly connected to the output or described use. A risk score does not by itself imply treatment. Optional consultation is not converted into required referral. Planning or a recommended parameter change is not autonomous execution. `THERAPY_DOSE_OR_DEVICE_CONTROL` may describe clinician-mediated changes or automatic device control; the retained detail distinguishes them, so the marginal category cannot be interpreted as a count of autonomous therapy.

## Clinical function grouping

- `SINGLE`: one described clinical AI-related function. Internal ensemble members, views, indicators, targets, or software components do not each create another function.
- `MULTIPLE`: the source supports distinguishable clinical functions. This is not a claim that all internal models or components have been enumerated.
- `UNCERTAIN`: the source cannot resolve clinical function grouping or AI attribution. Unknown internal model count alone does not justify this code.

For FluChip-8G, seven internal networks serve an integrated influenza classification function; this meets the retained `SINGLE` rule.

## Source-limited codes and scope

- `NOT_STATED`: the reviewed eligible passage does not specify the particular field, such as a source naming only patient-specific data without a modality.
- `NOT_ASSESSABLE`: source insufficiency or unresolved AI-function attribution prevents classification. Positive whole-device descriptions are preserved separately and do not establish AI-specific content.
- `UNCERTAIN`: unresolved clinical function grouping, as defined above.

These are substantive coding outcomes rather than blank cells; no negative clinical conclusion is implied. A contextual quotation identifies the source boundary, not proof of absence throughout a confidential regulatory file. Source scope is `DESCRIBED_AI_OR_ALGORITHMIC_FUNCTION`, `DEVICE_FUNCTION_AI_ATTRIBUTION_UNRESOLVED`, or `SOURCE_INSUFFICIENT`.

## Authorization-level interpretation

The first five fields contain authorization-level label sets. Co-occurring labels describe content present in the same authorization; they do not identify component-level input–output–action chains. Function grouping and source-attribution records provide the context needed to interpret these sets.
