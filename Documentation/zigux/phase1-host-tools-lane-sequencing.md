# Phase 1 Host Tools Lane Sequencing

This note keeps the closed Phase 1 host-tools tranche reviewable without reopening the whole helper batch at once.

## Scope

Use this note when work stays inside the Host Tools Alpha Pod and touches the closed Phase 1 helper packet under `tools/lib/*.zig` plus the shared Phase 1 docs, validator, fixture, workflow, or make-route surfaces.

Roadmap boundary:
- stay on host-side helper closure and alpha scaffolds only
- do not widen into Phase 2 toolchain work, Phase 3 ABI work, or later helper families from `lib/`, `zigux/helpers/`, or driver trees

## Authority

Treat these files as the bounded Phase 1 truth packet:
- `Documentation/zigux/phase1-closure.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Follow-Up Split

Shared-replay parked helpers reopen only for packet drift across shared docs, validators, fixtures, workflow wiring, or build routes:
- `tools/lib/argv_split.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/hweight.zig`
- `tools/lib/list_sort.zig`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`

Direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys:
- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/rbtree.zig`
- `tools/lib/string.zig`

## Anti-Overlap Rule

Do not batch work across those two sets in one follow-up lane.

Use these boundaries instead:
- shared-replay parked helpers get docs, manifest, validator, workflow, or make-route follow-through only
- direct-anchor helpers get helper-local anchor, manifest-anchor, or already-shipped fixture-key follow-through only
- if a change needs both sets, split it into separate bounded steps instead of treating Phase 1 as one open-ended helper family again

## Shared Packet Discipline

When shared Phase 1 wording or validation moves, keep these surfaces aligned in the same bounded reread:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase1-closure.md`
- `scripts/zigux/README.md`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase1-installer-review-surfaces.py`
- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-parity.py`
- `scripts/zigux/check-phase1-bench.py`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `make -C zigux phase1-validate`
- `make -C zigux phase1-test`
- `make -C zigux phase1-bench`
- `make -C zigux phase1`

## Practical Rule

If the next step can be explained as "tighten one shared packet surface" or "tighten one existing direct helper anchor," it belongs here.

If it needs a new helper family, a new subsystem tree, or a cross-phase validator expansion, it does not belong in this lane.
