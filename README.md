# ACDC Data Dictionary
This is the Gen3 data dictionary for the Australian Cardiovascular Disease Project.

The yamls and jsonschema is found in the `dictionary/prod_dict` folder.
- [yamls](dictionary/prod_dict/)
- [jsonschema](dictionary/prod_dict/acdc_schema.json)

## Development Workflow

This repository includes a `dictionary/test_dict` folder for testing purposes. You can convert the `input_dd.yaml` into jsonschema files without overwriting anything in the `dictionary/prod_dict` folder:

1. Use the `dictionary/test_dict` folder to generate and validate your schema changes
2. Copy specific elements from `dictionary/test_dict` to `dictionary/prod_dict` as needed
3. The `dictionary/prod_dict/acdc_schema.json` file is what will be used for deployment

### Copying Files Between Folders

To copy files between the test and production folders, you can use the provided scripts:

- Copy from test to production:
  ```bash
  bash dictionary/copy_to_prod.sh
  ```

- Copy from production to test:
  ```bash
  bash dictionary/copy_to_test.sh
  ```

## Using Gen3SchemaDev's Simplified YAML Input

The data model can be defined using Gen3SchemaDev's simplified YAML input language via the `input_dd.yaml` file. This approach is particularly useful for:
- Creating the main structure of the data model
- Defining links between nodes in a more readable format

For more information, see the [Gen3SchemaDev README](https://github.com/AustralianBioCommons/gen3schemadev).

## Updating the Dictionary

1. Copy prod_dict to test_dict
   ```bash
   bash dictionary/copy_to_test.sh
   ```

When making changes to the data dictionary:

2. Update the dictionary version in the `dictionary/test_dict/_settings.yaml` file
3. Bundle the schema using:
   ```bash
   gen3schemadev bundle -i dictionary/test_dict -f dictionary/test_dict/acdc_schema.json
   ```

## Validating the Dictionary

4. To validate a folder of jsonschema YAML files, use:
```bash
gen3schemadev validate -y dictionary/test_dict
gen3schemadev validate -b dictionary/test_dict/acdc_schema.json
```

For more details, see the [Gen3SchemaDev validation documentation](https://github.com/AustralianBioCommons/gen3schemadev).

## To visualise the dictionary
5. The dictionary can be visualised using [Gen3SchemaDev](https://github.com/AustralianBioCommons/gen3schemadev/blob/main/docs/gen3schemadev/quickstart.md).
```bash
gen3schemadev visualise -i dictionary/test_dict/acdc_schema.json
```

## Copying back to the prod folder
6. After validating and visualising the dictionary, copy it back to the prod folder:
```bash
bash dictionary/copy_to_prod.sh
```
- Then commit and push the changes to github