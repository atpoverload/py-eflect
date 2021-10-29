#!/bin/bash

rm -r eflect/protos
protoc --python_out=eflect protos/**/*.proto
