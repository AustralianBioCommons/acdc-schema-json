#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "SCRIPT_DIR is: $SCRIPT_DIR"
echo "Source test_dict path: $SCRIPT_DIR/test_dict"
echo "Destination path: $(pwd)/prod_dict"

if [ -d "prod_dict" ]; then
    read -p "Are you sure you want to overwrite the production dictionary? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        echo "Removing existing prod_dict at: $(pwd)/prod_dict"
        rm -r prod_dict
    else
        echo "Aborting."
        exit 1
    fi
fi

mkdir prod_dict
echo "Copying $SCRIPT_DIR/test_dict to $(pwd)/prod_dict ..."
cp -r $SCRIPT_DIR/test_dict prod_dict

echo "Copied test dictionary to prod_dict."