SRC=.
PROTOS_OUT=eflect/proto
PROTOS=$(PROTOS_OUT)/*.proto

clean:
	rm -r $(PROTOS_OUT)/*_pb2.py

protos:
	protoc --python_out=$(SRC) $(PROTOS)

smoke_test: protos
	python3 eflect -f tests/sleep_test.py --fake
	python3 eflect -f tests/sleep_test.py
