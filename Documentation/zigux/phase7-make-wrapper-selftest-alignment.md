# Phase 7 Make-Wrapper Selftest Alignment

This note keeps the shared Phase 7 make-wrapper review route honest.

The current shared Phase 7 helper packet depends on `make -C zigux phase7-validate`
replaying both the built-in self-tests and the direct repo-root checks for the
same checker family:

- `python3 scripts/zigux/validate-phase7.py --self-test`
- `python3 scripts/zigux/validate-phase7.py`
- `python3 scripts/zigux/check-phase7-make-wrapper.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper.py`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`
- `python3 scripts/zigux/check-phase7-argv-split-packet.py`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`
- `python3 scripts/zigux/check-phase7-rbtree-parity.py`
- `python3 scripts/zigux/check-phase7-build-wiring.py --self-test`
- `python3 scripts/zigux/check-phase7-build-wiring.py`

Keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`,
`Documentation/zigux/phase7-string-helpers-slice.md`,
`Documentation/zigux/phase7-cmdline-slice.md`,
`Documentation/zigux/phase7-argv-split-slice.md`,
`Documentation/zigux/phase7-rbtree-slice.md`, `scripts/zigux/README.md`,
`samples/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and
`zigux/tests/phase7_build.zig` aligned around that same shared replay packet so
the parked `string_helpers`, `cmdline`, `argv_split`, and `rbtree` bundle does
not drift back toward per-slice ad hoc checks.
