# Zigux Documentation

This directory is the product documentation root for Zigux.

Scope
- product charter
- review rules
- freeze map
- phase closure records
- phase policy
- future porting guides
- validation and artifact-diff policy

Rules
- keep product commitments here, not in ad hoc issue threads
- keep deep-core freeze decisions explicit
- require validation and rollback language for every new active port target
- align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`

Phase 3 notes
- Active Phase 3 slices are discovered from `phase3-*-slice.md` records instead of being duplicated in multiple hand-maintained inventories.
- `python3 scripts/zigux/validate-phase3.py` validates every discovered slice and its preferred manifest, accepts either the shared runner gate (`python3 scripts/zigux/run-phase3-checks.py --slug <slug>`) or a legacy per-slice wrapper gate in each slice record, reports obsolete `check-phase3-*.py` wrapper files that no longer belong to a discovered slice, and rejects legacy wrapper script paths inside Phase 3 manifests so those manifests remain a record of slice artifacts rather than compatibility entrypoints.
- `python3 scripts/zigux/phase3_catalog.py --self-test`, `python3 scripts/zigux/phase3_check_lib.py --self-test`, and `python3 scripts/zigux/run-phase3-checks.py --self-test` cover the discovery, shared-helper, and slug-selection paths without launching the full parity suite.
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-docs` lists the discovered slice records that still reference legacy per-slice wrapper commands, which makes wrapper-reference cleanup auditable instead of manual.
- `python3 scripts/zigux/phase3_catalog.py --rewrite-shared-runner-docs` rewrites those legacy record references to the shared runner command in place, which makes incremental cleanup repeatable.
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-references` lists remaining discovered Phase 3 wrapper mentions in non-slice documentation, so policy-doc cleanup stays auditable after the manifest references were removed.
- `python3 scripts/zigux/phase3_catalog.py --rewrite-legacy-wrapper-references` rewrites those non-slice documentation references to the shared runner command in place, which gives `artifact-diff.md` and related policy docs the same scripted cleanup path as the slice records.
- `python3 scripts/zigux/generate-phase3-check-wrappers.py --check` catches wrapper-template drift and obsolete wrapper files before the parity suite runs.
- `python3 scripts/zigux/run-phase3-checks.py --list` shows the currently discovered Phase 3 parity slices.
- `python3 scripts/zigux/run-phase3-checks.py` executes the full discovered Phase 3 parity suite.

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
