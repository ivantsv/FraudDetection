PROTOC = python -m grpc_tools.protoc
PROTO_DIR = .
OUT_DIR = ../generated_proto

.PHONY: all ml metadata transactions clean

all: ml metadata transactions

ml:
	$(PROTOC) -I$(PROTO_DIR) \
		--python_out=$(OUT_DIR) \
		--grpc_python_out=$(OUT_DIR) \
		$(PROTO_DIR)/ml.proto

metadata:
	$(PROTOC) -I$(PROTO_DIR) \
		--python_out=$(OUT_DIR) \
		--grpc_python_out=$(OUT_DIR) \
		$(PROTO_DIR)/metadata.proto

transactions:
	$(PROTOC) -I$(PROTO_DIR) \
		--python_out=$(OUT_DIR) \
		--grpc_python_out=$(OUT_DIR) \
		$(PROTO_DIR)/transactions.proto

clean:
	rm -rf $(OUT_DIR)/*.py