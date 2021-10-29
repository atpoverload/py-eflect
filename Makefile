SRC=.
PROTOS_OUT=eflect
PROTOS=protos/**

clean:
	rm -r $(PROTOS)/*_pb2.py

protos:
	protoc --python_out=eflect protos/**/*.proto

smoke_test: protos
	python3 eflect -f tests/sleep_test.py
