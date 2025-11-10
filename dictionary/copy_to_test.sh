#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "SCRIPT_DIR is: $SCRIPT_DIR"
echo "Source prod_dict path: $SCRIPT_DIR/prod_dict"
echo "Destination path: $SCRIPT_DIR/test_dict"

if [ -d "$SCRIPT_DIR/test_dict" ]; then
    read -p "Are you sure you want to overwrite the test dictionary? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        echo "Removing existing test_dict at: $SCRIPT_DIR/test_dict"
        rm -r "$SCRIPT_DIR/test_dict"
    else
        echo "Aborting."
        exit 1
    fi
fi

mkdir "$SCRIPT_DIR/test_dict"
echo "Copying $SCRIPT_DIR/prod_dict to $SCRIPT_DIR/test_dict ..."
cp -r "$SCRIPT_DIR/prod_dict/" "$SCRIPT_DIR/test_dict"

echo "Copied prod dictionary to test_dict."