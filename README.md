# NodeWeaver

> Turn any codebase into an interactive architecture map — not another wall of text.

**Status: early development (pre-alpha).** The project skeleton is in place. The features described below are planned and are not implemented yet.

NodeWeaver is a local-first tool that will scan a repository and generate an interactive knowledge graph, module summaries, and onboarding-ready documentation, so developers and researchers can understand a new or complex codebase in minutes instead of hours.

Built by the ARC team of the Octacity community.

---

## Why NodeWeaver?

Most AI coding assistants answer "explain this repo" with a long, linear block of text. That does not match how people build a mental model of a system: through structure, relationships, and data flow.

NodeWeaver is designed to:
- Parse your codebase with deterministic, rule-based **AST parsing**, not a guess from an LLM.
- Build a **knowledge graph** of modules, dependencies, and data flow.
- Render it as an **interactive visual map** you can click through.
- Run **entirely on your machine**, so no code is sent to an external server.

---

## Planned Features

- **Bird's-eye architecture map**: an interactive network graph of core modules and the dependencies between them.
- **Module and file cards**: click a file or folder to see a short summary of what it does, its inputs, and its outputs.
- **Documentation mode**: generate a slide or table walkthrough for onboarding a new developer or briefing a non-technical stakeholder.
- **Local and secure by default**: parsing, indexing, and visualization happen on your device.

---

## How It Will Work

NodeWeaver processes code through a layered, deterministic pipeline instead of feeding raw files into an LLM:

1. **Static parsing (AST)**: scan directory structure, imports, and function calls to build a structural skeleton.
2. **Semantic enrichment (local LLM)**: a small local model annotates the skeleton, answering "what does this file do?" and "where does the data flow?".
3. **Visual synthesis**: the knowledge graph is rendered as a self-contained, interactive HTML report.

```
Repository → AST Parser → Intermediate Representation → Dependency Graph → Local LLM Summaries → Visual Report
```

### Planned Stack

Python 3.12, `uv`, tree-sitter, Zova (storage), Ollama (local LLM), D3.js.

---

## Development Setup

Requirements: [uv](https://docs.astral.sh/uv/) and Git. `uv` installs the pinned Python version (3.12) for you.

```bash
git clone https://github.com/octacity-org/nodeweaver.git
cd nodeweaver
uv sync
uv run nodeweaver
```

At this stage the command only prints `Hello from nodeweaver!`. The planned scan command (`nodeweaver scan ./path`) does not exist yet.

Run the tests with:

```bash
uv run pytest
```

Sample projects used by the tests live in [`examples/`](examples/README.md).

---

## Roadmap

- [x] **Phase 0: Project skeleton** (Python package, `uv`, `tests/`, `examples/`)
- [ ] **Phase 1: Static parsing** with tree-sitter and an intermediate representation
- [ ] **Phase 2: Import resolution** and dependency graph
- [ ] **Phase 3: Storage and caching** with Zova
- [ ] **Phase 4: Milestone**, a working static graph without any LLM
- [ ] **Phase 5: Semantic layer** with a local LLM
- [ ] **Phase 6: Visual report** (`overview.html`) with clickable module cards
- [ ] **Phase 7: Tests, CI, and documentation mode**

---

## Design Principles

- **Deterministic first, LLM second**: structure comes from parsing, not inference. The LLM only enriches what is already known.
- **Local-only**: your code never leaves your machine.
- **Readable by default**: every output should be understood at a glance.

---

## Contributing

Contributions are welcome. Please read the [Octacity contributing guidelines](https://github.com/octacity-org/.github/blob/main/CONTRIBUTING.md) first. In short:

- Write issues and pull requests in English.
- Open an issue before starting work, and discuss architectural changes first.
- Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`).
- Fill in the pull request template and link the related issue.

## License

A license has not been chosen yet. Until one is added, all rights are reserved.
