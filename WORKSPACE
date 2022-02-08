workspace(name = "py-eflect")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
  name = "com_github_protocolbuffers_protobuf",
  sha256 = "cf754718b0aa945b00550ed7962ddc167167bd922b842199eeb6505e6f344852",
  strip_prefix = "protobuf-3.11.3",
  urls = [
    "https://mirror.bazel.build/github.com/protocolbuffers/protobuf/archive/v3.11.3.tar.gz",
    "https://github.com/protocolbuffers/protobuf/archive/v3.11.3.tar.gz",
  ],
)

load("eflect_deps.bzl", "eflect_deps", "eflect_proto_deps")
eflect_proto_deps()

load("@rules_proto//proto:repositories.bzl", "rules_proto_dependencies", "rules_proto_toolchains")
rules_proto_dependencies()
rules_proto_toolchains()
