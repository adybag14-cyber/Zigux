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
- `python3 scripts/zigux/validate-phase3.py` validates every discovered slice and its preferred manifest.
- `python3 scripts/zigux/run-phase3-checks.py --list` shows the currently discovered Phase 3 parity wrappers.
- `python3 scripts/zigux/run-phase3-checks.py` executes the full discovered Phase 3 parity suite.

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
