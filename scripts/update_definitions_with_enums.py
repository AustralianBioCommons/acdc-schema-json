# This script reads a csv file containing information about enums, then adds them onto the specified
# definitions file so that it can be referenced by the schema.

import pandas
import math
from gen3schemadev.utils import load_yaml, write_yaml

enum_df = pandas.read_csv("dictionary/enums/acdc_enum_definitions.csv")
enum_to_pull_list = enum_df['type_name'].unique().tolist()


def check_null(value):
    """
    Returns True if the input is considered 'null' or missing, otherwise False.
    Considers None, NaN, certain string representations, and empty collections as null.
    """
    import math

    # Check for None
    if value is None:
        return True

    # Check for NaN (float or pandas/numpy nan)
    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except Exception:
        pass

    # Check for string representations of "null"
    if isinstance(value, str):
        null_strs = {
            "", "null", "none", "nan", "n/a", "na",
            "not available", "not applicable", "missing"
        }
        if value.strip().lower() in null_strs:
            return True

    # Check for empty collections
    if isinstance(value, (list, tuple, set, dict)):
        if len(value) == 0:
            return True

    return False

def pull_enum(df, enum_name: str):
    result_df = df[df['type_name'] == enum_name]
    return result_df

def col_to_list(df, colname):
    return df[colname].tolist()

def get_enum_list(df, enum_name: str):
    result_df = pull_enum(df, enum_name)
    return col_to_list(result_df, "enum")

def get_enum_definition(df, enum_name: str, enum_term: str):
    result_df = pull_enum(df, enum_name)
    return result_df[result_df['enum'] == enum_term]['enum_definition'].iloc[0]

def get_enum_source(df, enum_name: str, enum_term: str):
    result_df = pull_enum(df, enum_name)
    return result_df[result_df['enum'] == enum_term]['source'].iloc[0]
  
def get_enum_term_id(df, enum_name: str, enum_term: str):
    result_df = pull_enum(df, enum_name)
    return result_df[result_df['enum'] == enum_term]['term_id'].iloc[0]
  

def construct_enum_def(df, enum_name: str):
    enum_term_list = get_enum_list(df, enum_name)
    enum_def_list = []
    for enum_term in enum_term_list:
        enumdef = {
          "enumeration": enum_term,
        }
        if not check_null(get_enum_definition(df, enum_name, enum_term)):
            enumdef["definition"] = get_enum_definition(df, enum_name, enum_term)
        if not check_null(get_enum_source(df, enum_name, enum_term)):
            enumdef["source"] = get_enum_source(df, enum_name, enum_term)
        if not check_null(get_enum_term_id(df, enum_name, enum_term)):
            enumdef["term_id"] = get_enum_term_id(df, enum_name, enum_term)
        enum_def_list.append(enumdef)
    return enum_def_list

def construct_enum_term_yaml_entry(df, enum_name: str, description: str = None):
    enum_term_list = get_enum_list(df, enum_name)
    enum_def_list = construct_enum_def(df, enum_name)
    output_dict = {
            "description": description,
            "enum": enum_term_list,
            "enumDef": enum_def_list,
    }
    return output_dict




definitions_dict = load_yaml("dictionary/test_dict/_definitions.yaml")
for enum_name in set(enums_to_pull_list):
    definitions_dict[enum_name] = construct_enum_term_yaml_entry(enum_df, enum_name)

write_yaml(definitions_dict, "dictionary/test_dict/_definitions.yaml")