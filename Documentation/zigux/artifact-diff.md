# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity claim.

Current Phase 1 use
- `zigux/tests/fixtures/phase1_helpers.json` is generated from the in-tree C helper implementations.
- `scripts/zigux/check-phase1-parity.py` rebuilds that artifact and compares it against the committed JSON.
- `scripts/zigux/artifact_diff.py` is the generic comparison layer that future Phase 2 tooling work will reuse.

Current Phase 2 use
- `zigux/tests/fixtures/fixdep/sample_expected.txt` is generated from the current in-tree C `scripts/basic/fixdep.c` behavior on a bounded committed sample.
- `scripts/zigux/check-fixdep-diff.py` compares the committed sample output against both the C tool and `scripts/zigux/fixdep.zig`.

Rules
- artifact fixtures must be generated from the current in-tree source of truth
- fixture scope must stay small and reviewable
- fixture updates must be intentional and committed alongside the code change that caused them
- do not use opaque binary blobs for early bootstrap parity when a text or JSON artifact is possible

Near-term target
- reuse the same artifact-diff pattern for Phase 2 dual-implementation tool outputs such as `fixdep` and `genksyms`
