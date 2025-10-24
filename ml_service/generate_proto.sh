#!/bin/bash

echo "Generating gRPC code from proto..."

mkdir -p generated

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./proto/ml.proto

touch generated/__init__.py
touch proto/__init__.py

echo "Generated files:"
ls -lh generated/

echo "

Done!"
