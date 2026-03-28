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

Active slice records
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `Documentation/zigux/phase3-list-hlist-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-xarray-slot-slice.md`
- `Documentation/zigux/phase3-idr-slot-slice.md`
- `Documentation/zigux/phase3-ida-bitmap-slice.md`
- `Documentation/zigux/phase3-ida-alloc-slice.md`
- `Documentation/zigux/phase3-ida-range-slice.md`
- `Documentation/zigux/phase3-ida-range-set-slice.md`
- `Documentation/zigux/phase3-ida-policy-slice.md`

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
