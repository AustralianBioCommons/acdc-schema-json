# Methods & Design Rationale — Proteomics & Metabolomics Arm of the ACDC Data Dictionary

*Provenance record for the dictionary repository. Explains what standards and components were used to build the mass-spectrometry proteomics and metabolomics arm of the Baker Heart & Diabetes Institute Gen3 data dictionary (`commons.heartdata.baker.edu.au`), how those choices were discovered and evaluated, and the reasoning behind each decision.*

**Companion document:** the *Implementation Specification* (`acdc_proteomics_metabolomics_implementation_spec.md`) holds the exact properties, enums, and YAML. This document is the "why and how"; that one is the "what to type."

---

## 1. Purpose and scope

This record documents the design of the proteomics and metabolomics extension so that future maintainers and secondary users can understand not just *what* the model contains but *why it is the way it is* — which community standards were adopted, which were deliberately rejected, and what constraints shaped the result.

Scope is **mass-spectrometry (MS) based proteomics and metabolomics** ingestion into an existing clinical cardiovascular Gen3 commons. It covers experimental-method (assay) metadata, data-file metadata, quality-control metrics, controlled vocabularies, and identifiers. It does **not** cover NMR metabolomics (reserved for future work), molecular-interaction or pathway modelling, or the storage of analyte measurements themselves (see §10).

## 2. Starting state — the modelling substrate

**Platform.** The commons uses a Gen3 data dictionary: a graph data model in which each node is a JSON-Schema (draft-04) document, authored as a YAML file, and the whole dictionary is compiled into a single bundled JSON that is deployed to Gen3's submission service (`sheepdog`). Authoring and compilation use the Australian BioCommons `gen3schemadev` toolchain, which also ships a metaschema validator and a business-rule validator.

**Existing graph.** Before this work the commons already had a clinical backbone (`program → project → subject → clinical_descriptor → sample`) and *placeholder* omics nodes: `proteomics_assay`, `metabolomics_assay` (and lipidomics/serum-marker siblings) under `experimental_methods`; `proteomics_file`, `metabolomics_file`, `qc_file` under `data_file`; and an `analysis_workflow` node. These omics nodes were thin — the assays carried little beyond an identifier, a description, an analyte-name array, and release fields, with no instrument, acquisition, chromatography, quantification, identification, or search metadata, and the file nodes had only a handful of format/category/unit fields.

**Annotation conventions already in use.** The dictionary annotates properties with ontology terms via `termDef` (`{term, source, term_id}`) and individual enum values via `enumDef` (`{enumeration, source, term_id}`), drawing on sources such as EFO, HPO, caDSR and DUO, with central controlled vocabularies held in `_definitions.yaml` and reusable term definitions in `_terms.yaml`. The extension was designed to match these conventions exactly.

## 3. Governing design principles

Five constraints, established with the data owners, drove every decision. They are recorded here because they explain choices that would otherwise look arbitrary.

1. **Highly normalised, single-parent graph.** Every node has exactly one required parent link, forming a single deterministic chain: `program → project → subject → clinical_descriptor → sample → {omics}_assay → {omics}_file`. Normalisation is intentional — it minimises the number of places an error can enter.
2. **Submission is a linear waterfall.** Researchers submit one tab-separated sheet per node, top to bottom, each sheet referencing only the `submitter_id` of the sheet directly above it. No sheet points to two parents.
3. **Researchers are not data engineers.** The submitting scientists do not work with JSON or entity-relationship graphs. Consequently the field `description` is the primary user interface, controlled vocabularies must be delivered as sheet dropdowns, and no design may require a submitter to reason about the graph.
4. **Additive and backwards-compatible.** Existing records must continue to validate. New capability is added by new properties, new central enums, and appended enum values — never by removing, renaming, or restructuring existing nodes, and never by adding to any node's `required` array.
5. **Minimal, high-value filtering.** Faceted search is intentionally kept to the major data types and a few high-value categorical fields, rather than exposing every property as a filter.

## 4. Discovery method — how the standards were identified and evaluated

Standards selection followed a three-stage process.

**Stage 1 — Landscape scan (FAIRsharing).** FAIRsharing was used as the entry point to enumerate candidate resources across the three complementary categories that a metadata model needs: controlled vocabularies/ontologies (for entities and allowable values), data formats/models (for structure), and minimum-reporting guidelines (for which fields should exist). This produced an initial candidate list spanning PSI-MS, ChEBI, CHMO, mzML, mzQC, SBML, SDF, MITAB, USI, SPLASH, MIAPE/MIMIx, HPP, MassIVE.quant, OORF, and PIDINST.

**Stage 2 — Primary-source verification.** Each candidate was checked against authoritative primary sources — HUPO Proteomics Standards Initiative (psidev.info), EMBL-EBI resources (PRIDE, MetaboLights, ChEBI, the Ontology Lookup Service), the Metabolomics Workbench, the Metabolomics Standards Initiative literature, and the OBO Foundry — to establish (a) governance and current status, (b) real-world community adoption, and (c) the specific terms, fields, or identifier formats each defines. This stage corrected several first-pass suggestions (see §5).

**Stage 3 — Buildability review (gen3schemadev).** The `gen3schemadev` documentation and source were read directly to ensure the intended additions are expressible and will pass validation. This surfaced the concrete business rules the dictionary is checked against and confirmed the correct authoring idioms (see §9).

**Evaluation criteria.** A candidate was adopted only if it was (i) genuinely community "gold standard" rather than niche or superseded, (ii) applicable to a *clinical cardiovascular* commons ingesting MS data (rather than, say, a regulatory-toxicology or molecular-interaction use case), and (iii) buildable within the Gen3/gen3schemadev constraints and the design principles of §3. Each candidate was assigned one of four verdicts: **MUST-ADOPT**, **SHOULD-ADOPT**, **OPTIONAL/CONTEXTUAL**, or **SKIP**.

## 5. Standards evaluated and verdicts

### 5.1 Controlled vocabularies (the semantic layer)

| Resource | Governance | Verdict | Rationale |
|---|---|---|---|
| **PSI-MS CV** (`MS:` accessions) | HUPO-PSI, CC-BY, actively curated | MUST-ADOPT | The authoritative vocabulary for MS instrument, ionization, mass analyzer, detector, dissociation, acquisition, quantification and QC metrics. It is the vocabulary embedded (as `cvParam`) inside mzML/mzIdentML/mzTab, so aligning to it makes the model interoperable with the entire MS tool ecosystem. |
| **ChEBI** (`CHEBI:` accessions) | EMBL-EBI, OBO Foundry | MUST-ADOPT | The default reference for small-molecule/metabolite identity, providing stable IDs and a chemical hierarchy. Used alongside structure anchors (InChIKey) for compound identification. |
| **CHMO** (Chemical Methods Ontology) | RSC / OBO Foundry | MUST-ADOPT (methods) | Correct source for chromatography and sample-preparation/extraction method terms (LC, GC, HILIC, reversed-phase), complementing PSI-MS which does not cover separation chemistry in depth. |
| **UO** (Units of Measurement Ontology) | OBO Foundry | MUST-ADOPT (units) | The single authority chosen for quantification units, so unit vocabulary does not diverge across the model. |
| **UBERON / Cell Ontology** | OBO Foundry | ADOPTED (specimen) | Anatomy/biofluid and cell-type terms for the specimen (`sample_type`) vocabulary; see §7.3. |

### 5.2 Data formats and models (structure)

| Resource | Status | Verdict | Rationale |
|---|---|---|---|
| **mzML** (v1.1.0) | HUPO-PSI, stable | MUST-ADOPT (format) | The community standard for raw/spectral MS data; its element model (instrument configuration, run, spectrum, scan, chromatogram, software, data processing) informed which acquisition metadata to capture. Added as a data-format value. |
| **mzIdentML** (v1.3.0) | HUPO-PSI | MUST-ADOPT (format) | Standard for peptide/protein identifications, search parameters, scores and FDR. Added as a proteomics format value. |
| **mzTab / mzTab-M** (2.0) | HUPO-PSI / Metabolomics Society | MUST-ADOPT (format) | Final results tables for proteomics (mzTab) and metabolomics (mzTab-M); the natural home for per-feature quantification and identification. Added as format values. |
| **SDRF-Proteomics / MAGE-TAB-Proteomics** | Ratified PSI spec (2023) | MUST-ADOPT (field model) | The current gold standard for sample-to-data experimental-design metadata, expressed as ontology-encoded columns. Because it maps samples to data files, it is the closest analogue to a Gen3 sample→assay→file dictionary and was used as the template for which assay-level fields to define. |
| **SBML** | Widely used (pathways) | SKIP | Represents biochemical reactions/pathways — a biological-interpretation layer outside assay ingestion. |
| **SDF** | Chemical structure format | SKIP | Compound structure representation; per-compound identity is handled by ChEBI/InChIKey and the mzTab-M results file, not a schema format. |
| **MITAB** | Molecular interactions (PSI-MI) | SKIP | Molecular-interaction tabular format; out of scope for MS assay ingestion. |

### 5.3 Reporting / minimum-information guidelines (required-vs-optional fields)

| Resource | Status | Verdict | Rationale |
|---|---|---|---|
| **MSI identification confidence levels** (Sumner 2007; Schymanski 2014) | Metabolomics Standards Initiative | MUST-ADOPT | The single most important metabolomics-specific metadata field — records how confidently a metabolite was identified (Level 1 confirmed → Level 4/5 unknown). Encoded as a controlled enum. |
| **HUPO HPP MS Data Interpretation Guidelines 3.0** (Deutsch 2019) | HUPO Human Proteome Project | OPTIONAL/CONTEXTUAL | These are *data-interpretation stringency* rules (≤1% protein-level FDR; ≥2 unique peptides ≥9 aa; USIs for novel-protein claims), not a metadata schema. Encoded indirectly as FDR-threshold and peptide-count fields rather than imported wholesale. |
| **MIAPE** (Minimum Information About a Proteomics Experiment) | HUPO-PSI, ~2007 | SKIP as a schema driver | Never formally retired but effectively superseded in practice by SDRF-Proteomics plus CV-annotated file formats; its *field intent* is captured via SDRF, but the checklist itself is legacy. |
| **MIMIx** (molecular-interaction MI) | HUPO-PSI | SKIP | Molecular-interaction scope; not applicable to MS proteomics/metabolomics assay ingestion. |
| **OECD Omics Reporting Framework (OORF / TRF+MRF)** | OECD EAGMST | SKIP (out of scope) | A real and active framework, but scoped to *regulatory toxicology* (chemical risk assessment, read-across, points of departure) — not clinical cardiovascular research. Recorded here so its exclusion is understood as deliberate, not an oversight. |
| **MassIVE.quant** | Community (quantitative MS) | OPTIONAL/CONTEXTUAL | Useful expectations for quantitative dataset reporting; folded into the quantification-method and abundance-measure fields rather than adopted as a distinct artifact. |

### 5.4 Identifiers

| Identifier | Format | Verdict | Rationale |
|---|---|---|---|
| **USI** (Universal Spectrum Identifier) | `mzspec:<collection>:<run>:<index>` | SHOULD-ADOPT (proteomics) | PSI-ratified, repository-resolvable pointer to an individual spectrum; supports reproducibility and novel-identification evidence. |
| **SPLASH** | `splash10-…` | OPTIONAL (metabolomics) | Database-independent hashed spectral identifier; useful for spectral deduplication/matching. |
| **ProteomeXchange (PXD)** | `PXD` + 6 digits | SHOULD-ADOPT | Dataset accession for proteomics data deposited to the PX consortium. |
| **MetaboLights (MTBLS) / Metabolomics Workbench (ST)** | `MTBLS…` / `ST######` | SHOULD-ADOPT (metabolomics) | Repository/study accessions for deposited metabolomics data (PXD is proteomics-only, so these are kept separate). |
| **ChEBI ID / InChIKey** | `CHEBI:…` / 27-char key | ADOPTED (compound identity) | Recorded per identified metabolite; InChIKey is the preferred structure anchor across databases. |

### 5.5 Quality control and instruments

| Resource | Status | Verdict | Rationale |
|---|---|---|---|
| **mzQC + PSI QC-CV** (v1.0.0, 2024; `MS:4000xxx`) | HUPO-PSI | SHOULD-ADOPT (selected metrics) | Standard QC metric definitions (spectrum counts, acquisition ranges, chromatography duration, identification counts, mass accuracy) applied to `qc_file`. |
| **PIDINST / RRID** | RDA / SciCrunch | OPTIONAL/CONTEXTUAL | Persistent instrument identifiers; full PIDINST is over-engineered for a clinical commons today, so instrument manufacturer/model/serial/RRID are captured as simple fields instead. |

### 5.6 Where the initial landscape scan was off

Three corrections from Stage 2 are worth recording, because they are the non-obvious calls a reviewer would probe: **SBML, SDF and MITAB** target pathways, chemical structures and molecular interactions respectively and are out of scope for MS assay ingestion; **MIAPE** is best treated as legacy and realised through SDRF rather than imported as a checklist; and **OORF** is a regulatory-toxicology framework, not a clinical-omics reporting standard. FAIRsharing surfaced all of these as candidates; primary-source review filtered them out.

## 6. Translating standards into the graph — architectural decisions

**Method vs payload vs quality separation.** The extension preserves and deepens a clean three-way split that maps naturally onto the PSI standards and onto the existing graph:

- **`{omics}_assay` = the method (and the batch).** All instrument, ionization, analyzer, detector, dissociation, acquisition, chromatography, sample-prep, quantification, identification and search-parameter metadata live here. This is where the bulk of the new fields were added.
- **`{omics}_file` = the payload.** Format, category, units/abundance measure, value semantics, and dataset/spectrum identifiers.
- **`qc_file` = the quality report.** Run-level QC metrics.

**The assay is the batch.** Because a single assay record describes a processing batch and links to all of its samples, "group by assay" is the batch key. This was a deliberate, load-bearing decision: batch effects are the dominant confounder in omics machine learning, so every data point must be unambiguously traceable to its batch. The graph guarantees this by construction (the file→assay link is required), and no separate `batch_id` field is introduced because it would duplicate the assay identity.

**Participant identity by traversal, not by shortcut.** A data file is tied back to its participant by traversing the existing single chain — `file → assay → sample → clinical_descriptor → subject` — which returns exactly the participant whose material is in the file. No `file → sample` shortcut link and no hand-typed participant-ID field were added: either would give the file a second parent (violating the single-parent/linear-waterfall principles) and duplicate information the traversal already provides, adding an error source for no gain. This decision reversed an earlier draft that had proposed such a link; the normalised chain makes it unnecessary.

**Summarised / participant-level data.** Some submissions are summarised tables where one file holds one participant's values. These use the *same* linear chain (each participant gets their own `sample → assay → file` rows); the only additions are file-level *value-semantics* fields describing how to read the table (granularity, abundance measure, normalization, transformation, feature count, missing-value encoding) and a `summarised results` data-category flag. Analyte values themselves remain inside files (see §10).

## 7. Cross-cutting schema-design decisions

### 7.1 Additive-only; requirements expressed without breaking existing data

No node's `required` array is modified, because adding a required field would reject every pre-existing record. Community "must-report" expectations are instead conveyed through (a) the field `description`, (b) a reporting-tier convention (Required-by-standard / Strongly-recommended / Optional) surfaced to submitters, (c) Gen3's native `preferred` block for important-but-non-blocking fields, and (d) a submission-time validation profile *conditioned on `data_category`*, so that summarised-results submissions are not forced to supply acquisition metadata that does not exist for them. This keeps hard enforcement out of the schema and in the submission layer, where it can be data-shape-aware.

### 7.2 Ontology codes are not embedded in the dictionary (one exception)

A deliberate decision was made **not** to bake ontology accession codes (`enumDef`/`termDef` `source`+`term_id`) into `_definitions.yaml` for most fields. Instead, fields are plain enums or strings, and their `description` links to the resolver (EBI OLS4 for PSI-MS, ChEBI, CHMO, UO) so a submitter or curator can look up — or `grep` — the exact term themselves. The rationale: it keeps the definition files lean, avoids pinning brittle, version-dependent accession numbers into the schema, and keeps maintenance low for a non-technical audience. This is why the accompanying research recorded a "verified vs verify-in-OLS4" split rather than hard-coding every accession.

**The single exception is `enum_sample_type`.** Specimen type is a stable, high-value filter for a cardiovascular commons (plasma vs serum materially changes the proteome and metabolome), so its terms are pinned with full `enumDef` ontology backing (UBERON, Cell Ontology, ChEBI, and PSI-MS specimen terms). Because these codes now render in the data-dictionary viewer, the mapping should be verified in OLS4 before deployment.

### 7.3 Controlled vocabularies as human-readable enums delivered via dropdowns

Enum values are stored as human-readable labels (e.g. `data-independent acquisition`, `orbitrap`, `plasma`) rather than codes. This aids the researcher reading the dictionary and keeps values consistent. Because exact-match validation on verbose labels is error-prone for hand-typed sheets, the intended delivery is a templated data-entry sheet with dropdowns (e.g. DataHarmonizer or the gen3schemadev sheet templates), which turns the controlled vocabulary from a source of friction into a guided pick-list. This is a consequence of design principle 3.

### 7.4 Specimen vocabulary (`sample_type`)

The pre-existing free-text `sample_type` was converted to a controlled enum spanning blood and derivatives, tissue, cell-based materials, nucleic acids, protein/peptide preparations, biofluids, other biological materials, derived systems (organoid/xenograft) and extracellular vesicles, each mapped to a source ontology term. Two safety values (`other`, `not_reported`) were added to preserve submitter flexibility and limit breakage of legacy free-text values. This is the **only** property in the extension whose *type* changes (free-text → enum); existing values must be mapped before deployment.

## 8. Components added (inventory)

At a high level, the extension introduces:

- **Ontology resolvers** cited in descriptions (PSI-MS, CHMO, ChEBI, UO; UBERON/CL for specimen) — pointers, not embedded codes (except `enum_sample_type`).
- **Assay-level method properties** (~25–30 per assay): instrument model/manufacturer/serial/RRID; ionization; mass analyzer; detector; dissociation; acquisition mode; chromatography type/instrument/column; digestion enzyme (proteomics); labelling and quantification method; search engine and version; sequence database and version; fixed/variable modifications; precursor/fragment mass tolerances; PSM/peptide/protein FDR thresholds; fractionation; plus metabolomics-specific ionization polarity, extraction/derivatization, internal standards, retention-index flag, reference database, MSI identification-confidence level, and compound-identity arrays (ChEBI IDs, InChIKeys, RefMet names).
- **File-level fields**: expanded data-format enums (adding mzML, mzXML, mzTab, mzTab-M, mzIdentML, raw/vendor and tabular formats); dataset/spectrum identifiers (USI, SPLASH, PXD, MTBLS, ST); and value-semantics fields for summarised data (granularity, abundance measure, normalization, transformation, feature count, missing-value encoding).
- **QC metrics** on `qc_file` aligned to the PSI QC-CV (spectrum counts, acquisition ranges, chromatography duration, identification counts, mass accuracy, missed-cleavage rate, overall status).
- **New central enums** in `_definitions.yaml` for each controlled field above, plus `enum_sample_type`, `enum_file_granularity`, `enum_abundance_measure`, `enum_transformation` and `enum_qc_metric_status`.

The Implementation Specification holds the exact property names, types, descriptions, and YAML.

## 9. Conformance and validation

The additions were checked against the two validators shipped with `gen3schemadev` and the design principles.

**Metaschema (GDC-derived).** Confirms node structure and property shape. Relevant constraints honoured: enum values are strings; `type`/`enum`/`$ref` present on every property; links carry all six required keys (`name, backref, label, target_type, multiplicity, required`) with alphanumeric/underscore names and a non-empty `label`; `category` values are from the allowed set (no new node categories were introduced).

**Rule validator (business rules).** The additions satisfy: every `data_file` node keeps its required `core_metadata_collections` link and its `data_type`/`data_format`/`data_category` properties; every link name has a matching property; array properties include `items`; no property uses a reserved system name (`id, project_id, type, submitter_id, state, created_datetime, updated_datetime, file_state, error_type, label`); and enum-backed properties use the documented `{description, $ref}` idiom (which the validator explicitly skips for the type check).

**A specific hazard handled.** The toolchain's `find_null_descriptions` check fails resolved-node metaschema validation on any `description: null` in `_definitions.yaml`. Every new and extended enum therefore carries a real description string — which doubly serves the "description is the UI" principle.

**Authoring workflow.** The deployed dictionary is a *compiled bundle*; edits are made in the per-node source YAML and `_definitions.yaml`/`_terms.yaml`, then recompiled and run through the metaschema and rule validators before deployment to `sheepdog`. The bundle JSON is not hand-edited as the source of truth.

## 10. Caveats, limitations and future work

- **Accession verification.** For fields kept code-free this is deferred to the submitter/curator by design. For `enum_sample_type`, whose codes are embedded and rendered in the viewer, the mapping (especially the PSI-MS specimen terms and cell-level UBERON/CL choices) should be confirmed in OLS4 before deployment.
- **One type change.** `sample_type` moves from free-text to enum; legacy values must be mapped first. Everything else is purely additive.
- **Metadata, not measurements.** The commons stores files plus metadata about them; faceted filters range over file/assay/subject metadata, never over the analyte values inside files. A summarised cohort-matrix file's individual values are not queryable at the graph level. Expectations for secondary users should be set accordingly.
- **Per-compound identity.** Metabolite identifiers are recorded as arrays on the assay for provenance; the authoritative per-feature identity and quantity live in the mzTab-M results file. If per-compound identity ever needs to be *queryable/filterable*, an additive per-metabolite child node would be the appropriate future extension.
- **NMR out of scope.** Metabolomics is modelled MS-first; an `nmrML` format value is reserved but the analyzer/acquisition vocabularies would need an NMR branch if NMR data is later ingested.
- **Delivery mechanism.** The controlled-vocabulary approach depends on a dropdown-driven submission template (design principle 3); building that template is a recommended follow-on and is independent of the dictionary itself.
- **Deposition vs reference.** Identifier fields (PXD, MTBLS, ST, USI) assume datasets are *referenced*; if the commons later *deposits* to these repositories, SDRF-Proteomics would move from a field-design template to a required export artifact.

## 11. Primary sources consulted

Authoritative sources used in Stage 2 verification (bibliographic references for the archive):

- HUPO Proteomics Standards Initiative — PSI-MS CV, mzML, mzIdentML, mzTab, mzQC, SDRF-Proteomics specifications (psidev.info; HUPO-PSI GitHub).
- EMBL-EBI — PRIDE / ProteomeXchange, MetaboLights, ChEBI, and the Ontology Lookup Service (OLS4).
- Metabolomics Workbench (RefMet, mwTab, study accessions) and the Metabolomics Society / MSI.
- OBO Foundry — ChEBI, CHMO, UO, UBERON, Cell Ontology.
- Sumner L.W. *et al.* (2007), "Proposed minimum reporting standards for chemical analysis," *Metabolomics* 3:211–221 — MSI identification levels.
- Schymanski E.L. *et al.* (2014), *Environ. Sci. Technol.* 48:2097–2098 — high-resolution MS identification confidence levels.
- Deutsch E.W. *et al.* (2019), "Human Proteome Project MS Data Interpretation Guidelines 3.0," *J. Proteome Res.* 18:4108–4116.
- Deutsch E.W. *et al.* (2021), "Universal Spectrum Identifier," *Nature Methods*.
- Wohlgemuth G. *et al.* (2016), "SPLASH, a hashed identifier for mass spectra," *Nature Biotechnology*.
- Hoffmann N. *et al.* (2019), "mzTab-M," *Anal. Chem.* 91:3302–3310.
- Australian BioCommons — `gen3schemadev` documentation, metaschema, and rule validator (source of the buildability constraints in §9).
- FAIRsharing.org — used for the Stage 1 landscape scan.

## 12. Provenance of this document

This design was produced by: (1) a FAIRsharing-seeded landscape scan of candidate standards; (2) verification of each candidate against the primary sources listed in §11, yielding the adopt/reject verdicts in §5; (3) a review of the existing ACDC dictionary structure and conventions; and (4) a read of the `gen3schemadev` documentation and source to guarantee the additions are buildable and validator-clean. Design decisions were refined in consultation with the data owners around the governing principles in §3 — in particular the normalised single-parent graph, the assay-as-batch model, and the treatment of ontology codes.

*This document should be updated if the standards landscape shifts materially (e.g. new PSI specifications), if NMR metabolomics enters scope, or if the commons begins depositing rather than referencing external datasets.*
