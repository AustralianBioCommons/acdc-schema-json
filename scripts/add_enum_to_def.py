#!/usr/bin/env python3
"""
Enum Definition Generator CLI Tool

This script reads a CSV file containing information about enums and adds them
to a specified YAML definitions file for schema reference.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from gen3schemadev.utils import load_yaml, write_yaml


# Configure logging
def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging with appropriate format and level.
    
    Args:
        verbose: If True, set logging level to DEBUG; otherwise INFO
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


logger = logging.getLogger(__name__)


def check_null(value: Any) -> bool:
    """
    Returns True if the input is considered 'null' or missing, otherwise False.
    
    Considers None, NaN, certain string representations, and empty collections as null.
    
    Args:
        value: The value to check for nullity
        
    Returns:
        bool: True if value is null, False otherwise
    """
    import math
    
    # Check for None
    if value is None:
        logger.debug(f"Value is None: {value}")
        return True
    
    # Check for NaN (float or pandas/numpy nan)
    try:
        if isinstance(value, float) and math.isnan(value):
            logger.debug(f"Value is NaN: {value}")
            return True
    except Exception as e:
        logger.debug(f"Exception checking NaN: {e}")
        pass
    
    # Check for string representations of "null"
    if isinstance(value, str):
        null_strs = {
            "", "null", "none", "nan", "n/a", "na",
            "not available", "not applicable", "missing"
        }
        if value.strip().lower() in null_strs:
            logger.debug(f"Value is null string: '{value}'")
            return True
    
    # Check for empty collections
    if isinstance(value, (list, tuple, set, dict)):
        if len(value) == 0:
            logger.debug(f"Value is empty collection: {value}")
            return True
    
    return False


def pull_enum(df: pd.DataFrame, enum_name: str) -> pd.DataFrame:
    """
    Filter dataframe for a specific enum type.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type to filter
        
    Returns:
        pd.DataFrame: Filtered dataframe containing only the specified enum
        
    Raises:
        ValueError: If enum_name not found in dataframe
    """
    result_df = df[df['type_name'] == enum_name]
    if result_df.empty:
        raise ValueError(f"Enum '{enum_name}' not found in dataframe")
    logger.debug(f"Pulled {len(result_df)} rows for enum '{enum_name}'")
    return result_df


def col_to_list(df: pd.DataFrame, colname: str) -> List[Any]:
    """
    Convert a dataframe column to a list.
    
    Args:
        df: The source dataframe
        colname: The name of the column to convert
        
    Returns:
        List: The column values as a list
        
    Raises:
        KeyError: If column not found in dataframe
    """
    if colname not in df.columns:
        raise KeyError(f"Column '{colname}' not found in dataframe")
    return df[colname].tolist()


def get_enum_list(df: pd.DataFrame, enum_name: str) -> List[str]:
    """
    Get the list of enum values for a specific enum type.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type
        
    Returns:
        List[str]: List of enum values
    """
    result_df = pull_enum(df, enum_name)
    return col_to_list(result_df, "enum")


def get_enum_definition(df: pd.DataFrame, enum_name: str, enum_term: str) -> str:
    """
    Get the definition for a specific enum term.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type
        enum_term: The specific enum term
        
    Returns:
        str: The definition of the enum term
        
    Raises:
        IndexError: If enum term not found
    """
    result_df = pull_enum(df, enum_name)
    filtered = result_df[result_df['enum'] == enum_term]
    if filtered.empty:
        raise IndexError(f"Enum term '{enum_term}' not found in enum '{enum_name}'")
    return filtered['enum_definition'].iloc[0]


def get_enum_source(df: pd.DataFrame, enum_name: str, enum_term: str) -> str:
    """
    Get the source for a specific enum term.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type
        enum_term: The specific enum term
        
    Returns:
        str: The source of the enum term
    """
    result_df = pull_enum(df, enum_name)
    filtered = result_df[result_df['enum'] == enum_term]
    if filtered.empty:
        raise IndexError(f"Enum term '{enum_term}' not found in enum '{enum_name}'")
    return filtered['source'].iloc[0]


def get_enum_term_id(df: pd.DataFrame, enum_name: str, enum_term: str) -> str:
    """
    Get the term ID for a specific enum term.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type
        enum_term: The specific enum term
        
    Returns:
        str: The term ID of the enum term
    """
    result_df = pull_enum(df, enum_name)
    filtered = result_df[result_df['enum'] == enum_term]
    if filtered.empty:
        raise IndexError(f"Enum term '{enum_term}' not found in enum '{enum_name}'")
    return filtered['term_id'].iloc[0]


def construct_enum_def(df: pd.DataFrame, enum_name: str) -> List[Dict[str, str]]:
    """
    Construct the enum definition list with all metadata.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type
        
    Returns:
        List[Dict]: List of enum definitions with metadata
    """
    enum_term_list = get_enum_list(df, enum_name)
    enum_def_list = []
    
    logger.info(f"Constructing enum definitions for '{enum_name}' with {len(enum_term_list)} terms")
    
    for enum_term in enum_term_list:
        enumdef = {
            "enumeration": enum_term,
        }
        
        try:
            definition = get_enum_definition(df, enum_name, enum_term)
            if not check_null(definition):
                enumdef["definition"] = definition
        except Exception as e:
            logger.warning(f"Could not get definition for '{enum_term}': {e}")
        
        try:
            source = get_enum_source(df, enum_name, enum_term)
            if not check_null(source):
                enumdef["source"] = source
        except Exception as e:
            logger.warning(f"Could not get source for '{enum_term}': {e}")
        
        try:
            term_id = get_enum_term_id(df, enum_name, enum_term)
            if not check_null(term_id):
                enumdef["term_id"] = term_id
        except Exception as e:
            logger.warning(f"Could not get term_id for '{enum_term}': {e}")
        
        enum_def_list.append(enumdef)
        logger.debug(f"Added enum definition for term '{enum_term}'")
    
    return enum_def_list


def construct_enum_term_yaml_entry(
    df: pd.DataFrame,
    enum_name: str,
    description: str = None
) -> Dict[str, Any]:
    """
    Construct the complete YAML entry for an enum type.
    
    Args:
        df: The source dataframe
        enum_name: The name of the enum type
        description: Optional description for the enum
        
    Returns:
        Dict: Complete YAML entry structure for the enum
    """
    enum_term_list = get_enum_list(df, enum_name)
    enum_def_list = construct_enum_def(df, enum_name)
    
    output_dict = {
        "description": description,
        "enum": enum_term_list,
        "enumDef": enum_def_list,
    }
    
    logger.debug(f"Constructed YAML entry for enum '{enum_name}'")
    return output_dict


def validate_file_exists(filepath: str, file_description: str) -> Path:
    """
    Validate that a file exists and is readable.
    
    Args:
        filepath: Path to the file
        file_description: Description of the file for error messages
        
    Returns:
        Path: Path object for the file
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file is not readable
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"{file_description} not found: {filepath}")
    
    if not path.is_file():
        raise ValueError(f"{file_description} is not a file: {filepath}")
    
    if not path.suffix:
        logger.warning(f"{file_description} has no file extension: {filepath}")
    
    logger.info(f"Validated {file_description}: {filepath}")
    return path


def validate_csv_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    """
    Validate that required columns exist in the dataframe.
    
    Args:
        df: The dataframe to validate
        required_columns: List of required column names
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"CSV missing required columns: {missing_columns}")
    logger.debug(f"CSV contains all required columns: {required_columns}")


def process_enums(enum_csv_path: str, definitions_yaml_path: str) -> None:
    """
    Main processing function to read enums from CSV and update YAML definitions.
    
    Args:
        enum_csv_path: Path to the enum CSV file
        definitions_yaml_path: Path to the definitions YAML file
        
    Raises:
        Various exceptions for file I/O and processing errors
    """
    try:
        # Validate input files
        csv_path = validate_file_exists(enum_csv_path, "Enum CSV file")
        yaml_path = validate_file_exists(definitions_yaml_path, "Definitions YAML file")
        
        # Load CSV
        logger.info(f"Loading enum CSV from: {csv_path}")
        enum_df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(enum_df)} rows from CSV")
        
        # Validate CSV structure
        required_columns = ['type_name', 'enum', 'enum_definition', 'source', 'term_id']
        validate_csv_columns(enum_df, required_columns)
        
        # Get unique enum types
        enum_to_pull_list = enum_df['type_name'].unique().tolist()
        logger.info(f"Found {len(enum_to_pull_list)} unique enum types: {enum_to_pull_list}")
        
        # Load existing definitions
        logger.info(f"Loading definitions YAML from: {yaml_path}")
        definitions_dict = load_yaml(str(yaml_path))
        logger.info(f"Loaded definitions YAML with {len(definitions_dict)} existing entries")
        
        # Process each enum type
        for enum_name in set(enum_to_pull_list):
            try:
                logger.info(f"Processing enum: {enum_name}")
                definitions_dict[enum_name] = construct_enum_term_yaml_entry(enum_df, enum_name)
                logger.info(f"Successfully processed enum: {enum_name}")
            except Exception as e:
                logger.error(f"Failed to process enum '{enum_name}': {e}", exc_info=True)
                raise
        
        # Write updated definitions
        logger.info(f"Writing updated definitions to: {yaml_path}")
        write_yaml(definitions_dict, str(yaml_path))
        logger.info(f"Successfully updated definitions file with {len(enum_to_pull_list)} enum types")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except pd.errors.EmptyDataError as e:
        logger.error(f"CSV file is empty: {e}")
        raise
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}", exc_info=True)
        raise


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate enum definitions from CSV and update YAML definitions file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --enum-csv enums.csv --definitions-yaml _definitions.yaml
  %(prog)s -e enums.csv -d _definitions.yaml --verbose
  
This tool reads enum information from a CSV file and adds it to a YAML
definitions file for schema reference.
        """
    )
    
    parser.add_argument(
        '-e', '--enum-csv',
        type=str,
        required=True,
        help='Path to the CSV file containing enum definitions (required columns: '
             'type_name, enum, enum_definition, source, term_id)'
    )
    
    parser.add_argument(
        '-d', '--definitions-yaml',
        type=str,
        required=True,
        help='Path to the YAML definitions file to update'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG level) logging output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the CLI tool.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        setup_logging(verbose=args.verbose)
        
        logger.info("Starting enum definition generator")
        logger.info(f"Enum CSV: {args.enum_csv}")
        logger.info(f"Definitions YAML: {args.definitions_yaml}")
        
        # Process enums
        process_enums(args.enum_csv, args.definitions_yaml)
        
        logger.info("Enum definition generation completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 1
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return 1
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty or cannot be read")
        return 1
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
