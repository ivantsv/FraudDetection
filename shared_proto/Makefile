PROTOC = python -m grpc_tools.protoc
PROTO_DIR = .
OUT_DIR ?= ../ml_service/generated

.PHONY: all ml metadata clean

all: ml metadata

ml:
	$(PROTOC) -I$(PROTO_DIR) --python_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) $(PROTO_DIR)/ml.proto

metadata:
	$(PROTOC) -I$(PROTO_DIR) --python_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) $(PROTO_DIR)/metadata.proto

transactions:
	$(PROTOC) -I$(PROTO_DIR) --python_out=$(OUT_DIR) --grpc_python_out=$(OUT_DIR) $(PROTO_DIR)/transactions.proto

clean:
	rm -rf $(OUT_DIR)/*.py
