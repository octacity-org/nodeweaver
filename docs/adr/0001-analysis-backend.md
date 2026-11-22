# ADR 0001: Use codebase-memory-mcp as the analysis backend

Status: Proposed
Date: 2026-11-22

## Context

NodeWeaver turns a repository into a graph of files, modules, classes and functions and the relations between them (imports, calls). The first plan was to build the extraction, import resolution and storage ourselves (tree-sitter, our own intermediate representation, Zova).

Octacity maintains codebase-memory-mcp (CBM, MIT license, a fork of DeusData/codebase-memory-mcp). It already indexes many languages, resolves calls with type information for Python, and keeps the graph in Zova. It has a command-line mode that prints JSON.

## Evaluation (CBM v2.0.1)

- It runs on Windows (amd64) and Linux from a Python subprocess. Arguments are passed as JSON on stdin.
- On `examples/sample_basic`: 45 nodes and 125 edges, 19 `CALLS` edges, the same set on Windows and Linux (one run on each).
- Counted by hand, 14 of 20 call sites inside the project are found. Missing: calls inside nested functions and lambdas, and calls on list elements. This count has not been checked by a second person.
- The release archive is 37 MB, the binary about 277 MB. The Windows binary is unsigned. `checksums.txt` is published.
- Not verified yet: network behaviour, run time, `sample_package`, `sample_broken`, ordering of the output.

## Decision

Use CBM as the analysis backend, behind a `Backend` interface and a `ProjectGraph` contract owned by NodeWeaver. The native tree-sitter parser and the file-level IR are removed from `main` and kept in the tag `native-parser-v0`. Gaps found in CBM are reported as issues in the CBM repository.

## Consequences

- No extraction, import resolution or storage to maintain on our side; more languages without extra work
- We depend on CBM releases and maintainers: pin the supported version range and keep recorded CBM outputs as test fixtures
- A large binary has to reach the user: a `setup` command that downloads a pinned release and verifies its checksum
- The privacy wording stays careful until the network behaviour is verified
- Completeness of the call graph depends on fixes in CBM

## Reversal

The `Backend` interface and the tag `native-parser-v0` make it possible to bring back a native backend.

## Rules carried over from the native IR

The `ProjectGraph` that NodeWeaver owns keeps these rules, which were decided for the native IR:

- Paths are relative to the scanned folder and use `/` on every operating system; absolute paths never appear in the output
- Line numbers are 1-based
- The output is sorted and does not contain values that change between runs or machines (timestamps, project names derived from absolute paths, internal ids)
- Files with syntax errors are reported, not dropped