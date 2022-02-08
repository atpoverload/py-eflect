load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def eflect_proto_deps():
  """Loads the dependencies for eflect's proto use."""
  if not native.existing_rule("rules_java"):
    http_archive(
        name = "rules_java",
        sha256 = "ccf00372878d141f7d5568cedc4c42ad4811ba367ea3e26bc7c43445bbc52895",
        strip_prefix = "rules_java-d7bf804c8731edd232cb061cb2a9fe003a85d8ee",
        urls = [
            "https://mirror.bazel.build/github.com/bazelbuild/rules_java/archive/d7bf804c8731edd232cb061cb2a9fe003a85d8ee.tar.gz",
            "https://github.com/bazelbuild/rules_java/archive/d7bf804c8731edd232cb061cb2a9fe003a85d8ee.tar.gz",
        ],
    )
  if not native.existing_rule("rules_proto"):
    http_archive(
        name = "rules_proto",
        sha256 = "2490dca4f249b8a9a3ab07bd1ba6eca085aaf8e45a734af92aad0c42d9dc7aaf",
        strip_prefix = "rules_proto-218ffa7dfa5408492dc86c01ee637614f8695c45",
        urls = [
            "https://mirror.bazel.build/github.com/bazelbuild/rules_proto/archive/218ffa7dfa5408492dc86c01ee637614f8695c45.tar.gz",
            "https://github.com/bazelbuild/rules_proto/archive/218ffa7dfa5408492dc86c01ee637614f8695c45.tar.gz",
        ],
    )
  if not native.existing_rule("rules_python"):
    http_archive(
        name = "rules_python",
        sha256 = "09a3c4791c61b62c2cbc5b2cbea4ccc32487b38c7a2cc8f87a794d7a659cc742",
        strip_prefix = "rules_python-740825b7f74930c62f44af95c9a4c1bd428d2c53",
        url = "https://github.com/bazelbuild/rules_python/archive/740825b7f74930c62f44af95c9a4c1bd428d2c53.zip",
    )
