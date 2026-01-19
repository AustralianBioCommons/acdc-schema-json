# ACDC Data Dictionary
This is the Gen3 data dictionary for the Australian Cardiovascular Disease Project.

The yamls and jsonschema is found in the `dictionary/prod_dict` folder.
- [yamls](dictionary/prod_dict/)
- [jsonschema](dictionary/prod_dict/acdc_schema.json)

## To visualise the dictionary
The dictionary can be visualised using [Gen3SchemaDev](https://github.com/AustralianBioCommons/gen3schemadev/blob/main/docs/gen3schemadev/quickstart.md).

## Using Gen3SchemaDev's Simplified YAML Input

The data model can be defined using Gen3SchemaDev's simplified YAML input language via the `input_dd.yaml` file. This approach is particularly useful for:
- Creating the main structure of the data model
- Defining links between nodes in a more readable format

For more information, see the [Gen3SchemaDev README](https://github.com/AustralianBioCommons/gen3schemadev).

### Development Workflow

This repository includes a `dictionary/test_dict` folder for testing purposes. You can convert the `input_dd.yaml` into jsonschema files without overwriting anything in the `dictionary/prod_dict` folder:

1. Use the `dictionary/test_dict` folder to generate and validate your schema changes
2. Copy specific elements from `dictionary/test_dict` to `dictionary/prod_dict` as needed
3. The `dictionary/prod_dict/acdc_schema.json` file is what will be used for deployment

### Updating the Dictionary

When making changes to the data dictionary:

1. Update the dictionary version in the `dictionary/prod_dict/_settings.yaml` file
2. Bundle the schema using:
   ```bash
   gen3schemadev bundle -i dictionary/prod_dict -f dictionary/prod_dict/acdc_schema.json
   ```
