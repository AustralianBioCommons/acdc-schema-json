# ACDC Data Dictionary

The Gen3 data dictionary for the Australian Cardiovascular Disease Commons
([commons.heartdata.baker.edu.au](https://commons.heartdata.baker.edu.au)).

- [Node schemas](dictionary/prod_dict/)
- [Bundled schema](dictionary/prod_dict/acdc_schema.json) — the file Gen3 actually loads

---

## Where the source of truth is

**The Gen3 node YAMLs in `dictionary/prod_dict/` are the source of truth, and they are edited by
hand.** So is `_definitions.yaml`, which holds the controlled vocabularies.

This repository is *schema-first*. There is no input file that the dictionary is generated from —
you edit the node schemas directly, then validate and re-bundle. That is a deliberate choice: the
model uses Gen3 features the simplified input language cannot express, including per-link
requirements, multiple parents on the file nodes, and ontology-annotated enums.

### Do not run `gen3schemadev generate` here

There is nothing to generate from, and it would do real damage. This repository used to carry a
`dictionary/input_dd.yaml`, and by the time it was removed it had been frozen for eight months while
the dictionary moved on across 29 commits. Regenerating from it would have:

- destroyed **343 of 448 properties** — `proteomics_assay` would drop from 37 to 2
- wiped every custom enum definition from `_definitions.yaml`, leaving dangling `$ref`s across the
  node files
- dropped links, including the extra parents on `qc_file`, `supplementary_file` and
  `analysis_workflow`
- replaced `project.yaml` and `program.yaml` with a generic template, losing the `systemProperties`
  and `uniqueKeys` Gen3 needs — which breaks submission outright

The pinned `gen3schemadev` is 3.1.0, which refuses to overwrite existing files by default, so this
is now hard to do by accident. Understanding why still matters.

`gen3schemadev` is used here for three things only: **`validate`**, **`bundle`** and **`visualise`**.

---

## Repository layout

| Path | What it is | Edit by hand? |
| --- | --- | --- |
| `dictionary/prod_dict/*.yaml` | The node schemas — the data model | **Yes — this is the source** |
| `dictionary/prod_dict/_definitions.yaml` | Shared definitions and controlled vocabularies | **Yes** |
| `dictionary/prod_dict/_terms.yaml`, `_settings.yaml` | Gen3 framework files; `_settings.yaml` holds the dictionary version | `_settings.yaml` only, to set the version |
| `dictionary/prod_dict/acdc_schema.json` | The bundled schema Gen3 loads | No — produced by `bundle` |
| `docs/` | Design rationale and methods | Yes |

`dictionary/prod_dict/` and `acdc_schema.json` are fetched by the deployment pipeline at those exact
paths, so **neither may be renamed** — see [Deployment](#deployment).

---

## Making a change

Install first: `pip install poetry && poetry install`, then either `eval $(poetry env activate)` or
prefix commands with `poetry run`. All commands run from the repository root.

**1. Branch.**

```bash
git switch main && git pull
git switch -c feat/describe-your-change
```

**2. Edit the node schema** in `dictionary/prod_dict/`. For the format — descriptors, links,
properties — see the
[Gen3 data modelling docs](https://github.com/AustralianBioCommons/gen3schemadev/tree/main/docs/gen3_data_modelling).
Those pages describe exactly what this repository maintains by hand.

**3. Validate.** Must exit 0.

```bash
poetry run gen3schemadev validate -y dictionary/prod_dict
```

**4. Re-bundle.** The bundle is generated, so it must be rebuilt whenever a schema changes.

```bash
poetry run gen3schemadev bundle -i dictionary/prod_dict -f dictionary/prod_dict/acdc_schema.json
```

**5. Validate the bundle too.**

```bash
poetry run gen3schemadev validate -b dictionary/prod_dict/acdc_schema.json
```

**6. Visualise (optional).** Requires Docker Compose; opens the model graph at `localhost:8080`.

```bash
poetry run gen3schemadev visualise -i dictionary/prod_dict/acdc_schema.json
```

**7. Commit and open a pull request.** The changed schema and the rebuilt `acdc_schema.json` belong
in the same commit, so the bundle never lags the model. CI checks both.

### Adding a node

Create `dictionary/prod_dict/<node>.yaml` following the shape of an existing node of the same
category, then add the node to its parents' `links` blocks, and add a matching link property under
`properties`. Validate — the rule checks will tell you if a link has no corresponding property, or
if a `data_file` node is missing its `core_metadata_collection` link.

### Adding or changing an enum

Controlled vocabularies live in `dictionary/prod_dict/_definitions.yaml` as `enum_*` entries. Add
the values under `enum`, and where the terms come from an ontology record the provenance in
`enumDef` with `source` and `term_id`. Reference it from a property with
`$ref: _definitions.yaml#/enum_<name>`.

**Removing an enum value is a breaking change** — data already submitted with that value stops
validating. Adding values is safe.

---

## Continuous integration

`.github/workflows/validate.yaml` runs on pull requests and pushes to `main`:

- **schemas are valid Gen3** — metaschema and business-rule validation over `dictionary/prod_dict`
- **the bundle is valid** — the same validation against `acdc_schema.json`, which is what actually
  gets deployed
- **the bundle is up to date** — rebuilt and compared, so a branch cannot change a schema and forget
  to re-bundle
- **the version is consistent** between `_settings.yaml` and `pyproject.toml`

There is deliberately no "matches its input" check — there is no input.

---

## Versioning

`_dict_version` in `dictionary/prod_dict/_settings.yaml` is the canonical dictionary version. Edit it
by hand when preparing a release, and match `pyproject.toml` and the git tag to it.

Bump it against **submitted data**: patch for descriptions and comments; minor for new nodes,
optional properties or enum values; major for anything that stops previously valid data from
validating, such as removing a property or an enum value.

---

## Deployment

Merging deploys nothing. The pipeline in
[`acdc-aws-etl-pipeline`](https://github.com/AustralianBioCommons/acdc-aws-etl-pipeline) fetches the
bundled schema **by git tag**:

```
https://raw.githubusercontent.com/AustralianBioCommons/acdc-schema-json/refs/tags/<tag>/dictionary/prod_dict/acdc_schema.json
```

So the release loop is:

1. **Tag this repository** — e.g. `v1.2.0`, matching `_dict_version`
2. **Bump `dictionary_version`** in `acdc-aws-etl-pipeline/config/deploy_config.yaml` for the target
   environment. Environments are pinned independently and can sit on different versions
3. **Run** that repository's `services/dictionary/deploy_dd.sh`

Because the tag and the path both appear in that URL, `dictionary/prod_dict/` and `acdc_schema.json`
are an external contract. Renaming either breaks deployment silently.

---

## Documentation

- [Proteomics and metabolomics methods and rationale](docs/acdc_proteomics_metabolomics_methods_and_rationale.md)
  — standards review and design decisions behind the mass-spectrometry arm of the model
- [Gen3 data modelling](https://github.com/AustralianBioCommons/gen3schemadev/tree/main/docs/gen3_data_modelling)
  — the node schema format: descriptors, links, properties
- [Running a Gen3 dictionary repository](https://github.com/AustralianBioCommons/gen3schemadev/blob/main/docs/gen3schemadev/dictionary_repo.md)
  — how schema-first repositories like this one are meant to work
