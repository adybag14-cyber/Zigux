- packet: `phase7-leaf-library-evidence`
- phase: `Phase 7`
- lane scope: shared leaf-library evidence rows and validation foothold only

## Current direct-readback companions

- `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`
- `Documentation/zigux/README.md`
- `scripts/zigux/check-phase7-shared-surface.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase7_leaf_library_evidence_manifest.json`
- `zigux/Makefile`
- `lib/string_helpers.zig`
- `lib/string_helpers_parse_int_array.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`

## Roadmap anchors

- `lib/string_helpers.c`
- `lib/cmdline.c`
- `lib/argv_split.c`
- `lib/rbtree.c`

## Current direct helper evidence

- `lib/string_helpers.zig` keeps the returned string-unit, escape, unescape, `kasprintf`, `kstrdupQuotable()`, and `kstrdupQuotableCmdline()` support packet readable on current `master`.
- `lib/string_helpers_parse_int_array.zig` keeps the focused integer-array parsing companion explicit without pretending the broader shared Phase 7 packet is already closed.
- `lib/cmdline.zig` keeps the current option parsing, `memparse`, and integer-range handling packet readable on current `master`.
- `lib/argv_split.zig` keeps the current whitespace-tokenization helper family readable on current `master`.

## Current replay inventory

- `python3 scripts/zigux/check-phase7-shared-surface.py`
- `python3 scripts/zigux/check-phase7-shared-surface.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/validate-phase7.py --self-test`
- `make -C zigux phase7-validate`

## Current repo-reality gaps

- `lib/rbtree.zig`
- `zigux/tests/phase7_build.zig`

## Review posture

- keep the current Phase 7 packet bounded to returned leaf-library helper evidence, the shared docs-root, scripts-root, and tests-root reminder packet, the dedicated `check-phase7-build-wiring.py` guard, and one Makefile-backed validation foothold
- do not present the missing `lib/rbtree.zig` roadmap anchor or `zigux/tests/phase7_build.zig` as landed work
- do not widen this packet into new helper semantics, closure claims, or deeper runtime-family validation routes until those remaining missing anchors land