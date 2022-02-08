load("@rules_proto//proto:defs.bzl", "proto_library")
load("@com_github_protocolbuffers_protobuf//:protobuf.bzl", "py_proto_library")

proto_library(
  name = "sample_protos",
  visibility = ["//visibility:public"],
  srcs = glob(["*.proto"]),

)

py_proto_library(
  name = "sample_py_protos",
  visibility = ["//visibility:public"],
  srcs = glob(["*.proto"]),
)
