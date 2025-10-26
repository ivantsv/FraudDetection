PROTOC = python -m grpc_tools.protoc
PROTO_DIR = .
OUT_DIR = ../generated_proto

.PHONY: all ml metadata transactions clean fix-imports

all: ml metadata transactions fix-imports

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

fix-imports:
	@if [ -f $(OUT_DIR)/ml_pb2_grpc.py ]; then \
		sed -i 's/^import ml_pb2/from generated_proto import ml_pb2/' $(OUT_DIR)/ml_pb2_grpc.py; \
	fi
	@if [ -f $(OUT_DIR)/metadata_pb2_grpc.py ]; then \
		sed -i 's/^import metadata_pb2/from generated_proto import metadata_pb2/' $(OUT_DIR)/metadata_pb2_grpc.py; \
	fi
	@if [ -f $(OUT_DIR)/transactions_pb2_grpc.py ]; then \
		sed -i 's/^import transactions_pb2/from generated_proto import transactions_pb2/' $(OUT_DIR)/transactions_pb2_grpc.py; \
	fi

clean:
	rm -rf $(OUT_DIR)/*.py